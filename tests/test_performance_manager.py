"""
Unit tests for the PerformanceManager module.

Tests performance monitoring, lazy loading, caching, and optimization
functionality for the dashboard components.
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from performance_manager import (
        PerformanceMetrics, PerformanceMonitor, LazyLoader, 
        PerformanceOptimizedManager
    )
    from models import Cashbook, CashbookMetadata
    from cashbook_manager import CashbookManager
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    PerformanceMetrics = None
    PerformanceMonitor = None
    LazyLoader = None
    PerformanceOptimizedManager = None
    Cashbook = None
    CashbookMetadata = None
    CashbookManager = None


@pytest.mark.skipif(not PERFORMANCE_AVAILABLE, reason="Performance manager not available")
class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics dataclass."""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        start_time = time.perf_counter()
        end_time = start_time + 0.1
        
        metrics = PerformanceMetrics(
            operation_name="test_operation",
            start_time=start_time,
            end_time=end_time,
            duration=0.1,
            items_processed=10
        )
        
        assert metrics.operation_name == "test_operation"
        assert metrics.start_time == start_time
        assert metrics.end_time == end_time
        assert metrics.duration == 0.1
        assert metrics.items_processed == 10
        assert metrics.duration_ms == 100.0
    
    def test_duration_ms_property(self):
        """Test duration_ms property calculation."""
        metrics = PerformanceMetrics(
            operation_name="test",
            start_time=0,
            end_time=0.05,
            duration=0.05
        )
        
        assert metrics.duration_ms == 50.0


