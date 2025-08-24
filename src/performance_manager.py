"""
Performance Manager for optimizing dashboard operations.

This module provides lazy loading, caching, and performance monitoring
capabilities for the cashbook dashboard to handle large numbers of cashbooks
efficiently.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps, lru_cache
try:
    from models import Cashbook, CashbookMetadata
    from cashbook_manager import CashbookManager
except ImportError:
    try:
        from .models import Cashbook, CashbookMetadata
        from .cashbook_manager import CashbookManager
    except ImportError:
        # For testing without customtkinter
        Cashbook = None
        CashbookMetadata = None
        CashbookManager = None


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_usage: Optional[int] = None
    items_processed: Optional[int] = None
    
    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000


class PerformanceMonitor:
    """Monitor and track performance metrics for dashboard operations."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
    
    def measure_operation(self, operation_name: str):
        """Decorator to measure operation performance."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Count items if result is a list
                    items_count = len(result) if isinstance(result, list) else None
                    
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    # Record metrics
                    metric = PerformanceMetrics(
                        operation_name=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        items_processed=items_count
                    )
                    
                    with self._lock:
                        self.metrics.append(metric)
                        # Keep only last 100 metrics to prevent memory growth
                        if len(self.metrics) > 100:
                            self.metrics = self.metrics[-100:]
                    
                    return result
                    
                except Exception as e:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    # Record failed operation
                    metric = PerformanceMetrics(
                        operation_name=f"{operation_name}_FAILED",
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration
                    )
                    
                    with self._lock:
                        self.metrics.append(metric)
                    
                    raise
            
            return wrapper
        return decorator
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        with self._lock:
            if not self.metrics:
                return {"total_operations": 0}
            
            # Group by operation name
            operations = {}
            for metric in self.metrics:
                op_name = metric.operation_name
                if op_name not in operations:
                    operations[op_name] = []
                operations[op_name].append(metric)
            
            # Calculate statistics for each operation
            summary = {"total_operations": len(self.metrics), "operations": {}}
            
            for op_name, op_metrics in operations.items():
                durations = [m.duration for m in op_metrics]
                summary["operations"][op_name] = {
                    "count": len(op_metrics),
                    "avg_duration_ms": (sum(durations) / len(durations)) * 1000,
                    "min_duration_ms": min(durations) * 1000,
                    "max_duration_ms": max(durations) * 1000,
                    "total_duration_ms": sum(durations) * 1000
                }
            
            return summary
    
    def get_slow_operations(self, threshold_ms: float = 100.0) -> List[PerformanceMetrics]:
        """Get operations that exceeded the performance threshold."""
        with self._lock:
            return [
                metric for metric in self.metrics
                if metric.duration_ms > threshold_ms
            ]


class LazyLoader:
    """Implements lazy loading for cashbook data to improve performance."""
    
    def __init__(self, cashbook_manager: CashbookManager, batch_size: int = 10):
        self.cashbook_manager = cashbook_manager
        self.batch_size = batch_size
        self._cache: Dict[str, Cashbook] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes
        self._lock = threading.Lock()
    
    def get_cashbooks_batch(self, offset: int = 0, limit: Optional[int] = None) -> List[Cashbook]:
        """
        Get a batch of cashbooks with lazy loading.
        
        Args:
            offset: Starting index for the batch
            limit: Maximum number of cashbooks to return
            
        Returns:
            List of cashbooks for the requested batch
        """
        if limit is None:
            limit = self.batch_size
        
        # Get all cashbook IDs sorted by last modified
        all_cashbooks = self.cashbook_manager.get_all_cashbooks()
        
        # Apply offset and limit
        batch_cashbooks = all_cashbooks[offset:offset + limit]
        
        # Load cashbooks with caching
        result = []
        for cashbook in batch_cashbooks:
            cached_cashbook = self._get_cached_cashbook(cashbook.id)
            if cached_cashbook:
                result.append(cached_cashbook)
            else:
                # Cache the cashbook
                self._cache_cashbook(cashbook)
                result.append(cashbook)
        
        return result
    
    def _get_cached_cashbook(self, cashbook_id: str) -> Optional[Cashbook]:
        """Get cashbook from cache if still valid."""
        with self._lock:
            if cashbook_id not in self._cache:
                return None
            
            # Check if cache is still valid
            cache_time = self._cache_timestamps.get(cashbook_id)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._cache[cashbook_id]
            else:
                # Remove expired cache entry
                self._cache.pop(cashbook_id, None)
                self._cache_timestamps.pop(cashbook_id, None)
                return None
    
    def _cache_cashbook(self, cashbook: Cashbook) -> None:
        """Cache a cashbook with timestamp."""
        with self._lock:
            self._cache[cashbook.id] = cashbook
            self._cache_timestamps[cashbook.id] = datetime.now()
            
            # Limit cache size to prevent memory growth
            if len(self._cache) > 100:
                # Remove oldest entries
                oldest_items = sorted(
                    self._cache_timestamps.items(),
                    key=lambda x: x[1]
                )[:20]  # Remove 20 oldest items
                
                for cashbook_id, _ in oldest_items:
                    self._cache.pop(cashbook_id, None)
                    self._cache_timestamps.pop(cashbook_id, None)
    
    def invalidate_cache(self, cashbook_id: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            cashbook_id: Specific cashbook to invalidate, or None to clear all
        """
        with self._lock:
            if cashbook_id:
                self._cache.pop(cashbook_id, None)
                self._cache_timestamps.pop(cashbook_id, None)
            else:
                self._cache.clear()
                self._cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            now = datetime.now()
            valid_entries = sum(
                1 for timestamp in self._cache_timestamps.values()
                if now - timestamp < self._cache_ttl
            )
            
            return {
                "total_entries": len(self._cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self._cache) - valid_entries,
                "cache_hit_ratio": valid_entries / max(len(self._cache), 1),
                "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60
            }


