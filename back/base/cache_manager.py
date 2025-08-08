# cache_manager.py - Comprehensive caching and performance optimization
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Advanced cache management with intelligent invalidation"""
    
    # Cache timeout configurations (in seconds)
    CACHE_TIMEOUTS = {
        'short': 300,      # 5 minutes - frequently changing data
        'medium': 1800,    # 30 minutes - moderately changing data
        'long': 3600,      # 1 hour - stable data
        'very_long': 86400 # 24 hours - rarely changing data
    }
    
    # Cache key prefixes
    PREFIXES = {
        'user': 'user',
        'business': 'business',
        'service': 'service',
        'booking': 'booking',
        'customer': 'customer',
        'analytics': 'analytics',
        'subscription': 'subscription',
        'notification': 'notification'
    }
    
    @classmethod
    def generate_key(cls, prefix: str, identifier: Union[str, int], 
                    suffix: str = None) -> str:
        """Generate standardized cache key"""
        key_parts = [prefix, str(identifier)]
        if suffix:
            key_parts.append(suffix)
        return ':'.join(key_parts)
    
    @classmethod
    def generate_query_key(cls, prefix: str, query_params: Dict) -> str:
        """Generate cache key for database queries"""
        # Sort parameters for consistent keys
        sorted_params = sorted(query_params.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        
        # Create hash of parameters to keep key length manageable
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        return f"{prefix}:query:{params_hash}"
    
    @classmethod
    def set(cls, key: str, value: Any, timeout: str = 'medium') -> bool:
        """Set cache value with timeout"""
        timeout_seconds = cls.CACHE_TIMEOUTS.get(timeout, cls.CACHE_TIMEOUTS['medium'])
        try:
            return cache.set(key, value, timeout_seconds)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get cache value"""
        try:
            return cache.get(key, default)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """Delete cache key"""
        try:
            return cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern(pattern)
            else:
                # Fallback for cache backends that don't support pattern deletion
                # This is less efficient but ensures compatibility
                keys_to_delete = []
                if hasattr(cache, '_cache'):  # Django's locmem cache
                    for key in cache._cache.keys():
                        if pattern.replace('*', '') in key:
                            keys_to_delete.append(key)
                
                deleted_count = 0
                for key in keys_to_delete:
                    if cls.delete(key):
                        deleted_count += 1
                
                return deleted_count
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    @classmethod
    def invalidate_business_cache(cls, business_id: int):
        """Invalidate all cache entries for a business"""
        patterns = [
            f"{cls.PREFIXES['business']}:{business_id}:*",
            f"{cls.PREFIXES['service']}:*:business:{business_id}",
            f"{cls.PREFIXES['booking']}:*:business:{business_id}",
            f"{cls.PREFIXES['customer']}:*:business:{business_id}",
            f"{cls.PREFIXES['analytics']}:{business_id}:*"
        ]
        
        for pattern in patterns:
            cls.delete_pattern(pattern)
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"{cls.PREFIXES['user']}:{user_id}:*",
            f"{cls.PREFIXES['subscription']}:{user_id}:*",
            f"{cls.PREFIXES['notification']}:{user_id}:*"
        ]
        
        for pattern in patterns:
            cls.delete_pattern(pattern)


class QueryCacheManager:
    """Manager for caching database queries"""
    
    @classmethod
    def cache_queryset(cls, queryset: QuerySet, cache_key: str, 
                      timeout: str = 'medium') -> List[Dict]:
        """Cache queryset results"""
        # Check if results are already cached
        cached_result = CacheManager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query and serialize results
        try:
            results = list(queryset.values())
            CacheManager.set(cache_key, results, timeout)
            return results
        except Exception as e:
            logger.error(f"Query cache error: {e}")
            return list(queryset.values())
    
    @classmethod
    def cache_analytics_query(cls, business_id: int, query_func, 
                             params: Dict, timeout: str = 'long') -> Dict:
        """Cache analytics query results"""
        cache_key = CacheManager.generate_query_key(
            f"{CacheManager.PREFIXES['analytics']}:{business_id}",
            params
        )
        
        cached_result = CacheManager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            result = query_func(**params)
            CacheManager.set(cache_key, result, timeout)
            return result
        except Exception as e:
            logger.error(f"Analytics cache error: {e}")
            return {}


