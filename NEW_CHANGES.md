# New Changes

This document captures a detailed implementation roadmap for major improvements that are currently not fully implemented, with priority on external VST lookup and browser reliability.

## Scope

1. Implement complete browser-tree traversal and consistent response fields.
2. Add a first-class external plugin search tool.
3. Add URI/path indexing and caching for faster lookups.
4. Fix known path lookup defects and normalize category parsing.
5. Remove or fully implement dead browser command paths.
6. Expand plugin alias support beyond Serum.
7. Add robust browser/plugin test coverage.

## 1) Full Browser Tree Traversal

### Problem

- Browser tree output is shallow and does not recurse into child nodes.
- MCP-side formatting expects fields not consistently returned (`path`, `has_more`, totals).

### Implementation Goals

- Return recursive node trees with stable structure.
- Include metadata needed for both human-readable and JSON output modes.

### Proposed Node Contract

Each node should contain:

- `name: str`
- `path: str`
- `uri: str | None`
- `is_folder: bool`
- `is_loadable: bool`
- `is_device: bool`
- `has_more: bool` (children truncated due to depth limit)
- `children: list[Node]`

Top-level response should include:

- `type`
- `categories`
- `available_categories`
- `total_nodes`
- `total_folders`
- `total_loadable`
- `max_depth_used`

### Remote Script Tasks (`AbletonMCP_Remote_Script/__init__.py`)

1. Add helper `_serialize_browser_item(item, path, depth, max_depth)`.
2. Add helper `_normalize_browser_category(name)` for canonical roots.
3. Recursively traverse children up to `max_depth`.
4. Set `has_more=True` where children exist but traversal stops.
5. Gracefully handle missing attributes with `hasattr` guards.

### MCP Server Tasks (`MCP_Server/server.py`)

1. Align text formatter with actual response keys.
2. Add optional `output_format` parameter to `get_browser_tree`:
   - `tree` (default)
   - `json`
3. Show totals in text mode.
4. Preserve raw JSON mode for tool-to-tool callers.

### Acceptance Criteria

- Tree includes nested children for at least three levels when present.
- No crashes when categories differ by Ableton version/OS.
- Output remains deterministic between repeated calls.

## 2) Add `search_external_plugins` Tool

### Problem

- Current plugin loading is URI/path-based.
- There is no natural lookup flow for external VST/AU plugin names.

### New Tool API (MCP)

Tool name: `search_external_plugins`

Parameters:

- `query: str`
- `plugin_format: str = "all"` (`all|vst2|vst3|au`)
- `vendor: str = ""`
- `max_results: int = 20`
- `fuzzy: bool = True`
- `refresh_cache: bool = False`

Response fields per result:

- `name`
- `uri`
- `path`
- `format`
- `vendor`
- `score`
- `is_loadable`

### Ranking Strategy

Score by descending priority:

1. Exact normalized name match.
2. Prefix name match.
3. Token overlap score.
4. Substring fallback.
5. Vendor filter boost.

### Remote Script Tasks

1. Add command handler for plugin search.
2. Discover plugin roots from browser attributes (`plugins` and equivalents).
3. Traverse plugin nodes into candidate records.
4. Apply ranking and return top `max_results`.

### MCP Server Tasks

1. Add tool wrapper and clean result formatting.
2. Provide optional JSON output mode.
3. Return ambiguity guidance when many close matches appear.

### Optional Convenience Tool

Add `load_plugin_by_search(track_index, query, ...)`:

1. Search.
2. Resolve best/unique match.
3. Load via URI.

### Acceptance Criteria

- Common plugin name queries return valid URI candidates.
- Ambiguous names produce ranked options instead of silent first-choice loading.
- Warm-cache search is fast enough for interactive workflows.

## 3) URI/Path Index and Cache

### Problem

- URI lookup recursively scans browser hierarchy repeatedly.
- Performance and lookup reliability degrade for deep structures.

### Index Design

Maintain cache in Remote Script:

- `by_uri: dict[str, NodeRef]`
- `by_path: dict[str, NodeRef]`
- `plugin_candidates: list[PluginSummary]`
- `built_at: float`
- `generation: int`

