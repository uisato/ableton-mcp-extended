"""
Performance Optimization System - Real-Time Music Generation

This system optimizes performance for real-time music generation and responsiveness
during the music creation workflow. It provides caching, parallel processing,
and intelligent resource management to ensure smooth user experience.

Key features:
- Intelligent caching of AI-generated content
- Parallel processing of generation tasks
- Memory management and cleanup
- Real-time performance monitoring
- Adaptive quality vs speed trade-offs
- Background pre-generation
- Resource usage optimization
- Latency minimization

This ensures the system is responsive and can generate music in real-time
without blocking the user interface or Ableton Live workflow.
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import pickle
import psutil
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    REAL_TIME = "real_time"       # < 100ms response
    INTERACTIVE = "interactive"   # < 500ms response
    BACKGROUND = "background"     # < 2s response
    BATCH = "batch"              # No time constraint

class CacheType(Enum):
    CHORD_PROGRESSIONS = "chord_progressions"
    MELODIC_PHRASES = "melodic_phrases"
    RHYTHMIC_PATTERNS = "rhythmic_patterns"
    ARRANGEMENT_SECTIONS = "arrangement_sections"
    TRANSITION_EFFECTS = "transition_effects"
    QUALITY_ASSESSMENTS = "quality_assessments"
    STYLE_TEMPLATES = "style_templates"

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    operation_type: str
    start_time: float
    end_time: float
    duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit: bool
    quality_score: float
    success: bool

@dataclass
class CacheEntry:
    """Cached content entry"""
    key: str
    content: Any
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    size_bytes: int = 0

@dataclass
class GenerationTask:
    """Generation task for parallel processing"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    priority: int  # 1-10, 10 being highest
    created_at: datetime = field(default_factory=datetime.now)
    performance_level: PerformanceLevel = PerformanceLevel.INTERACTIVE
    callback: Optional[Callable] = None

