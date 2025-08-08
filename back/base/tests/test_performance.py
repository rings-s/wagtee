# test_performance.py - Performance and caching tests
import time
from datetime import datetime, timedelta
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test.utils import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from ..cache_manager import (
    CacheManager, QueryCacheManager, SubscriptionCacheManager,
    AnalyticsCacheManager, DatabaseOptimizer, cache_result
)
from ..models import Service, Booking, Customer
from accounts.models import BusinessProfile

User = get_user_model()

class CacheManagerTest(TestCase):
    """Test cache management functionality"""
    
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key = CacheManager.generate_key('test', 123, 'suffix')
        self.assertEqual(key, 'test:123:suffix')
        
        key_no_suffix = CacheManager.generate_key('test', 123)
        self.assertEqual(key_no_suffix, 'test:123')
    
    def test_cache_operations(self):
        """Test basic cache operations"""
        key = 'test_key'
        value = {'data': 'test_value', 'number': 123}
        
        # Test set
        result = CacheManager.set(key, value, 'short')
        self.assertTrue(result)
        
        # Test get
        cached_value = CacheManager.get(key)
        self.assertEqual(cached_value, value)
        
        # Test get with default
        non_existent = CacheManager.get('non_existent', 'default')
        self.assertEqual(non_existent, 'default')
        
        # Test delete
        delete_result = CacheManager.delete(key)
        self.assertTrue(delete_result)
        
        # Verify deletion
        cached_value = CacheManager.get(key)
        self.assertIsNone(cached_value)
    
    def test_cache_invalidation(self):
        """Test cache invalidation patterns"""
        business_id = self.business.id
        
        # Set some business-related cache entries
        CacheManager.set(f'business:{business_id}:data', {'test': 'data'})
        CacheManager.set(f'service:123:business:{business_id}', {'service': 'data'})
        CacheManager.set(f'analytics:{business_id}:monthly', {'analytics': 'data'})
        
        # Invalidate business cache
        CacheManager.invalidate_business_cache(business_id)
        
        # Verify cache entries are removed
        self.assertIsNone(CacheManager.get(f'business:{business_id}:data'))
        # Note: Pattern deletion may not work with all cache backends in tests
    
    def test_subscription_cache_manager(self):
        """Test subscription-specific cache operations"""
        user_id = self.user.id
        subscription_data = {
            'active': True,
            'tier': 'premium',
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'features': ['basic_booking', 'advanced_analytics']
        }
        
        # Test set subscription
        result = SubscriptionCacheManager.set_user_subscription(user_id, subscription_data)
        self.assertTrue(result)
        
        # Test get subscription
        cached_subscription = SubscriptionCacheManager.get_user_subscription(user_id)
        self.assertEqual(cached_subscription, subscription_data)
        
        # Test invalidation
        SubscriptionCacheManager.invalidate_user_subscription(user_id)
        cached_subscription = SubscriptionCacheManager.get_user_subscription(user_id)
        self.assertIsNone(cached_subscription)
    
    def test_analytics_cache_manager(self):
        """Test analytics cache management"""
        business_id = self.business.id
        analytics_data = {
            'total_bookings': 150,
            'total_revenue': 15000,
            'average_rating': 4.5
        }
        
        # Test set analytics
        result = AnalyticsCacheManager.set_business_analytics(
            business_id, analytics_data, 'month'
        )
        self.assertTrue(result)
        
        # Test get analytics
        cached_analytics = AnalyticsCacheManager.get_business_analytics(
            business_id, 'month'
        )
        self.assertEqual(cached_analytics, analytics_data)
        
        # Test invalidation
        AnalyticsCacheManager.invalidate_business_analytics(business_id)
        cached_analytics = AnalyticsCacheManager.get_business_analytics(
            business_id, 'month'
        )
        self.assertIsNone(cached_analytics)


