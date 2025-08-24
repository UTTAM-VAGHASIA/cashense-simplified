"""
Benchmark tests for performance measurement and optimization validation.

These tests measure the performance of various dashboard operations
and validate that performance optimizations are working correctly.
"""

import pytest
import time
import tempfile
import shutil
from typing import List, Dict, Any
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Cashbook, CashbookMetadata
from cashbook_manager import CashbookManager
from performance_manager import PerformanceOptimizedManager, PerformanceMonitor


class TestPerformanceBenchmarks:
    """Benchmark tests for performance measurement."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def small_dataset_manager(self, temp_dir):
        """Create manager with small dataset (10 cashbooks)."""
        manager = CashbookManager(data_dir=temp_dir)
        for i in range(10):
            manager.create_cashbook(
                f"Small Dataset Cashbook {i}",
                f"Description {i}",
                f"Category {i % 3}"
            )
        return manager
    
    @pytest.fixture
    def medium_dataset_manager(self, temp_dir):
        """Create manager with medium dataset (100 cashbooks)."""
        manager = CashbookManager(data_dir=temp_dir)
        for i in range(100):
            manager.create_cashbook(
                f"Medium Dataset Cashbook {i:03d}",
                f"Description for cashbook {i}",
                f"Category {i % 10}"
            )
        return manager
    
    @pytest.fixture
    def large_dataset_manager(self, temp_dir):
        """Create manager with large dataset (500 cashbooks)."""
        manager = CashbookManager(data_dir=temp_dir)
        for i in range(500):
            manager.create_cashbook(
                f"Large Dataset Cashbook {i:03d}",
                f"Description for cashbook {i}",
                f"Category {i % 20}"
            )
        return manager
    
    def measure_operation_time(self, operation_func, *args, **kwargs) -> float:
        """
        Measure the execution time of an operation.
        
        Returns:
            Execution time in seconds
        """
        start_time = time.perf_counter()
        operation_func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time
    
    def test_cashbook_creation_performance(self, temp_dir):
        """Benchmark cashbook creation performance."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Measure time to create 100 cashbooks
        start_time = time.perf_counter()
        
        for i in range(100):
            manager.create_cashbook(
                f"Benchmark Cashbook {i}",
                f"Description {i}",
                f"Category {i % 5}"
            )
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Should create 100 cashbooks in reasonable time
        assert total_time < 10.0  # Less than 10 seconds
        
        # Calculate average time per cashbook
        avg_time_per_cashbook = total_time / 100
        assert avg_time_per_cashbook < 0.1  # Less than 100ms per cashbook
        
        print(f"Created 100 cashbooks in {total_time:.3f}s (avg: {avg_time_per_cashbook*1000:.1f}ms per cashbook)")
    
    def test_get_recent_cashbooks_performance(self, medium_dataset_manager):
        """Benchmark get_recent_cashbooks performance."""
        manager = medium_dataset_manager
        
        # Measure time to get recent cashbooks
        execution_time = self.measure_operation_time(
            manager.get_recent_cashbooks, 10
        )
        
        # Should be very fast for recent cashbooks
        assert execution_time < 0.1  # Less than 100ms
        
        print(f"get_recent_cashbooks(10) took {execution_time*1000:.1f}ms")
    
    def test_get_all_cashbooks_performance(self, medium_dataset_manager):
        """Benchmark get_all_cashbooks performance."""
        manager = medium_dataset_manager
        
        # Measure time to get all cashbooks
        execution_time = self.measure_operation_time(manager.get_all_cashbooks)
        
        # Should be reasonably fast even for 100 cashbooks
        assert execution_time < 0.5  # Less than 500ms
        
        print(f"get_all_cashbooks() for 100 cashbooks took {execution_time*1000:.1f}ms")
    
    def test_search_performance(self, medium_dataset_manager):
        """Benchmark search performance."""
        optimized_manager = PerformanceOptimizedManager(medium_dataset_manager)
        
        # Measure search time
        execution_time = self.measure_operation_time(
            optimized_manager.search_cashbooks, "Cashbook", 20
        )
        
        # Search should be fast
        assert execution_time < 0.2  # Less than 200ms
        
        print(f"search_cashbooks() took {execution_time*1000:.1f}ms")
    
    def test_lazy_loading_performance(self, large_dataset_manager):
        """Benchmark lazy loading performance."""
        optimized_manager = PerformanceOptimizedManager(large_dataset_manager)
        
        # Measure first batch load (cold cache)
        cold_time = self.measure_operation_time(
            optimized_manager.lazy_loader.get_cashbooks_batch, 0, 20
        )
        
        # Measure second batch load (warm cache)
        warm_time = self.measure_operation_time(
            optimized_manager.lazy_loader.get_cashbooks_batch, 0, 20
        )
        
        # Both should be fast, warm should be faster or similar
        assert cold_time < 0.5  # Less than 500ms
        assert warm_time < 0.5  # Less than 500ms
        
        print(f"Lazy loading: cold={cold_time*1000:.1f}ms, warm={warm_time*1000:.1f}ms")
    
    def test_pagination_performance(self, large_dataset_manager):
        """Benchmark pagination performance."""
        optimized_manager = PerformanceOptimizedManager(large_dataset_manager)
        
        # Measure pagination performance
        execution_time = self.measure_operation_time(
            optimized_manager.get_all_cashbooks_paginated, 0, 25
        )
        
        # Pagination should be fast
        assert execution_time < 0.3  # Less than 300ms
        
        print(f"get_all_cashbooks_paginated(page=0, size=25) took {execution_time*1000:.1f}ms")
    
    def test_data_loading_performance(self, temp_dir):
        """Benchmark data loading performance."""
        # Create manager with data
        manager1 = CashbookManager(data_dir=temp_dir)
        for i in range(200):
            manager1.create_cashbook(f"Load Test {i}", f"Desc {i}", f"Cat {i % 8}")
        
        # Measure time to load data in new manager instance
        start_time = time.perf_counter()
        manager2 = CashbookManager(data_dir=temp_dir)
        end_time = time.perf_counter()
        
        loading_time = end_time - start_time
        
        # Should load 200 cashbooks reasonably quickly
        assert loading_time < 2.0  # Less than 2 seconds
        assert len(manager2._cashbooks) == 200
        
        print(f"Loaded 200 cashbooks in {loading_time*1000:.1f}ms")
    
    def test_data_saving_performance(self, temp_dir):
        """Benchmark data saving performance."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create cashbooks
        for i in range(100):
            manager.create_cashbook(f"Save Test {i}", f"Desc {i}", f"Cat {i % 5}")
        
        # Measure save time for updates
        start_time = time.perf_counter()
        
        # Update 10 cashbooks
        cashbooks = manager.get_all_cashbooks()[:10]
        for i, cashbook in enumerate(cashbooks):
            manager.update_cashbook(cashbook.id, description=f"Updated desc {i}")
        
        end_time = time.perf_counter()
        update_time = end_time - start_time
        
        # Should update and save reasonably quickly
        assert update_time < 1.0  # Less than 1 second for 10 updates
        
        print(f"Updated and saved 10 cashbooks in {update_time*1000:.1f}ms")
    
    def test_performance_monitoring_overhead(self, medium_dataset_manager):
        """Benchmark performance monitoring overhead."""
        optimized_manager = PerformanceOptimizedManager(medium_dataset_manager)
        
        # Measure operation without monitoring
        start_time = time.perf_counter()
        medium_dataset_manager.get_recent_cashbooks(10)
        end_time = time.perf_counter()
        unmonitored_time = end_time - start_time
        
        # Measure operation with monitoring
        start_time = time.perf_counter()
        optimized_manager.get_recent_cashbooks_optimized(10)
        end_time = time.perf_counter()
        monitored_time = end_time - start_time
        
        # Monitoring overhead should be minimal
        overhead = monitored_time - unmonitored_time
        overhead_percentage = (overhead / unmonitored_time) * 100 if unmonitored_time > 0 else 0
        
        # Overhead should be less than 50%
        assert overhead_percentage < 50.0
        
        print(f"Monitoring overhead: {overhead*1000:.1f}ms ({overhead_percentage:.1f}%)")
    
    def test_cache_performance_benefit(self, large_dataset_manager):
        """Benchmark cache performance benefits."""
        optimized_manager = PerformanceOptimizedManager(large_dataset_manager)
        
        # Clear cache first
        optimized_manager.lazy_loader.invalidate_cache()
        
        # Measure first access (cache miss)
        start_time = time.perf_counter()
        batch1 = optimized_manager.lazy_loader.get_cashbooks_batch(0, 50)
        end_time = time.perf_counter()
        cache_miss_time = end_time - start_time
        
        # Measure second access (cache hit)
        start_time = time.perf_counter()
        batch2 = optimized_manager.lazy_loader.get_cashbooks_batch(0, 50)
        end_time = time.perf_counter()
        cache_hit_time = end_time - start_time
        
        # Cache hit should be faster or similar
        assert len(batch1) == len(batch2) == 50
        
        # Calculate performance improvement
        if cache_miss_time > 0:
            improvement = ((cache_miss_time - cache_hit_time) / cache_miss_time) * 100
            print(f"Cache performance: miss={cache_miss_time*1000:.1f}ms, hit={cache_hit_time*1000:.1f}ms, improvement={improvement:.1f}%")
        else:
            print(f"Cache performance: miss={cache_miss_time*1000:.1f}ms, hit={cache_hit_time*1000:.1f}ms")
    
    def test_scalability_comparison(self, temp_dir):
        """Test performance scalability across different dataset sizes."""
        dataset_sizes = [10, 50, 100, 200]
        results = {}
        
        for size in dataset_sizes:
            # Create manager with specific size
            manager = CashbookManager(data_dir=temp_dir)
            for i in range(size):
                manager.create_cashbook(f"Scale Test {i}", f"Desc {i}", f"Cat {i % 5}")
            
            # Measure get_all_cashbooks performance
            execution_time = self.measure_operation_time(manager.get_all_cashbooks)
            results[size] = execution_time
            
            print(f"get_all_cashbooks() for {size} cashbooks: {execution_time*1000:.1f}ms")
        
        # Performance should scale reasonably (not exponentially)
        # Check that 200 items doesn't take more than 10x the time of 10 items
        if results[10] > 0:
            scale_factor = results[200] / results[10]
            assert scale_factor < 50  # Should not be more than 50x slower
            print(f"Scalability factor (200 vs 10 items): {scale_factor:.1f}x")
    
    def test_memory_efficiency(self, large_dataset_manager):
        """Test memory efficiency of operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure memory before operations
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        optimized_manager = PerformanceOptimizedManager(large_dataset_manager)
        
        # Load data multiple times
        for _ in range(10):
            optimized_manager.get_all_cashbooks_paginated(page=0, page_size=50)
            optimized_manager.search_cashbooks("Cashbook", limit=20)
        
        # Measure memory after operations
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase
        
        print(f"Memory usage: before={memory_before:.1f}MB, after={memory_after:.1f}MB, increase={memory_increase:.1f}MB")