@pytest.mark.skipif(not PERFORMANCE_AVAILABLE, reason="Performance manager not available")
class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a performance monitor instance."""
        return PerformanceMonitor()
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.metrics == []
        assert hasattr(monitor, '_lock')
    
    def test_measure_operation_decorator(self, monitor):
        """Test the measure_operation decorator."""
        @monitor.measure_operation("test_function")
        def test_function(x, y):
            time.sleep(0.01)  # Small delay to measure
            return x + y
        
        result = test_function(2, 3)
        
        assert result == 5
        assert len(monitor.metrics) == 1
        
        metric = monitor.metrics[0]
        assert metric.operation_name == "test_function"
        assert metric.duration > 0
        assert metric.items_processed is None  # No list returned
    
    def test_measure_operation_with_list_result(self, monitor):
        """Test measuring operation that returns a list."""
        @monitor.measure_operation("list_function")
        def list_function():
            return [1, 2, 3, 4, 5]
        
        result = list_function()
        
        assert result == [1, 2, 3, 4, 5]
        assert len(monitor.metrics) == 1
        
        metric = monitor.metrics[0]
        assert metric.operation_name == "list_function"
        assert metric.items_processed == 5
    
    def test_measure_operation_with_exception(self, monitor):
        """Test measuring operation that raises an exception."""
        @monitor.measure_operation("failing_function")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_function()
        
        assert len(monitor.metrics) == 1
        
        metric = monitor.metrics[0]
        assert metric.operation_name == "failing_function_FAILED"
        assert metric.duration > 0
    
    def test_get_metrics_summary_empty(self, monitor):
        """Test getting metrics summary when no metrics exist."""
        summary = monitor.get_metrics_summary()
        
        assert summary == {"total_operations": 0}
    
    def test_get_metrics_summary_with_data(self, monitor):
        """Test getting metrics summary with data."""
        # Add some test metrics
        monitor.metrics = [
            PerformanceMetrics("op1", 0, 0.1, 0.1),
            PerformanceMetrics("op1", 0, 0.2, 0.2),
            PerformanceMetrics("op2", 0, 0.05, 0.05)
        ]
        
        summary = monitor.get_metrics_summary()
        
        assert summary["total_operations"] == 3
        assert "operations" in summary
        assert "op1" in summary["operations"]
        assert "op2" in summary["operations"]
        
        op1_stats = summary["operations"]["op1"]
        assert op1_stats["count"] == 2
        assert op1_stats["avg_duration_ms"] == 150.0  # (100 + 200) / 2
        assert op1_stats["min_duration_ms"] == 100.0
        assert op1_stats["max_duration_ms"] == 200.0
    
    def test_get_slow_operations(self, monitor):
        """Test getting slow operations."""
        # Add metrics with different durations
        monitor.metrics = [
            PerformanceMetrics("fast_op", 0, 0.05, 0.05),  # 50ms
            PerformanceMetrics("slow_op", 0, 0.15, 0.15),  # 150ms
            PerformanceMetrics("very_slow_op", 0, 0.25, 0.25)  # 250ms
        ]
        
        slow_ops = monitor.get_slow_operations(threshold_ms=100.0)
        
        assert len(slow_ops) == 2
        assert slow_ops[0].operation_name == "slow_op"
        assert slow_ops[1].operation_name == "very_slow_op"
    
    def test_metrics_limit(self, monitor):
        """Test that metrics are limited to prevent memory growth."""
        # Add more than 100 metrics
        for i in range(150):
            monitor.metrics.append(
                PerformanceMetrics(f"op_{i}", 0, 0.01, 0.01)
            )
        
        # Trigger the limit by adding one more through decorator
        @monitor.measure_operation("trigger_limit")
        def test_func():
            return []
        
        test_func()
        
        # Should be limited to 100 metrics
        assert len(monitor.metrics) == 100
    
    def test_thread_safety(self, monitor):
        """Test thread safety of performance monitor."""
        results = []
        
        def worker():
            @monitor.measure_operation("thread_test")
            def thread_function():
                time.sleep(0.001)
                return [1, 2, 3]
            
            result = thread_function()
            results.append(result)
        
        # Create multiple threads
        threads = [threading.Thread(target=worker) for _ in range(10)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 10
        assert len(monitor.metrics) == 10
        
        # All operations should be recorded
        for metric in monitor.metrics:
            assert metric.operation_name == "thread_test"
            assert metric.items_processed == 3


@pytest.mark.skipif(not PERFORMANCE_AVAILABLE, reason="Performance manager not available")
class TestLazyLoader:
    """Test cases for LazyLoader class."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create a mock cashbook manager."""
        manager = Mock(spec=CashbookManager)
        
        # Create test cashbooks
        cashbooks = []
        for i in range(20):
            cashbook = Cashbook(
                id=f"cb_{i}",
                name=f"Cashbook {i}",
                description=f"Description {i}",
                category="Test"
            )
            cashbooks.append(cashbook)
        
        manager.get_all_cashbooks.return_value = cashbooks
        return manager
    
    @pytest.fixture
    def lazy_loader(self, mock_manager):
        """Create a lazy loader instance."""
        return LazyLoader(mock_manager, batch_size=5)
    
    def test_lazy_loader_initialization(self, lazy_loader, mock_manager):
        """Test lazy loader initialization."""
        assert lazy_loader.cashbook_manager == mock_manager
        assert lazy_loader.batch_size == 5
        assert lazy_loader._cache == {}
        assert lazy_loader._cache_timestamps == {}
    
    def test_get_cashbooks_batch_basic(self, lazy_loader):
        """Test getting a basic batch of cashbooks."""
        batch = lazy_loader.get_cashbooks_batch(offset=0, limit=3)
        
        assert len(batch) == 3
        assert batch[0].name == "Cashbook 0"
        assert batch[1].name == "Cashbook 1"
        assert batch[2].name == "Cashbook 2"
    
    def test_get_cashbooks_batch_with_offset(self, lazy_loader):
        """Test getting a batch with offset."""
        batch = lazy_loader.get_cashbooks_batch(offset=5, limit=3)
        
        assert len(batch) == 3
        assert batch[0].name == "Cashbook 5"
        assert batch[1].name == "Cashbook 6"
        assert batch[2].name == "Cashbook 7"
    
    def test_get_cashbooks_batch_default_limit(self, lazy_loader):
        """Test getting a batch with default limit."""
        batch = lazy_loader.get_cashbooks_batch(offset=0)
        
        assert len(batch) == 5  # Default batch_size
    
    def test_caching_functionality(self, lazy_loader):
        """Test that cashbooks are cached properly."""
        # First call should cache the cashbooks
        batch1 = lazy_loader.get_cashbooks_batch(offset=0, limit=2)
        
        # Check that cashbooks are cached
        assert len(lazy_loader._cache) == 2
        assert "cb_0" in lazy_loader._cache
        assert "cb_1" in lazy_loader._cache
        
        # Second call should use cache
        batch2 = lazy_loader.get_cashbooks_batch(offset=0, limit=2)
        
        # Results should be the same
        assert batch1[0].id == batch2[0].id
        assert batch1[1].id == batch2[1].id
    
    def test_cache_expiration(self, lazy_loader):
        """Test that cache entries expire properly."""
        # Set a very short TTL for testing
        lazy_loader._cache_ttl = timedelta(milliseconds=10)
        
        # Get a batch to populate cache
        batch1 = lazy_loader.get_cashbooks_batch(offset=0, limit=1)
        assert len(lazy_loader._cache) == 1
        
        # Wait for cache to expire
        time.sleep(0.02)
        
        # Get the same batch again
        batch2 = lazy_loader.get_cashbooks_batch(offset=0, limit=1)
        
        # Cache should have been refreshed
        assert len(lazy_loader._cache) == 1
    
    def test_cache_size_limit(self, lazy_loader):
        """Test that cache size is limited."""
        # Get many batches to exceed cache limit
        for i in range(0, 120, 5):  # This will cache 120 items
            lazy_loader.get_cashbooks_batch(offset=i % 20, limit=1)
        
        # Cache should be limited
        assert len(lazy_loader._cache) <= 100
    
    def test_invalidate_cache_specific(self, lazy_loader):
        """Test invalidating specific cache entry."""
        # Populate cache
        lazy_loader.get_cashbooks_batch(offset=0, limit=3)
        assert len(lazy_loader._cache) == 3
        
        # Invalidate specific entry
        lazy_loader.invalidate_cache("cb_1")
        
        assert len(lazy_loader._cache) == 2
        assert "cb_1" not in lazy_loader._cache
        assert "cb_0" in lazy_loader._cache
        assert "cb_2" in lazy_loader._cache
    
    def test_invalidate_cache_all(self, lazy_loader):
        """Test invalidating all cache entries."""
        # Populate cache
        lazy_loader.get_cashbooks_batch(offset=0, limit=3)
        assert len(lazy_loader._cache) == 3
        
        # Invalidate all
        lazy_loader.invalidate_cache()
        
        assert len(lazy_loader._cache) == 0
        assert len(lazy_loader._cache_timestamps) == 0
    
    def test_get_cache_stats(self, lazy_loader):
        """Test getting cache statistics."""
        # Initially empty
        stats = lazy_loader.get_cache_stats()
        assert stats["total_entries"] == 0
        assert stats["valid_entries"] == 0
        
        # Add some entries
        lazy_loader.get_cashbooks_batch(offset=0, limit=3)
        
        stats = lazy_loader.get_cache_stats()
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 3
        assert stats["expired_entries"] == 0
        assert stats["cache_hit_ratio"] == 1.0
    
    def test_thread_safety(self, lazy_loader):
        """Test thread safety of lazy loader."""
        results = []
        
        def worker(offset):
            batch = lazy_loader.get_cashbooks_batch(offset=offset, limit=2)
            results.append(batch)
        
        # Create multiple threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        
        # Cache should contain entries (exact number may vary due to threading)
        assert len(lazy_loader._cache) > 0


