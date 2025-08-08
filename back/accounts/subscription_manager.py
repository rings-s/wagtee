from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import User, Subscription
import logging

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Advanced subscription management and enforcement system"""
    
    # Subscription tier limits
    TIER_LIMITS = {
        'basic': {
            'max_services': 5,
            'max_bookings_per_month': 50,
            'max_customers': 100,
            'whatsapp_reminders': True,
            'analytics': False,
            'priority_support': False,
            'custom_branding': False,
        },
        'standard': {
            'max_services': 15,
            'max_bookings_per_month': 200,
            'max_customers': 500,
            'whatsapp_reminders': True,
            'analytics': True,
            'priority_support': False,
            'custom_branding': True,
        },
        'premium': {
            'max_services': -1,  # Unlimited
            'max_bookings_per_month': -1,  # Unlimited
            'max_customers': -1,  # Unlimited
            'whatsapp_reminders': True,
            'analytics': True,
            'priority_support': True,
            'custom_branding': True,
        }
    }
    
    @classmethod
    def get_active_subscription(cls, user: User) -> dict:
        """Get user's active subscription with caching"""
        cache_key = f'subscription_{user.id}'
        cached_subscription = cache.get(cache_key)
        
        if cached_subscription:
            return cached_subscription
        
        try:
            subscription = Subscription.objects.filter(
                user=user,
                is_active=True,
                end_date__gt=timezone.now()
            ).first()
            
            if subscription:
                subscription_data = {
                    'tier': subscription.tier,
                    'is_active': True,
                    'end_date': subscription.end_date,
                    'limits': cls.TIER_LIMITS.get(subscription.tier, cls.TIER_LIMITS['basic'])
                }
            else:
                # No active subscription - grace period or trial
                subscription_data = {
                    'tier': 'trial',
                    'is_active': False,
                    'end_date': None,
                    'limits': {
                        'max_services': 2,
                        'max_bookings_per_month': 10,
                        'max_customers': 20,
                        'whatsapp_reminders': False,
                        'analytics': False,
                        'priority_support': False,
                        'custom_branding': False,
                    }
                }
            
            # Cache for 1 hour
            cache.set(cache_key, subscription_data, 3600)
            return subscription_data
            
        except Exception as e:
            logger.error(f"Subscription check failed for user {user.id}: {str(e)}")
            return cls._get_trial_subscription()
    
    @classmethod
    def _get_trial_subscription(cls) -> dict:
        """Return trial subscription limits"""
        return {
            'tier': 'trial',
            'is_active': False,
            'end_date': None,
            'limits': cls.TIER_LIMITS.get('trial', {
                'max_services': 2,
                'max_bookings_per_month': 10,
                'max_customers': 20,
                'whatsapp_reminders': False,
                'analytics': False,
                'priority_support': False,
                'custom_branding': False,
            })
        }
    
    @classmethod
    def check_feature_access(cls, user: User, feature: str) -> bool:
        """Check if user has access to specific feature"""
        subscription = cls.get_active_subscription(user)
        return subscription['limits'].get(feature, False)
    
    @classmethod
    def check_limit(cls, user: User, limit_type: str, current_count: int = None) -> dict:
        """
        Check if user is within subscription limits
        
        Returns:
            dict: {
                'allowed': bool,
                'limit': int,
                'current': int,
                'remaining': int,
                'message': str
            }
        """
        subscription = cls.get_active_subscription(user)
        limit = subscription['limits'].get(limit_type, 0)
        
        # Unlimited access
        if limit == -1:
            return {
                'allowed': True,
                'limit': -1,
                'current': current_count or 0,
                'remaining': -1,
                'message': 'Unlimited access'
            }
        
        # Get current count if not provided
        if current_count is None:
            current_count = cls._get_current_usage(user, limit_type)
        
        allowed = current_count < limit
        remaining = max(0, limit - current_count)
        
        return {
            'allowed': allowed,
            'limit': limit,
            'current': current_count,
            'remaining': remaining,
            'message': f'Using {current_count}/{limit}' if allowed else f'Limit exceeded: {current_count}/{limit}'
        }
    
    @classmethod
    def _get_current_usage(cls, user: User, limit_type: str) -> int:
        """Get current usage count for specific limit type"""
        try:
            business_profile = user.business_profile
            
            if limit_type == 'max_services':
                from base.models import Service
                return Service.objects.filter(business=business_profile, is_active=True).count()
            
            elif limit_type == 'max_bookings_per_month':
                from base.models import Booking
                now = timezone.now()
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                return Booking.objects.filter(
                    business=business_profile,
                    created_at__gte=month_start
                ).count()
            
            elif limit_type == 'max_customers':
                from base.models import Customer, Booking
                return Customer.objects.filter(
                    booking__business=business_profile
                ).distinct().count()
            
            return 0
            
        except Exception as e:
            logger.error(f"Usage calculation failed for {limit_type}: {str(e)}")
            return 0
    
    @classmethod
    def enforce_subscription(cls, user: User, feature: str = None, limit_type: str = None) -> dict:
        """
        Enforce subscription rules
        
        Returns:
            dict: {
                'allowed': bool,
                'message': str,
                'subscription_required': bool,
                'upgrade_url': str
            }
        """
        subscription = cls.get_active_subscription(user)
        
        # Check if subscription is expired
        if not subscription['is_active'] and subscription['tier'] != 'trial':
            return {
                'allowed': False,
                'message': 'Your subscription has expired. Please renew to continue using Wagtee.',
                'subscription_required': True,
                'upgrade_url': '/api/accounts/subscriptions/'
            }
        
        # Check feature access
        if feature and not subscription['limits'].get(feature, False):
            tier_name = subscription['tier'].title()
            return {
                'allowed': False,
                'message': f'This feature is not available in your {tier_name} plan. Please upgrade.',
                'subscription_required': False,
                'upgrade_url': '/api/accounts/subscriptions/'
            }
        
        # Check usage limits
        if limit_type:
            limit_check = cls.check_limit(user, limit_type)
            if not limit_check['allowed']:
                return {
                    'allowed': False,
                    'message': f'{limit_check["message"]}. Please upgrade your plan.',
                    'subscription_required': False,
                    'upgrade_url': '/api/accounts/subscriptions/'
                }
        
        return {
            'allowed': True,
            'message': 'Access granted',
            'subscription_required': False,
            'upgrade_url': None
        }
    
    @classmethod
    def get_subscription_status(cls, user: User) -> dict:
        """Get comprehensive subscription status"""
        subscription = cls.get_active_subscription(user)
        
        # Calculate usage
        usage = {}
        for limit_type in ['max_services', 'max_bookings_per_month', 'max_customers']:
            usage[limit_type] = cls.check_limit(user, limit_type)
        
        # Calculate days until expiry
        days_until_expiry = None
        if subscription['end_date']:
            days_until_expiry = (subscription['end_date'] - timezone.now()).days
        
        return {
            'subscription': subscription,
            'usage': usage,
            'days_until_expiry': days_until_expiry,
            'needs_payment': not subscription['is_active'],
            'features': subscription['limits']
        }
    
    @classmethod
    def invalidate_cache(cls, user: User):
        """Invalidate subscription cache for user"""
        cache_key = f'subscription_{user.id}'
        cache.delete(cache_key)


class SubscriptionEnforcementMixin:
    """Mixin for views that need subscription enforcement"""
    
    subscription_feature = None
    subscription_limit = None
    
    def check_subscription_access(self):
        """Check if user has subscription access"""
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return {'allowed': False, 'message': 'Authentication required'}
        
        # Skip for admins and super admins
        if self.request.user.role in ['admin', 'super_admin']:
            return {'allowed': True, 'message': 'Admin access'}
        
        return SubscriptionManager.enforce_subscription(
            self.request.user,
            feature=self.subscription_feature,
            limit_type=self.subscription_limit
        )
    
    def dispatch(self, request, *args, **kwargs):
        access_check = self.check_subscription_access()
        
        if not access_check['allowed']:
            from rest_framework.response import Response
            from rest_framework import status
            
            return Response({
                'error': access_check['message'],
                'subscription_required': access_check.get('subscription_required', False),
                'upgrade_url': access_check.get('upgrade_url'),
                'error_code': 'SUBSCRIPTION_REQUIRED'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        return super().dispatch(request, *args, **kwargs)