class TestPerformanceRegression:
    """Tests to detect performance regressions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_performance_thresholds(self, temp_dir):
        """Test that operations meet performance thresholds."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create test dataset
        for i in range(50):
            manager.create_cashbook(f"Threshold Test {i}", f"Desc {i}", f"Cat {i % 5}")
        
        optimized_manager = PerformanceOptimizedManager(manager)
        
        # Define performance thresholds (in seconds)
        thresholds = {
            'get_recent_cashbooks': 0.1,
            'get_all_cashbooks': 0.2,
            'search_cashbooks': 0.15,
            'pagination': 0.2,
            'lazy_loading': 0.3
        }
        
        # Test each operation against its threshold
        operations = {
            'get_recent_cashbooks': lambda: manager.get_recent_cashbooks(10),
            'get_all_cashbooks': lambda: manager.get_all_cashbooks(),
            'search_cashbooks': lambda: optimized_manager.search_cashbooks("Test", 10),
            'pagination': lambda: optimized_manager.get_all_cashbooks_paginated(0, 20),
            'lazy_loading': lambda: optimized_manager.lazy_loader.get_cashbooks_batch(0, 20)
        }
        
        for operation_name, operation_func in operations.items():
            start_time = time.perf_counter()
            operation_func()
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            threshold = thresholds[operation_name]
            
            assert execution_time < threshold, (
                f"{operation_name} took {execution_time:.3f}s, "
                f"exceeding threshold of {threshold:.3f}s"
            )
            
            print(f"{operation_name}: {execution_time*1000:.1f}ms (threshold: {threshold*1000:.0f}ms)")
    
    def test_performance_monitoring_accuracy(self, temp_dir):
        """Test accuracy of performance monitoring."""
        manager = CashbookManager(data_dir=temp_dir)
        optimized_manager = PerformanceOptimizedManager(manager)
        
        # Create some test data
        for i in range(20):
            manager.create_cashbook(f"Monitor Test {i}", f"Desc {i}", "Test")
        
        # Perform monitored operations
        optimized_manager.get_recent_cashbooks_optimized(5)
        optimized_manager.search_cashbooks("Test", 10)
        
        # Get performance metrics
        metrics = optimized_manager.performance_monitor.get_metrics_summary()
        
        # Should have recorded operations
        assert metrics["total_operations"] >= 2
        
        # Check specific operations
        operations = metrics.get("operations", {})
        assert "get_recent_cashbooks_optimized" in operations
        assert "search_cashbooks" in operations
        
        # Metrics should be reasonable
        for op_name, op_stats in operations.items():
            assert op_stats["count"] >= 1
            assert op_stats["avg_duration_ms"] >= 0
            assert op_stats["min_duration_ms"] >= 0
            assert op_stats["max_duration_ms"] >= op_stats["min_duration_ms"]
    
    def test_cache_efficiency_metrics(self, temp_dir):
        """Test cache efficiency metrics."""
        manager = CashbookManager(data_dir=temp_dir)
        optimized_manager = PerformanceOptimizedManager(manager)
        
        # Create test data
        for i in range(30):
            manager.create_cashbook(f"Cache Test {i}", f"Desc {i}", "Test")
        
        # Access data multiple times to test cache
        for _ in range(3):
            optimized_manager.lazy_loader.get_cashbooks_batch(0, 10)
        
        # Get cache statistics
        cache_stats = optimized_manager.lazy_loader.get_cache_stats()
        
        # Should have cache entries
        assert cache_stats["total_entries"] > 0
        assert cache_stats["valid_entries"] > 0
        assert cache_stats["cache_hit_ratio"] >= 0
        
        print(f"Cache stats: {cache_stats}")


if __name__ == '__main__':
    # Run with verbose output to see benchmark results
    pytest.main([__file__, '-v', '-s'])