class PerformanceOptimizedManager:
    """
    Enhanced cashbook manager with performance optimizations.
    
    Provides lazy loading, caching, and performance monitoring
    for better handling of large numbers of cashbooks.
    """
    
    def __init__(self, cashbook_manager: CashbookManager):
        self.cashbook_manager = cashbook_manager
        self.performance_monitor = PerformanceMonitor()
        self.lazy_loader = LazyLoader(cashbook_manager)
        
        # Performance thresholds
        self.slow_operation_threshold_ms = 100.0
        self.large_dataset_threshold = 50
    
    @property
    def monitor(self) -> PerformanceMonitor:
        """Get the performance monitor."""
        return self.performance_monitor
    
    def get_recent_cashbooks_optimized(self, limit: int = 4) -> List[Cashbook]:
        """
        Get recent cashbooks with performance optimization.
        
        Args:
            limit: Maximum number of cashbooks to return
            
        Returns:
            List of recent cashbooks
        """
        start_time = time.perf_counter()
        try:
            # For small limits, use regular method
            if limit <= 10:
                result = self.cashbook_manager.get_recent_cashbooks(limit)
            else:
                # For larger limits, use lazy loading
                result = self.lazy_loader.get_cashbooks_batch(offset=0, limit=limit)
            
            # Record performance metric
            end_time = time.perf_counter()
            duration = end_time - start_time
            metric = PerformanceMetrics(
                operation_name="get_recent_cashbooks_optimized",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                items_processed=len(result) if isinstance(result, list) else None
            )
            self.performance_monitor.metrics.append(metric)
            
            return result
        except Exception as e:
            # Record failed operation
            end_time = time.perf_counter()
            duration = end_time - start_time
            metric = PerformanceMetrics(
                operation_name="get_recent_cashbooks_optimized_FAILED",
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            self.performance_monitor.metrics.append(metric)
            raise
    
    def get_all_cashbooks_paginated(self, page: int = 0, page_size: int = 20) -> Dict[str, Any]:
        """
        Get all cashbooks with pagination for better performance.
        
        Args:
            page: Page number (0-based)
            page_size: Number of cashbooks per page
            
        Returns:
            Dictionary with cashbooks, pagination info, and metadata
        """
        offset = page * page_size
        
        # Get total count efficiently
        total_count = len(self.cashbook_manager._cashbooks)
        
        # Get the requested page
        cashbooks = self.lazy_loader.get_cashbooks_batch(offset=offset, limit=page_size)
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages - 1
        has_prev = page > 0
        
        return {
            "cashbooks": cashbooks,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": has_next,
                "has_prev": has_prev,
                "start_index": offset,
                "end_index": min(offset + page_size, total_count)
            },
            "performance": {
                "is_large_dataset": total_count > self.large_dataset_threshold,
                "cache_stats": self.lazy_loader.get_cache_stats()
            }
        }
    
    def search_cashbooks(self, query: str, limit: int = 20) -> List[Cashbook]:
        """
        Search cashbooks by name, description, or category.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching cashbooks
        """
        start_time = time.perf_counter()
        try:
            if not query.strip():
                return []
            
            query_lower = query.lower().strip()
            results = []
            
            # Search through all cashbooks
            for cashbook in self.cashbook_manager.get_all_cashbooks():
                # Check name, description, and category
                if (query_lower in cashbook.name.lower() or
                    query_lower in cashbook.description.lower() or
                    query_lower in cashbook.category.lower()):
                    results.append(cashbook)
                    
                    if len(results) >= limit:
                        break
            
            # Record performance metric
            end_time = time.perf_counter()
            duration = end_time - start_time
            metric = PerformanceMetrics(
                operation_name="search_cashbooks",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                items_processed=len(results)
            )
            self.performance_monitor.metrics.append(metric)
            
            return results
        except Exception as e:
            # Record failed operation
            end_time = time.perf_counter()
            duration = end_time - start_time
            metric = PerformanceMetrics(
                operation_name="search_cashbooks_FAILED",
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            self.performance_monitor.metrics.append(metric)
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        metrics_summary = self.performance_monitor.get_metrics_summary()
        slow_operations = self.performance_monitor.get_slow_operations(
            self.slow_operation_threshold_ms
        )
        cache_stats = self.lazy_loader.get_cache_stats()
        
        # Analyze dataset size
        total_cashbooks = len(self.cashbook_manager._cashbooks)
        is_large_dataset = total_cashbooks > self.large_dataset_threshold
        
        return {
            "dataset_info": {
                "total_cashbooks": total_cashbooks,
                "is_large_dataset": is_large_dataset,
                "large_dataset_threshold": self.large_dataset_threshold
            },
            "performance_metrics": metrics_summary,
            "slow_operations": [
                {
                    "operation": op.operation_name,
                    "duration_ms": op.duration_ms,
                    "items_processed": op.items_processed,
                    "timestamp": datetime.fromtimestamp(op.start_time).isoformat()
                }
                for op in slow_operations[-10:]  # Last 10 slow operations
            ],
            "cache_performance": cache_stats,
            "recommendations": self._generate_performance_recommendations(
                total_cashbooks, metrics_summary, cache_stats
            )
        }
    
    def _generate_performance_recommendations(
        self, 
        total_cashbooks: int, 
        metrics: Dict[str, Any], 
        cache_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Dataset size recommendations
        if total_cashbooks > self.large_dataset_threshold:
            recommendations.append(
                f"Large dataset detected ({total_cashbooks} cashbooks). "
                "Consider using pagination for better performance."
            )
        
        # Cache performance recommendations
        if cache_stats.get("cache_hit_ratio", 0) < 0.7:
            recommendations.append(
                "Low cache hit ratio detected. Consider increasing cache TTL "
                "or reviewing data access patterns."
            )
        
        # Operation performance recommendations
        operations = metrics.get("operations", {})
        for op_name, op_stats in operations.items():
            if op_stats.get("avg_duration_ms", 0) > self.slow_operation_threshold_ms:
                recommendations.append(
                    f"Operation '{op_name}' is slow (avg: {op_stats['avg_duration_ms']:.1f}ms). "
                    "Consider optimization or caching."
                )
        
        if not recommendations:
            recommendations.append("Performance is optimal. No recommendations at this time.")
        
        return recommendations
    
    def optimize_for_large_dataset(self) -> None:
        """Apply optimizations for large datasets."""
        # Increase cache size and TTL for large datasets
        if len(self.cashbook_manager._cashbooks) > self.large_dataset_threshold:
            self.lazy_loader._cache_ttl = timedelta(minutes=10)  # Longer cache
            
            # Pre-warm cache with recent cashbooks
            recent_cashbooks = self.cashbook_manager.get_recent_cashbooks(limit=20)
            for cashbook in recent_cashbooks:
                self.lazy_loader._cache_cashbook(cashbook)
    
    def clear_performance_data(self) -> None:
        """Clear all performance monitoring data."""
        self.performance_monitor.metrics.clear()
        self.lazy_loader.invalidate_cache()