### Cache Lifecycle

1. Lazy-build on first lookup/search.
2. Rebuild on:
   - explicit `refresh_cache=True`
   - lookup misses in expected regions
   - optional TTL expiration
3. Backfill after fallback recursive lookup.

### Thread Safety

- Wrap cache mutation with lock/guard around build and refresh.
- Keep read path lock-light (copy references where needed).

### Acceptance Criteria

- Repeated URI lookups are near constant-time after first build.
- Refresh path is explicit and logged.

## 4) Fix Path Bug and Normalize Category Semantics

### Known Defect

- Root category typo for instruments path handling (`"nstruments"`).

### Implementation

1. Fix typo.
2. Centralize category normalization:
   - lowercase
   - trim whitespace
   - map aliases (example: `audio-effects` -> `audio_effects`)
3. Apply same normalization to all browser handlers:
   - `get_browser_item`
   - `get_browser_items_at_path`
   - new plugin search

### Acceptance Criteria

- `instruments/...` paths resolve correctly.
- Case and separator differences do not break category selection.

## 5) Dead Browser Commands: Remove or Implement

### Problem

- Router includes legacy command branches that are not consistently implemented.
- This increases maintenance risk and unclear behavior.

### Recommended Plan

1. Implement compatibility wrappers for legacy commands against canonical tree/path APIs.
2. Mark legacy responses with deprecation metadata:
   - `deprecated: true`
   - `replacement: "..."`
3. Document removal timeline (next major release).

### Alternative

- Remove dead command branches immediately and update docs/tooling in one change.

### Acceptance Criteria

- No unsupported command references remain in router paths.
- Documented behavior matches actual runtime behavior.

## 6) Expand Plugin Alias Profiles

### Problem

- Friendly alias/category mapping currently only targets a single plugin profile.

### Data Model Upgrade

Keep current behavior but scale the registry:

- Option A: multiple Python modules per plugin profile.
- Option B: external JSON/YAML profiles loaded at startup.

Profile shape:

- `match_names: list[str]`
- `aliases: dict[str, str]`
- `categories: dict[str, list[str]]`
- optional `vendor`
- optional `regex_patterns`

### Initial Plugin Coverage (Suggested)

- Diva
- Massive X
- Pigments
- Kontakt
- Vital

### Safety/Quality Checks

1. Duplicate alias detector at load time.
2. Category prefix overlap warnings.
3. Case-insensitive matching across aliases and device names.

### Acceptance Criteria

- Alias resolution in `set_device_parameter` works for multiple plugin families.
- Category summaries in `get_device_parameters` are useful beyond Serum.

## 7) Browser/Plugin Test Coverage

### Current Gap

- Existing tests focus on index conversion, arrangement, and core device workflows.
- Browser/plugin lookup logic has minimal direct coverage.

### Test Plan

1. Add command-construction tests:
   - `get_browser_tree`
   - `get_browser_items_at_path`
   - `search_external_plugins`
2. Add ranking tests:
   - exact > prefix > fuzzy > substring
   - vendor filter behavior
   - `max_results` truncation
3. Add cache tests:
   - cache build
   - cache hit
   - refresh invalidation
4. Add legacy compatibility/deprecation tests.

### Suggested New Test Files

- `tests/unit/test_browser_tools.py`
- `tests/unit/test_plugin_search.py`
- `tests/unit/test_browser_cache.py`

### Acceptance Criteria

- New browser/plugin tests run in CI.
- Regressions in parsing/ranking/cache behavior are caught automatically.

## Recommended Delivery Sequence

1. Path bug fix + category normalization.
2. Full browser tree traversal contract.
3. Cache/index layer.
4. `search_external_plugins` tool.
5. Alias profile expansion.
6. Legacy command compatibility/deprecation.
7. Complete browser/plugin test suite and docs updates.

## Definition of Done

- Users can search and load external plugins by natural query.
- Browser API responses are complete, recursive, and consistent.
- URI/path lookup performance is improved through caching.
- Legacy command behavior is explicit and documented.
- Multi-plugin alias support is implemented and tested.
- CI includes browser/plugin-focused unit coverage.