@pytest.mark.skipif(not PERFORMANCE_AVAILABLE, reason="Performance manager not available")
class TestPerformanceOptimizedManager:
    """Test cases for PerformanceOptimizedManager class."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create a mock cashbook manager."""
        manager = Mock(spec=CashbookManager)
        
        # Create test cashbooks
        cashbooks = []
        for i in range(30):
            cashbook = Cashbook(
                id=f"cb_{i}",
                name=f"Cashbook {i}",
                description=f"Description {i}",
                category="Test" if i % 2 == 0 else "Personal"
            )
            cashbooks.append(cashbook)
        
        manager.get_all_cashbooks.return_value = cashbooks
        manager.get_recent_cashbooks.return_value = cashbooks[:10]
        manager._cashbooks = {cb.id: cb for cb in cashbooks}
        
        return manager
    
    @pytest.fixture
    def optimized_manager(self, mock_manager):
        """Create an optimized manager instance."""
        return PerformanceOptimizedManager(mock_manager)
    
    def test_optimized_manager_initialization(self, optimized_manager, mock_manager):
        """Test optimized manager initialization."""
        assert optimized_manager.cashbook_manager == mock_manager
        assert hasattr(optimized_manager, 'performance_monitor')
        assert hasattr(optimized_manager, 'lazy_loader')
        assert optimized_manager.slow_operation_threshold_ms == 100.0
        assert optimized_manager.large_dataset_threshold == 50
    
    def test_get_recent_cashbooks_optimized_small_limit(self, optimized_manager):
        """Test optimized recent cashbooks with small limit."""
        result = optimized_manager.get_recent_cashbooks_optimized(limit=5)
        
        assert len(result) == 5
        # Should use regular method for small limits
        optimized_manager.cashbook_manager.get_recent_cashbooks.assert_called_once_with(5)
    
    def test_get_recent_cashbooks_optimized_large_limit(self, optimized_manager):
        """Test optimized recent cashbooks with large limit."""
        result = optimized_manager.get_recent_cashbooks_optimized(limit=15)
        
        assert len(result) == 15
        # Should use lazy loading for large limits
    
    def test_get_all_cashbooks_paginated(self, optimized_manager):
        """Test paginated cashbook retrieval."""
        result = optimized_manager.get_all_cashbooks_paginated(page=0, page_size=10)
        
        assert "cashbooks" in result
        assert "pagination" in result
        assert "performance" in result
        
        # Check pagination info
        pagination = result["pagination"]
        assert pagination["current_page"] == 0
        assert pagination["page_size"] == 10
        assert pagination["total_count"] == 30
        assert pagination["total_pages"] == 3
        assert pagination["has_next"] is True
        assert pagination["has_prev"] is False
        
        # Check cashbooks
        assert len(result["cashbooks"]) == 10
    
    def test_get_all_cashbooks_paginated_last_page(self, optimized_manager):
        """Test paginated retrieval of last page."""
        result = optimized_manager.get_all_cashbooks_paginated(page=2, page_size=10)
        
        pagination = result["pagination"]
        assert pagination["current_page"] == 2
        assert pagination["has_next"] is False
        assert pagination["has_prev"] is True
        
        # Last page should have remaining items
        assert len(result["cashbooks"]) == 10
    
    def test_search_cashbooks(self, optimized_manager):
        """Test cashbook search functionality."""
        # Search by name
        results = optimized_manager.search_cashbooks("Cashbook 1")
        
        # Should find cashbooks with "1" in the name
        assert len(results) > 0
        for cashbook in results:
            assert "1" in cashbook.name
    
    def test_search_cashbooks_empty_query(self, optimized_manager):
        """Test search with empty query."""
        results = optimized_manager.search_cashbooks("")
        assert results == []
        
        results = optimized_manager.search_cashbooks("   ")
        assert results == []
    
    def test_search_cashbooks_by_category(self, optimized_manager):
        """Test search by category."""
        results = optimized_manager.search_cashbooks("Personal")
        
        assert len(results) > 0
        for cashbook in results:
            assert "Personal" in cashbook.category
    
    def test_search_cashbooks_limit(self, optimized_manager):
        """Test search result limit."""
        results = optimized_manager.search_cashbooks("Cashbook", limit=5)
        
        assert len(results) <= 5
    
    def test_get_performance_report(self, optimized_manager):
        """Test getting performance report."""
        # Perform some operations to generate metrics
        optimized_manager.get_recent_cashbooks_optimized(5)
        optimized_manager.search_cashbooks("test")
        
        report = optimized_manager.get_performance_report()
        
        assert "dataset_info" in report
        assert "performance_metrics" in report
        assert "slow_operations" in report
        assert "cache_performance" in report
        assert "recommendations" in report
        
        # Check dataset info
        dataset_info = report["dataset_info"]
        assert dataset_info["total_cashbooks"] == 30
        assert dataset_info["is_large_dataset"] is False  # 30 < 50
    
    def test_optimize_for_large_dataset(self, optimized_manager):
        """Test optimization for large datasets."""
        # Mock a large dataset
        optimized_manager.cashbook_manager._cashbooks = {
            f"cb_{i}": Mock() for i in range(100)
        }
        
        original_ttl = optimized_manager.lazy_loader._cache_ttl
        
        optimized_manager.optimize_for_large_dataset()
        
        # Should increase cache TTL for large datasets
        assert optimized_manager.lazy_loader._cache_ttl > original_ttl
    
    def test_clear_performance_data(self, optimized_manager):
        """Test clearing performance data."""
        # Generate some data
        optimized_manager.get_recent_cashbooks_optimized(5)
        
        # Should have metrics and cache
        assert len(optimized_manager.performance_monitor.metrics) > 0
        
        optimized_manager.clear_performance_data()
        
        # Should be cleared
        assert len(optimized_manager.performance_monitor.metrics) == 0
    
    def test_performance_monitoring_integration(self, optimized_manager):
        """Test that operations are properly monitored."""
        # Perform operations
        optimized_manager.get_recent_cashbooks_optimized(5)
        optimized_manager.search_cashbooks("test")
        
        # Check that metrics were recorded
        metrics = optimized_manager.performance_monitor.get_metrics_summary()
        assert metrics["total_operations"] >= 2
        
        operations = metrics.get("operations", {})
        assert "get_recent_cashbooks_optimized" in operations
        assert "search_cashbooks" in operations


if __name__ == '__main__':
    pytest.main([__file__])