def cache_result(timeout: str = 'medium', key_generator=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Default key generation
                func_name = f"{func.__module__}.{func.__name__}"
                args_str = str(args) + str(sorted(kwargs.items()))
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                cache_key = f"func:{func_name}:{args_hash}"
            
            # Check cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


class SubscriptionCacheManager:
    """Specialized cache manager for subscription data"""
    
    @classmethod
    def get_user_subscription(cls, user_id: int) -> Optional[Dict]:
        """Get cached user subscription data"""
        cache_key = CacheManager.generate_key(
            CacheManager.PREFIXES['subscription'], 
            user_id
        )
        return CacheManager.get(cache_key)
    
    @classmethod
    def set_user_subscription(cls, user_id: int, subscription_data: Dict) -> bool:
        """Cache user subscription data"""
        cache_key = CacheManager.generate_key(
            CacheManager.PREFIXES['subscription'], 
            user_id
        )
        return CacheManager.set(cache_key, subscription_data, 'long')
    
    @classmethod
    def invalidate_user_subscription(cls, user_id: int):
        """Invalidate user subscription cache"""
        cache_key = CacheManager.generate_key(
            CacheManager.PREFIXES['subscription'], 
            user_id
        )
        CacheManager.delete(cache_key)
    
    @classmethod
    def get_subscription_limits(cls, tier: str) -> Dict:
        """Get cached subscription tier limits"""
        cache_key = f"subscription_limits:{tier}"
        
        cached_limits = CacheManager.get(cache_key)
        if cached_limits is not None:
            return cached_limits
        
        # Default limits if not cached
        limits = {
            'basic': {
                'max_services': 5,
                'max_bookings_per_month': 100,
                'max_customers': 500,
                'features': ['basic_booking', 'basic_analytics']
            },
            'standard': {
                'max_services': 15,
                'max_bookings_per_month': 300,
                'max_customers': 1500,
                'features': ['basic_booking', 'advanced_analytics', 'whatsapp_notifications', 'realtime_updates']
            },
            'premium': {
                'max_services': -1,  # Unlimited
                'max_bookings_per_month': -1,  # Unlimited
                'max_customers': -1,  # Unlimited
                'features': ['basic_booking', 'advanced_analytics', 'whatsapp_notifications', 'realtime_updates', 'api_access', 'custom_branding']
            }
        }
        
        tier_limits = limits.get(tier, limits['basic'])
        CacheManager.set(cache_key, tier_limits, 'very_long')
        
        return tier_limits


class AnalyticsCacheManager:
    """Specialized cache manager for analytics data"""
    
    @classmethod
    def get_business_analytics(cls, business_id: int, period: str = 'month') -> Optional[Dict]:
        """Get cached business analytics"""
        cache_key = CacheManager.generate_key(
            CacheManager.PREFIXES['analytics'],
            business_id,
            period
        )
        return CacheManager.get(cache_key)
    
    @classmethod
    def set_business_analytics(cls, business_id: int, analytics_data: Dict, 
                             period: str = 'month') -> bool:
        """Cache business analytics data"""
        cache_key = CacheManager.generate_key(
            CacheManager.PREFIXES['analytics'],
            business_id,
            period
        )
        return CacheManager.set(cache_key, analytics_data, 'long')
    
    @classmethod
    def invalidate_business_analytics(cls, business_id: int):
        """Invalidate all analytics cache for a business"""
        pattern = f"{CacheManager.PREFIXES['analytics']}:{business_id}:*"
        CacheManager.delete_pattern(pattern)


# Signal handlers for automatic cache invalidation
@receiver(post_save)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """Automatically invalidate relevant cache on model save"""
    model_name = sender.__name__.lower()
    
    # Business-related models
    if hasattr(instance, 'business_id'):
        CacheManager.invalidate_business_cache(instance.business_id)
    elif hasattr(instance, 'business') and hasattr(instance.business, 'id'):
        CacheManager.invalidate_business_cache(instance.business.id)
    
    # User-related models
    if hasattr(instance, 'user_id'):
        CacheManager.invalidate_user_cache(instance.user_id)
    elif hasattr(instance, 'user') and hasattr(instance.user, 'id'):
        CacheManager.invalidate_user_cache(instance.user.id)
    
    # Model-specific invalidation
    if model_name == 'booking':
        # Invalidate analytics cache when bookings change
        if hasattr(instance, 'business') and hasattr(instance.business, 'id'):
            AnalyticsCacheManager.invalidate_business_analytics(instance.business.id)
    
    elif model_name == 'subscription':
        # Invalidate subscription cache
        if hasattr(instance, 'user_id'):
            SubscriptionCacheManager.invalidate_user_subscription(instance.user_id)


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Automatically invalidate relevant cache on model delete"""
    # Use same logic as save signal
    invalidate_cache_on_save(sender, instance, **kwargs)


class DatabaseOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_booking_queries(queryset):
        """Optimize booking-related queries"""
        return queryset.select_related(
            'business', 'service', 'customer'
        ).prefetch_related(
            'reviews'
        )
    
    @staticmethod
    def optimize_service_queries(queryset):
        """Optimize service-related queries"""
        return queryset.select_related('business').annotate(
            booking_count=Count('bookings'),
            total_revenue=Sum('bookings__total_price')
        )
    
    @staticmethod
    def optimize_customer_queries(queryset):
        """Optimize customer-related queries"""
        return queryset.annotate(
            total_bookings=Count('bookings'),
            total_spent=Sum('bookings__total_price'),
            last_booking_date=Max('bookings__appointment_date')
        )
    
    @staticmethod
    def optimize_analytics_queries(business_id: int, period: str = 'month'):
        """Optimize analytics queries with caching"""
        from .models import Booking, Service, Customer
        from django.db.models import Count, Sum, Avg
        
        # Define date range
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Cache key for analytics
        cache_key = f"analytics:{business_id}:{period}:{start_date.date()}"
        
        # Check cache first
        cached_data = CacheManager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Execute optimized queries
        base_bookings = Booking.objects.filter(
            business_id=business_id,
            created_at__gte=start_date
        )
        
        analytics_data = {
            'period_bookings': base_bookings.count(),
            'period_revenue': base_bookings.aggregate(
                total=Sum('total_price')
            )['total'] or 0,
            'confirmed_bookings': base_bookings.filter(status='confirmed').count(),
            'completed_bookings': base_bookings.filter(status='completed').count(),
            'cancelled_bookings': base_bookings.filter(status='cancelled').count(),
            'pending_bookings': base_bookings.filter(status='pending').count(),
            'average_booking_value': base_bookings.aggregate(
                avg=Avg('total_price')
            )['avg'] or 0,
            'top_services': list(
                Service.objects.filter(business_id=business_id)
                .annotate(
                    booking_count=Count('bookings', filter=Q(bookings__created_at__gte=start_date)),
                    revenue=Sum('bookings__total_price', filter=Q(bookings__created_at__gte=start_date))
                )
                .order_by('-booking_count')[:5]
                .values('name', 'booking_count', 'revenue')
            ),
            'customer_insights': {
                'new_customers': Customer.objects.filter(
                    business_id=business_id,
                    created_at__gte=start_date
                ).count(),
                'repeat_customers': base_bookings.values('customer').distinct().count()
            }
        }
        
        # Cache the results
        CacheManager.set(cache_key, analytics_data, 'long')
        
        return analytics_data