class PerformanceOptimizer:
    """Main performance optimization system"""
    
    def __init__(self, cache_size_mb: int = 500, max_concurrent_tasks: int = 4):
        self.cache_size_mb = cache_size_mb
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Performance tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_memory_usage = 0
        self.cache_hit_rate = 0.0
        
        # Caching system
        self.content_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {cache_type: {"hits": 0, "misses": 0} for cache_type in CacheType}
        
        # Task management
        self.task_queue: List[GenerationTask] = []
        self.active_tasks: Dict[str, GenerationTask] = {}
        self.task_results: Dict[str, Any] = {}
        
        # Background processing
        self.background_executor = None
        self.is_running = True
        
        # Resource monitoring
        self.system_monitor = SystemResourceMonitor()
        
        # Start background processing
        self._start_background_processing()
        
    def _start_background_processing(self):
        """Start background task processing"""
        def background_worker():
            while self.is_running:
                self._process_task_queue()
                time.sleep(0.1)  # Check every 100ms
                
        self.background_thread = threading.Thread(target=background_worker, daemon=True)
        self.background_thread.start()
        
    async def generate_with_optimization(self, 
                                       generation_type: str, 
                                       input_data: Dict[str, Any],
                                       performance_level: PerformanceLevel = PerformanceLevel.INTERACTIVE,
                                       use_cache: bool = True) -> Dict[str, Any]:
        """Generate content with performance optimization"""
        
        start_time = time.time()
        operation_id = f"{generation_type}_{int(start_time * 1000)}"
        
        logger.debug(f"Starting optimized generation: {generation_type} ({performance_level.value})")
        
        try:
            # Check cache first
            cache_result = None
            if use_cache:
                cache_result = self._check_cache(generation_type, input_data)
                
            if cache_result:
                logger.debug(f"Cache hit for {generation_type}")
                result = cache_result
                cache_hit = True
            else:
                logger.debug(f"Cache miss for {generation_type}")
                # Generate content based on performance level
                result = await self._generate_content_optimized(generation_type, input_data, performance_level)
                cache_hit = False
                
                # Cache the result
                if use_cache:
                    self._cache_content(generation_type, input_data, result)
                    
            # Record performance metrics
            end_time = time.time()
            metrics = self._create_performance_metrics(
                operation_type=generation_type,
                start_time=start_time,
                end_time=end_time,
                cache_hit=cache_hit,
                success=True
            )
            self.metrics_history.append(metrics)
            
            # Clean up if needed
            await self._cleanup_if_needed()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in optimized generation: {e}")
            
            # Record failed metrics
            end_time = time.time()
            metrics = self._create_performance_metrics(
                operation_type=generation_type,
                start_time=start_time,
                end_time=end_time,
                cache_hit=False,
                success=False
            )
            self.metrics_history.append(metrics)
            
            raise
            
    def _check_cache(self, generation_type: str, input_data: Dict[str, Any]) -> Optional[Any]:
        """Check if content exists in cache"""
        
        cache_key = self._generate_cache_key(generation_type, input_data)
        
        if cache_key in self.content_cache:
            entry = self.content_cache[cache_key]
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            # Update cache statistics
            cache_type = self._get_cache_type(generation_type)
            self.cache_stats[cache_type]["hits"] += 1
            
            return entry.content
            
        # Cache miss
        cache_type = self._get_cache_type(generation_type)
        self.cache_stats[cache_type]["misses"] += 1
        
        return None
        
    def _cache_content(self, generation_type: str, input_data: Dict[str, Any], content: Any):
        """Cache generated content"""
        
        cache_key = self._generate_cache_key(generation_type, input_data)
        
        # Calculate content size
        content_size = len(pickle.dumps(content))
        
        # Check if we have space
        if self._get_cache_size_mb() + (content_size / 1024 / 1024) > self.cache_size_mb:
            self._evict_cache_entries()
            
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            content=content,
            timestamp=datetime.now(),
            quality_score=content.get("quality_score", 0.0) if isinstance(content, dict) else 0.0,
            size_bytes=content_size
        )
        
        self.content_cache[cache_key] = entry
        logger.debug(f"Cached content for key: {cache_key[:16]}...")
        
    def _generate_cache_key(self, generation_type: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key from input data"""
        
        # Create deterministic hash from input data
        input_string = json.dumps(input_data, sort_keys=True)
        hash_object = hashlib.md5(input_string.encode())
        
        return f"{generation_type}_{hash_object.hexdigest()}"
        
    def _get_cache_type(self, generation_type: str) -> CacheType:
        """Map generation type to cache type"""
        
        type_mapping = {
            "chord_progression": CacheType.CHORD_PROGRESSIONS,
            "melody": CacheType.MELODIC_PHRASES,
            "rhythm": CacheType.RHYTHMIC_PATTERNS,
            "arrangement": CacheType.ARRANGEMENT_SECTIONS,
            "transition": CacheType.TRANSITION_EFFECTS,
            "quality_check": CacheType.QUALITY_ASSESSMENTS
        }
        
        return type_mapping.get(generation_type, CacheType.MELODIC_PHRASES)
        
    def _get_cache_size_mb(self) -> float:
        """Get current cache size in MB"""
        
        total_bytes = sum(entry.size_bytes for entry in self.content_cache.values())
        return total_bytes / 1024 / 1024
        
    def _evict_cache_entries(self):
        """Evict least recently used cache entries"""
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.content_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest 25% of entries
        entries_to_remove = len(sorted_entries) // 4
        
        for i in range(entries_to_remove):
            key, entry = sorted_entries[i]
            del self.content_cache[key]
            logger.debug(f"Evicted cache entry: {key[:16]}...")
            
    async def _generate_content_optimized(self, 
                                        generation_type: str, 
                                        input_data: Dict[str, Any],
                                        performance_level: PerformanceLevel) -> Dict[str, Any]:
        """Generate content with performance-based optimization"""
        
        if performance_level == PerformanceLevel.REAL_TIME:
            # Real-time: Use fastest, simplest generation
            return await self._generate_real_time(generation_type, input_data)
        elif performance_level == PerformanceLevel.INTERACTIVE:
            # Interactive: Balance quality and speed
            return await self._generate_interactive(generation_type, input_data)
        elif performance_level == PerformanceLevel.BACKGROUND:
            # Background: Higher quality, more time
            return await self._generate_background(generation_type, input_data)
        else:  # BATCH
            # Batch: Highest quality, no time constraint
            return await self._generate_batch(generation_type, input_data)
            
    async def _generate_real_time(self, generation_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time generation with minimal latency"""
        
        # Use simplified algorithms for speed
        if generation_type == "chord_progression":
            return self._generate_simple_chord_progression(input_data)
        elif generation_type == "melody":
            return self._generate_simple_melody(input_data)
        elif generation_type == "rhythm":
            return self._generate_simple_rhythm(input_data)
        else:
            return {"content": f"Simple {generation_type}", "quality_score": 0.6}
            
    async def _generate_interactive(self, generation_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Interactive generation with balanced quality/speed"""
        
        # Use medium-complexity algorithms
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "content": f"Interactive {generation_type}",
            "quality_score": 0.75,
            "generation_time_ms": 100
        }
        
    async def _generate_background(self, generation_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Background generation with higher quality"""
        
        # Use more sophisticated algorithms
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "content": f"Background {generation_type}",
            "quality_score": 0.85,
            "generation_time_ms": 500
        }
        
    async def _generate_batch(self, generation_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch generation with highest quality"""
        
        # Use most sophisticated algorithms
        await asyncio.sleep(1.0)  # Simulate processing time
        
        return {
            "content": f"Batch {generation_type}",
            "quality_score": 0.95,
            "generation_time_ms": 1000
        }
        
    def _generate_simple_chord_progression(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple chord progression for real-time use"""
        
        key = input_data.get("key", "C")
        length = input_data.get("length", 4)
        
        # Simple I-V-vi-IV progression
        if key.endswith("m"):
            # Minor key
            root = key[:-1]
            chords = [f"{root}m", f"{root}m", f"{root}m", f"{root}m"]
        else:
            # Major key
            chords = [key, "G", "Am", "F"]
            
        return {
            "chord_progression": chords[:length],
            "quality_score": 0.6,
            "generation_time_ms": 10
        }
        
    def _generate_simple_melody(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple melody for real-time use"""
        
        # Generate basic scale-based melody
        notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
        melody_length = input_data.get("length", 8)
        
        melody = notes[:melody_length]
        
        return {
            "melody": [{"pitch": note, "duration": 0.5} for note in melody],
            "quality_score": 0.6,
            "generation_time_ms": 5
        }
        
    def _generate_simple_rhythm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple rhythm for real-time use"""
        
        # Basic four-on-the-floor pattern
        pattern = {
            "kick": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            "snare": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            "hihat": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        }
        
        return {
            "rhythm_pattern": pattern,
            "quality_score": 0.7,
            "generation_time_ms": 15
        }
        
    def _create_performance_metrics(self, 
                                  operation_type: str,
                                  start_time: float,
                                  end_time: float,
                                  cache_hit: bool,
                                  success: bool) -> PerformanceMetrics:
        """Create performance metrics entry"""
        
        duration_ms = (end_time - start_time) * 1000
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        return PerformanceMetrics(
            operation_type=operation_type,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            cache_hit=cache_hit,
            quality_score=0.8,  # Placeholder
            success=success
        )
        
    async def _cleanup_if_needed(self):
        """Clean up resources if needed"""
        
        # Clean up old metrics (keep last 1000)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
            
        # Clean up old task results
        current_time = datetime.now()
        old_results = [
            task_id for task_id, result in self.task_results.items()
            if isinstance(result, dict) and 
            "timestamp" in result and
            (current_time - result["timestamp"]).total_seconds() > 3600  # 1 hour
        ]
        
        for task_id in old_results:
            del self.task_results[task_id]
            
    def _process_task_queue(self):
        """Process background task queue"""
        
        if not self.task_queue or len(self.active_tasks) >= self.max_concurrent_tasks:
            return
            
        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        # Process highest priority task
        task = self.task_queue.pop(0)
        self.active_tasks[task.task_id] = task
        
        # Start task processing
        asyncio.create_task(self._execute_background_task(task))
        
    async def _execute_background_task(self, task: GenerationTask):
        """Execute a background task"""
        
        try:
            logger.debug(f"Executing background task: {task.task_id}")
            
            # Generate content
            result = await self._generate_content_optimized(
                task.task_type,
                task.input_data,
                task.performance_level
            )
            
            # Store result
            self.task_results[task.task_id] = {
                "result": result,
                "timestamp": datetime.now(),
                "success": True
            }
            
            # Call callback if provided
            if task.callback:
                task.callback(task.task_id, result)
                
        except Exception as e:
            logger.error(f"Background task failed: {task.task_id} - {e}")
            
            self.task_results[task.task_id] = {
                "error": str(e),
                "timestamp": datetime.now(),
                "success": False
            }
            
        finally:
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
                
    def queue_background_task(self, 
                            task_type: str,
                            input_data: Dict[str, Any],
                            priority: int = 5,
                            callback: Optional[Callable] = None) -> str:
        """Queue a task for background processing"""
        
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        
        task = GenerationTask(
            task_id=task_id,
            task_type=task_type,
            input_data=input_data,
            priority=priority,
            performance_level=PerformanceLevel.BACKGROUND,
            callback=callback
        )
        
        self.task_queue.append(task)
        
        logger.debug(f"Queued background task: {task_id}")
        return task_id
        
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a background task"""
        
        return self.task_results.get(task_id)
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and statistics"""
        
        if not self.metrics_history:
            return {"status": "no_data"}
            
        recent_metrics = self.metrics_history[-100:]  # Last 100 operations
        
        # Calculate averages
        avg_duration = sum(m.duration_ms for m in recent_metrics) / len(recent_metrics)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        cache_hit_rate = cache_hits / len(recent_metrics)
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        
        # Calculate cache statistics
        cache_stats_summary = {}
        for cache_type, stats in self.cache_stats.items():
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                hit_rate = stats["hits"] / total_requests
            else:
                hit_rate = 0.0
            cache_stats_summary[cache_type.value] = {
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }
            
        return {
            "performance": {
                "avg_response_time_ms": round(avg_duration, 2),
                "cache_hit_rate": round(cache_hit_rate, 3),
                "success_rate": round(success_rate, 3),
                "total_operations": len(self.metrics_history),
                "active_tasks": len(self.active_tasks),
                "queued_tasks": len(self.task_queue)
            },
            "cache": {
                "total_entries": len(self.content_cache),
                "cache_size_mb": round(self._get_cache_size_mb(), 2),
                "cache_limit_mb": self.cache_size_mb,
                "cache_utilization": round(self._get_cache_size_mb() / self.cache_size_mb, 3),
                "cache_stats": cache_stats_summary
            },
            "system": {
                "memory_usage_percent": psutil.virtual_memory().percent,
                "cpu_usage_percent": psutil.cpu_percent(),
                "available_memory_gb": round(psutil.virtual_memory().available / 1024**3, 2)
            }
        }
        
    def optimize_for_real_time(self):
        """Optimize system for real-time performance"""
        
        # Reduce cache size for faster access
        self.cache_size_mb = min(self.cache_size_mb, 100)
        
        # Increase concurrent task limit
        self.max_concurrent_tasks = min(self.max_concurrent_tasks * 2, 8)
        
        # Pre-generate common patterns
        self._pre_generate_common_patterns()
        
        logger.info("Optimized system for real-time performance")
        
    def _pre_generate_common_patterns(self):
        """Pre-generate common musical patterns for cache"""
        
        # Common chord progressions
        common_progressions = [
            {"key": "C", "length": 4},
            {"key": "Am", "length": 4},
            {"key": "G", "length": 4},
            {"key": "Em", "length": 4}
        ]
        
        for progression_data in common_progressions:
            result = self._generate_simple_chord_progression(progression_data)
            self._cache_content("chord_progression", progression_data, result)
            
        logger.debug("Pre-generated common patterns")
        
    def shutdown(self):
        """Shutdown the performance optimizer"""
        
        self.is_running = False
        
        if hasattr(self, 'background_thread'):
            self.background_thread.join(timeout=5.0)
            
        logger.info("Performance optimizer shut down")

class SystemResourceMonitor:
    """Monitor system resources for optimization decisions"""
    
    def __init__(self):
        self.last_check = time.time()
        self.resource_history = []
        
    def get_current_resources(self) -> Dict[str, float]:
        """Get current system resource usage"""
        
        return {
            "memory_percent": psutil.virtual_memory().percent,
            "cpu_percent": psutil.cpu_percent(),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "available_memory_gb": psutil.virtual_memory().available / 1024**3
        }
        
    def should_reduce_quality(self) -> bool:
        """Determine if quality should be reduced due to resource constraints"""
        
        resources = self.get_current_resources()
        
        # Reduce quality if memory usage > 85% or CPU > 90%
        return (
            resources["memory_percent"] > 85 or 
            resources["cpu_percent"] > 90
        )
        
    def get_recommended_performance_level(self) -> PerformanceLevel:
        """Get recommended performance level based on system resources"""
        
        resources = self.get_current_resources()
        
        if resources["memory_percent"] > 90 or resources["cpu_percent"] > 95:
            return PerformanceLevel.REAL_TIME
        elif resources["memory_percent"] > 80 or resources["cpu_percent"] > 85:
            return PerformanceLevel.INTERACTIVE
        elif resources["memory_percent"] > 70 or resources["cpu_percent"] > 75:
            return PerformanceLevel.BACKGROUND
        else:
            return PerformanceLevel.BATCH 