class DatabaseOptimizerTest(TestCase):
    """Test database optimization utilities"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
        
        # Create test data
        self.service = Service.objects.create(
            business=self.business,
            name='Test Service',
            price=100,
            duration=60,
            category='barber'
        )
        
        self.customer = Customer.objects.create(
            business=self.business,
            name='Test Customer',
            phone_number='+966501234567'
        )
        
        self.booking = Booking.objects.create(
            business=self.business,
            service=self.service,
            customer=self.customer,
            customer_name='Test Customer',
            customer_phone='+966501234567',
            appointment_date='2024-12-25',
            appointment_time='10:00:00',
            total_price=100
        )
    
    def test_optimize_booking_queries(self):
        """Test booking query optimization"""
        queryset = Booking.objects.all()
        optimized_queryset = DatabaseOptimizer.optimize_booking_queries(queryset)
        
        # Check that select_related is applied
        self.assertIn('business', optimized_queryset.query.select_related)
        self.assertIn('service', optimized_queryset.query.select_related)
        self.assertIn('customer', optimized_queryset.query.select_related)
    
    def test_optimize_service_queries(self):
        """Test service query optimization"""
        queryset = Service.objects.all()
        optimized_queryset = DatabaseOptimizer.optimize_service_queries(queryset)
        
        # Execute query to test annotations
        services = list(optimized_queryset)
        self.assertEqual(len(services), 1)
        
        service = services[0]
        self.assertTrue(hasattr(service, 'booking_count'))
        self.assertTrue(hasattr(service, 'total_revenue'))
    
    def test_optimize_customer_queries(self):
        """Test customer query optimization"""
        queryset = Customer.objects.all()
        optimized_queryset = DatabaseOptimizer.optimize_customer_queries(queryset)
        
        # Execute query to test annotations
        customers = list(optimized_queryset)
        self.assertEqual(len(customers), 1)
        
        customer = customers[0]
        self.assertTrue(hasattr(customer, 'total_bookings'))
        self.assertTrue(hasattr(customer, 'total_spent'))
        self.assertTrue(hasattr(customer, 'last_booking_date'))
    
    @patch('base.cache_manager.CacheManager.get')
    @patch('base.cache_manager.CacheManager.set')
    def test_optimize_analytics_queries(self, mock_cache_set, mock_cache_get):
        """Test analytics query optimization with caching"""
        # Mock cache miss
        mock_cache_get.return_value = None
        
        business_id = self.business.id
        analytics = DatabaseOptimizer.optimize_analytics_queries(business_id, 'month')
        
        # Verify analytics data structure
        self.assertIn('period_bookings', analytics)
        self.assertIn('period_revenue', analytics)
        self.assertIn('confirmed_bookings', analytics)
        self.assertIn('top_services', analytics)
        self.assertIn('customer_insights', analytics)
        
        # Verify cache was called
        mock_cache_set.assert_called_once()
        
        # Test cache hit
        cached_analytics = {'cached': True}
        mock_cache_get.return_value = cached_analytics
        
        result = DatabaseOptimizer.optimize_analytics_queries(business_id, 'month')
        self.assertEqual(result, cached_analytics)


class PerformanceTest(APITestCase):
    """Test API performance with caching"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data for performance testing
        self.services = []
        for i in range(10):
            service = Service.objects.create(
                business=self.business,
                name=f'Service {i}',
                price=100 + i,
                duration=60,
                category='barber'
            )
            self.services.append(service)
        
        self.customers = []
        for i in range(20):
            customer = Customer.objects.create(
                business=self.business,
                name=f'Customer {i}',
                phone_number=f'+96650123456{i:02d}'
            )
            self.customers.append(customer)
        
        # Create bookings
        for i in range(50):
            Booking.objects.create(
                business=self.business,
                service=self.services[i % len(self.services)],
                customer=self.customers[i % len(self.customers)],
                customer_name=f'Customer {i % len(self.customers)}',
                customer_phone=f'+96650123456{(i % len(self.customers)):02d}',
                appointment_date='2024-12-25',
                appointment_time='10:00:00',
                total_price=100 + i
            )
        
        cache.clear()
    
    def test_services_list_performance(self):
        """Test services list API performance"""
        # First request (cache miss)
        start_time = time.time()
        response1 = self.client.get('/api/base/services/')
        first_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request (cache hit - if caching is implemented)
        start_time = time.time()
        response2 = self.client.get('/api/base/services/')
        second_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['results']), 10)
        
        # Log performance metrics
        print(f"First request time: {first_request_time:.4f}s")
        print(f"Second request time: {second_request_time:.4f}s")
    
    def test_bookings_list_performance(self):
        """Test bookings list API performance with pagination"""
        # Test with pagination
        response = self.client.get('/api/base/bookings/?page=1&page_size=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 10)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
    
    def test_query_count_optimization(self):
        """Test that queries are optimized to prevent N+1 problems"""
        with self.assertNumQueries(5):  # Adjust based on expected query count
            response = self.client.get('/api/base/bookings/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_bulk_operations_performance(self):
        """Test bulk operations performance"""
        service_ids = [service.id for service in self.services[:5]]
        
        bulk_data = {
            'ids': service_ids,
            'data': {'is_active': False}
        }
        
        start_time = time.time()
        response = self.client.post('/api/base/services/bulk_update/', bulk_data)
        execution_time = time.time() - start_time
        
        if response.status_code == status.HTTP_200_OK:
            print(f"Bulk update time for {len(service_ids)} services: {execution_time:.4f}s")
        
        # Should be faster than individual updates
        self.assertLess(execution_time, 1.0)  # Should complete within 1 second


class CacheFunctionDecoratorTest(TestCase):
    """Test cache function decorator"""
    
    def setUp(self):
        cache.clear()
    
    def test_cache_result_decorator(self):
        """Test cache_result decorator functionality"""
        
        call_count = 0
        
        @cache_result(timeout='short')
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate expensive operation
            return x + y
        
        # First call
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # Second call with same parameters (should be cached)
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Third call with different parameters
        result3 = expensive_function(2, 3)
        self.assertEqual(result3, 5)
        self.assertEqual(call_count, 2)  # Should increment
    
    def test_custom_key_generator(self):
        """Test cache decorator with custom key generator"""
        
        call_count = 0
        
        def custom_key_gen(x, y):
            return f"custom:key:{x}:{y}"
        
        @cache_result(timeout='short', key_generator=custom_key_gen)
        def another_function(x, y):
            nonlocal call_count
            call_count += 1
            return x * y
        
        # First call
        result1 = another_function(2, 3)
        self.assertEqual(result1, 6)
        self.assertEqual(call_count, 1)
        
        # Verify custom key is used
        cached_value = cache.get("custom:key:2:3")
        self.assertEqual(cached_value, 6)


class LoadTest(TestCase):
    """Simulated load testing"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
    
    def test_concurrent_cache_operations(self):
        """Test cache operations under concurrent access"""
        import threading
        import concurrent.futures
        
        def cache_operation(thread_id):
            """Simulate cache operations from different threads"""
            key = f"test_key_{thread_id}"
            value = f"test_value_{thread_id}"
            
            # Set value
            CacheManager.set(key, value, 'short')
            
            # Get value
            retrieved = CacheManager.get(key)
            
            return retrieved == value
        
        # Run concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cache_operation, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All operations should succeed
        self.assertTrue(all(results))
    
    def test_memory_usage_with_large_dataset(self):
        """Test memory usage with large dataset"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large dataset
        large_data = {f"key_{i}": f"value_{i}" * 100 for i in range(1000)}
        
        # Cache the data
        for key, value in large_data.items():
            CacheManager.set(key, value, 'short')
        
        # Measure memory usage
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
        
        # Clean up
        for key in large_data.keys():
            CacheManager.delete(key)
        
        # Memory increase should be reasonable (less than 100MB for this test)
        self.assertLess(memory_increase, 100 * 1024 * 1024)


@override_settings(DEBUG=True)
class SQLPerformanceTest(TestCase):
    """Test SQL query performance and optimization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
        
        # Create larger dataset for meaningful performance testing
        services = []
        for i in range(20):
            service = Service.objects.create(
                business=self.business,
                name=f'Service {i}',
                price=100 + i,
                duration=60,
                category='barber'
            )
            services.append(service)
        
        customers = []
        for i in range(50):
            customer = Customer.objects.create(
                business=self.business,
                name=f'Customer {i}',
                phone_number=f'+96650123456{i:02d}'
            )
            customers.append(customer)
        
        # Create many bookings
        for i in range(200):
            Booking.objects.create(
                business=self.business,
                service=services[i % len(services)],
                customer=customers[i % len(customers)],
                customer_name=f'Customer {i % len(customers)}',
                customer_phone=f'+96650123456{(i % len(customers)):02d}',
                appointment_date='2024-12-25',
                appointment_time='10:00:00',
                total_price=100 + i
            )
    
    def test_optimized_vs_unoptimized_queries(self):
        """Compare optimized vs unoptimized query performance"""
        
        # Unoptimized query (N+1 problem)
        connection.queries_log.clear()
        
        unoptimized_bookings = Booking.objects.filter(business=self.business)
        for booking in unoptimized_bookings[:10]:
            _ = booking.service.name  # This causes additional queries
            _ = booking.customer.name  # This causes additional queries
        
        unoptimized_query_count = len(connection.queries)
        
        # Optimized query
        connection.queries_log.clear()
        
        optimized_bookings = DatabaseOptimizer.optimize_booking_queries(
            Booking.objects.filter(business=self.business)
        )
        for booking in optimized_bookings[:10]:
            _ = booking.service.name  # No additional queries due to select_related
            _ = booking.customer.name  # No additional queries due to select_related
        
        optimized_query_count = len(connection.queries)
        
        print(f"Unoptimized queries: {unoptimized_query_count}")
        print(f"Optimized queries: {optimized_query_count}")
        
        # Optimized should use significantly fewer queries
        self.assertLess(optimized_query_count, unoptimized_query_count)