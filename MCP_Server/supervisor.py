"""Crash-resilient stdio supervisor for the AbletonMCP server.

Claude Desktop launches a local MCP server once and never restarts it.  If the
process dies -- and the python worker has repeatedly been killed by a signal
hours after a clean start, with nothing on stderr -- the tools silently vanish
and the app reports "Server disconnected" until it is relaunched.

This module sits between the host and the real server:

    host  <-stdio->  supervisor (server.py)  <-stdio->  worker (server.py --worker)

The supervisor owns the host-facing stdin/stdout and forwards newline-delimited
JSON-RPC in both directions.  If the worker exits while the host's stdin is
still open, the supervisor:

  1. logs the worker's exit status (a negative code is the signal number) to
     logs/ableton-mcp.log so the cause is on record,
  2. answers every in-flight request with a JSON-RPC error instead of leaving
     the host hanging,
  3. respawns the worker and replays the MCP ``initialize`` handshake the host
     already performed, swallowing the duplicate response,
  4. resumes forwarding.  The host never notices.

Both processes also log SIGTERM/SIGHUP to the same file before dying, so the
next unexplained death has a paper trail.

Set ``ABLETON_MCP_NO_SUPERVISOR=1`` to run the server in-process as before, and
``ABLETON_MCP_LOG=/path/to/file.log`` to move the log file.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

LOG_ENV = "ABLETON_MCP_LOG"
NO_SUPERVISOR_ENV = "ABLETON_MCP_NO_SUPERVISOR"

# Give up (and let the host see a real disconnect) if the worker keeps dying
# immediately -- that is a broken install, not a stray kill.
RAPID_EXIT_WINDOW_SECONDS = 60.0
RAPID_EXIT_LIMIT = 3
RESPAWN_DELAY_SECONDS = 0.5
HANDSHAKE_TIMEOUT_SECONDS = 30.0
SHUTDOWN_GRACE_SECONDS = 5.0


# ── logging ─────────────────────────────────────────────────────────


def default_log_path() -> str:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(repo_root, "logs", "ableton-mcp.log")


def setup_file_logging(name: str) -> logging.Logger:
    """Attach a small rotating file handler to ``name`` and return the logger.

    The handler is added to the named logger, so records still propagate to the
    root logger (i.e. stderr, which the host captures) as well.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    path = os.environ.get(LOG_ENV) or default_log_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=2)
        handler.setFormatter(
            logging.Formatter("%(asctime)s pid=%(process)d %(name)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    except OSError as e:  # unwritable location: fall back to stderr only
        logger.warning("file logging disabled (%s): %s", path, e)
    return logger


def install_signal_logging(logger: logging.Logger, signals=(signal.SIGTERM, signal.SIGHUP),
                           before_exit=None) -> None:
    """Log which signal killed us (and who our parent is) before dying."""

    def handler(signum, _frame):
        try:
            name = signal.Signals(signum).name
        except ValueError:
            name = str(signum)
        logger.warning("received %s (ppid=%s) -- exiting", name, os.getppid())
        for h in logger.handlers:
            try:
                h.flush()
            except Exception:
                pass
        if before_exit is not None:
            try:
                before_exit(signum)
            except Exception:
                pass
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    for sig in signals:
        try:
            signal.signal(sig, handler)
        except (ValueError, OSError):
            pass


# ── supervisor ──────────────────────────────────────────────────────


def _parse(line: bytes) -> Optional[Dict[str, Any]]:
    try:
        msg = json.loads(line)
    except (ValueError, UnicodeDecodeError):
        return None
    return msg if isinstance(msg, dict) else None


def _is_response(msg: Dict[str, Any]) -> bool:
    return "id" in msg and ("result" in msg or "error" in msg)


def _is_request(msg: Dict[str, Any]) -> bool:
    return "id" in msg and "method" in msg


class Supervisor:
    def __init__(self, worker_cmd: List[str], logger: logging.Logger, cwd: Optional[str] = None):
        self.cmd = worker_cmd
        self.cwd = cwd
        self.log = logger

        self.host_in = sys.stdin.buffer
        self.host_out = sys.stdout.buffer
        self.out_lock = threading.Lock()

        self.state = threading.Condition()  # guards everything below
        self.proc: Optional[subprocess.Popen] = None
        self.generation = 0
        self.replaying = False
        self.stopping = False
        self.pending: Dict[Any, bool] = {}  # request ids forwarded to the live worker, unanswered
        self.exit_times: List[float] = []

        self.init_request: Optional[bytes] = None
        self.init_id: Any = None
        self.initialized_notice: Optional[bytes] = None
        self.handshake_done = threading.Event()

    # ── host side ──

    def write_host(self, line: bytes) -> None:
        if not line.endswith(b"\n"):
            line += b"\n"
        with self.out_lock:
            try:
                self.host_out.write(line)
                self.host_out.flush()
            except (BrokenPipeError, ValueError, OSError):
                # Host went away; the stdin reader will hit EOF and shut us down.
                pass

    def fail_request(self, req_id: Any, message: str) -> None:
        self.write_host(json.dumps({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32000, "message": message},
        }).encode("utf-8"))

    # ── worker side ──

    def spawn(self) -> subprocess.Popen:
        proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,  # inherit: the host logs our stderr
            cwd=self.cwd,
            bufsize=-1,
        )
        self.generation += 1
        gen = self.generation
        self.log.info("worker started pid=%s gen=%s cmd=%s", proc.pid, gen, " ".join(self.cmd))
        threading.Thread(target=self.pump_worker_stdout, args=(proc, gen),
                         name=f"worker-stdout-{gen}", daemon=True).start()
        threading.Thread(target=self.watch_worker, args=(proc, gen),
                         name=f"worker-wait-{gen}", daemon=True).start()
        return proc

    def send_to_worker(self, line: bytes, msg: Optional[Dict[str, Any]]) -> None:
        with self.state:
            while self.replaying and not self.stopping:
                self.state.wait(timeout=1.0)
            proc = self.proc
            is_req = msg is not None and _is_request(msg)
            if proc is None or proc.poll() is not None:
                if is_req:
                    self.fail_request(msg["id"], "ableton-mcp worker is not running")
                return
            if is_req:
                self.pending[msg["id"]] = True
            try:
                proc.stdin.write(line)
                proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError) as e:
                self.log.warning("write to worker pid=%s failed: %s", proc.pid, e)
                if is_req:
                    self.pending.pop(msg["id"], None)
                    self.fail_request(msg["id"], "ableton-mcp worker died; request not delivered")

    def pump_worker_stdout(self, proc: subprocess.Popen, gen: int) -> None:
        for line in iter(proc.stdout.readline, b""):
            msg = _parse(line)
            if msg is not None and _is_response(msg):
                with self.state:
                    if self.replaying and gen == self.generation and msg.get("id") == self.init_id:
                        # Duplicate answer to the replayed initialize -- the host
                        # already has the original one.
                        self.handshake_done.set()
                        continue
                    self.pending.pop(msg.get("id"), None)
            self.write_host(line)

    def watch_worker(self, proc: subprocess.Popen, gen: int) -> None:
        rc = proc.wait()
        with self.state:
            if gen != self.generation:
                return  # stale; a newer worker is already running
            if self.stopping:
                self.log.info("worker pid=%s exited rc=%s during shutdown", proc.pid, rc)
                return
            if rc < 0:
                try:
                    why = f"killed by {signal.Signals(-rc).name}"
                except ValueError:
                    why = f"killed by signal {-rc}"
            else:
                why = f"exit code {rc}"
            self.log.error("worker pid=%s gen=%s died unexpectedly (%s)", proc.pid, gen, why)

            now = time.monotonic()
            self.exit_times = [t for t in self.exit_times if now - t < RAPID_EXIT_WINDOW_SECONDS] + [now]
            if len(self.exit_times) >= RAPID_EXIT_LIMIT:
                self.log.error("worker died %d times in %.0fs -- giving up so the host sees the failure",
                               len(self.exit_times), RAPID_EXIT_WINDOW_SECONDS)
                self.stopping = True
                self.state.notify_all()
                self._fail_all_pending("ableton-mcp worker keeps crashing; see logs/ableton-mcp.log")
                for h in self.log.handlers:
                    try:
                        h.flush()
                    except Exception:
                        pass
                os._exit(1)

            self._fail_all_pending(f"ableton-mcp worker restarted ({why}); please retry")
            self.replaying = True
            self.handshake_done.clear()
            self.proc = None

        time.sleep(RESPAWN_DELAY_SECONDS)
        self._respawn_and_replay()

    def _fail_all_pending(self, message: str) -> None:
        # caller holds self.state
        for req_id in list(self.pending):
            self.fail_request(req_id, message)
        self.pending.clear()

    def _respawn_and_replay(self) -> None:
        with self.state:
            if self.stopping:
                self.replaying = False
                self.state.notify_all()
                return
            try:
                proc = self.spawn()
            except OSError as e:
                self.log.error("respawn failed: %s", e)
                self.stopping = True
                self.replaying = False
                self.state.notify_all()
                os._exit(1)
            self.proc = proc
            init_request, initialized_notice = self.init_request, self.initialized_notice

        if init_request is None:
            # Host never initialised the old worker; nothing to replay.
            with self.state:
                self.replaying = False
                self.state.notify_all()
            return

        ok = False
        try:
            proc.stdin.write(init_request)
            proc.stdin.flush()
            ok = self.handshake_done.wait(HANDSHAKE_TIMEOUT_SECONDS)
            if ok and initialized_notice is not None:
                proc.stdin.write(initialized_notice)
                proc.stdin.flush()
        except (BrokenPipeError, ValueError, OSError) as e:
            self.log.error("handshake replay failed: %s", e)
        if ok:
            self.log.info("worker pid=%s re-initialised; resuming", proc.pid)
        else:
            self.log.error("worker pid=%s did not answer the replayed initialize within %.0fs",
                           proc.pid, HANDSHAKE_TIMEOUT_SECONDS)
        with self.state:
            self.replaying = False
            self.state.notify_all()

    # ── lifecycle ──

    def shutdown_worker(self, reason: str) -> None:
        with self.state:
            self.stopping = True
            self.state.notify_all()
            proc = self.proc
        if proc is None or proc.poll() is not None:
            return
        self.log.info("shutting down worker pid=%s (%s)", proc.pid, reason)
        try:
            proc.stdin.close()  # EOF: the MCP stdio server exits cleanly on this
        except Exception:
            pass
        try:
            proc.wait(timeout=SHUTDOWN_GRACE_SECONDS)
            return
        except subprocess.TimeoutExpired:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=2.0)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def run(self) -> int:
        install_signal_logging(self.log, signals=(signal.SIGTERM, signal.SIGHUP, signal.SIGINT),
                               before_exit=lambda s: self.shutdown_worker(f"signal {s}"))
        self.log.info("supervisor started (ppid=%s)", os.getppid())
        with self.state:
            self.proc = self.spawn()

        try:
            for line in iter(self.host_in.readline, b""):
                if not line.strip():
                    continue
                msg = _parse(line)
                if msg is not None:
                    method = msg.get("method")
                    if method == "initialize" and "id" in msg:
                        self.init_request, self.init_id = line, msg["id"]
                    elif method == "notifications/initialized":
                        self.initialized_notice = line
                self.send_to_worker(line, msg)
        except (OSError, ValueError) as e:
            self.log.warning("host stdin error: %s", e)

        self.shutdown_worker("host closed stdin")
        self.log.info("supervisor exiting")
        return 0


def run_supervisor(worker_cmd: List[str], cwd: Optional[str] = None) -> int:
    logger = setup_file_logging("AbletonMCPSupervisor")
    return Supervisor(worker_cmd, logger, cwd=cwd).run()
