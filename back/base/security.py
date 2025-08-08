# security.py - Comprehensive security measures for Wagtee platform
import re
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from rest_framework import status
from rest_framework.response import Response
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SecurityValidator:
    """Comprehensive security validation for all inputs"""
    
    # Saudi-specific validation patterns
    SAUDI_PHONE_PATTERN = r'^\+966[0-9]{9}$'
    CR_NUMBER_PATTERN = r'^[1-9][0-9]{9}$'
    VAT_NUMBER_PATTERN = r'^[0-9]{15}$'
    ARABIC_TEXT_PATTERN = r'^[\u0600-\u06FF\s\d\-\.\,\(\)]+$'
    
    # Security patterns
    SQL_INJECTION_PATTERNS = [
        r'(\b(ALTER|CREATE|DELETE|DROP|EXEC|EXECUTE|INSERT|SELECT|UNION|UPDATE)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\-\-|\#|/\*|\*/)',
        r'(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)',
        r'(\<\s*SCRIPT)',
    ]
    
    XSS_PATTERNS = [
        r'<\s*script[^>]*>',
        r'javascript\s*:',
        r'on\w+\s*=',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
    ]
    
    @classmethod
    def validate_saudi_phone(cls, phone: str) -> bool:
        """Validate Saudi phone number format"""
        if not phone:
            return False
        return bool(re.match(cls.SAUDI_PHONE_PATTERN, phone))
    
    @classmethod
    def validate_cr_number(cls, cr_number: str) -> bool:
        """Validate Saudi CR number format"""
        if not cr_number:
            return True  # Optional field
        return bool(re.match(cls.CR_NUMBER_PATTERN, cr_number))
    
    @classmethod
    def validate_vat_number(cls, vat_number: str) -> bool:
        """Validate Saudi VAT number format"""
        if not vat_number:
            return True  # Optional field
        return bool(re.match(cls.VAT_NUMBER_PATTERN, vat_number))
    
    @classmethod
    def validate_arabic_text(cls, text: str) -> bool:
        """Validate Arabic text format"""
        if not text:
            return True  # Optional fields
        return bool(re.match(cls.ARABIC_TEXT_PATTERN, text))
    
    @classmethod
    def sanitize_input(cls, value: str) -> str:
        """Sanitize input to prevent XSS and injection attacks"""
        if not isinstance(value, str):
            return value
        
        # Remove potential XSS patterns
        for pattern in cls.XSS_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Remove potential SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Trim and normalize whitespace
        value = ' '.join(value.split())
        
        return value.strip()
    
    @classmethod
    def validate_business_data(cls, data: Dict) -> Dict[str, str]:
        """Validate business-specific data"""
        errors = {}
        
        # Phone validation
        if 'phone_number' in data:
            if not cls.validate_saudi_phone(data['phone_number']):
                errors['phone_number'] = 'رقم الهاتف يجب أن يكون بالصيغة +966xxxxxxxxx'
        
        # CR number validation
        if 'cr_number' in data:
            if not cls.validate_cr_number(data['cr_number']):
                errors['cr_number'] = 'رقم السجل التجاري يجب أن يكون 10 أرقام'
        
        # VAT number validation
        if 'vat_number' in data:
            if not cls.validate_vat_number(data['vat_number']):
                errors['vat_number'] = 'الرقم الضريبي يجب أن يكون 15 رقم'
        
        # Arabic text validation
        for field in ['business_name_ar', 'description_ar', 'address_ar']:
            if field in data and data[field]:
                if not cls.validate_arabic_text(data[field]):
                    errors[field] = f'{field} يجب أن يحتوي على نص عربي صحيح'
        
        return errors
    
    @classmethod
    def sanitize_bulk_data(cls, data: Dict) -> Dict:
        """Sanitize data for bulk operations"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_input(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = None
            else:
                # For complex types, convert to string and sanitize
                sanitized[key] = cls.sanitize_input(str(value))
        
        return sanitized


class RateLimiter:
    """Advanced rate limiting with different tiers"""
    
    RATE_LIMITS = {
        'login': {'requests': 5, 'window': 300, 'block_duration': 900},  # 5 attempts per 5 min
        'api_general': {'requests': 100, 'window': 60, 'block_duration': 300},  # 100 per minute
        'api_heavy': {'requests': 10, 'window': 60, 'block_duration': 600},  # 10 per minute for heavy ops
        'otp_request': {'requests': 3, 'window': 600, 'block_duration': 1800},  # 3 per 10 min
        'password_reset': {'requests': 3, 'window': 3600, 'block_duration': 3600},  # 3 per hour
    }
    
    @classmethod
    def get_client_ip(cls, request) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    @classmethod
    def get_rate_limit_key(cls, action: str, identifier: str) -> str:
        """Generate rate limit cache key"""
        return f"rate_limit:{action}:{identifier}"
    
    @classmethod
    def is_rate_limited(cls, action: str, identifier: str) -> Tuple[bool, int]:
        """Check if action is rate limited"""
        if action not in cls.RATE_LIMITS:
            return False, 0
        
        config = cls.RATE_LIMITS[action]
        key = cls.get_rate_limit_key(action, identifier)
        
        # Check if blocked
        block_key = f"{key}:blocked"
        if cache.get(block_key):
            return True, config['block_duration']
        
        # Get current count
        current_count = cache.get(key, 0)
        
        if current_count >= config['requests']:
            # Block the identifier
            cache.set(block_key, True, config['block_duration'])
            logger.warning(f"Rate limit exceeded for {action} by {identifier}")
            return True, config['block_duration']
        
        return False, 0
    
    @classmethod
    def increment_counter(cls, action: str, identifier: str):
        """Increment rate limit counter"""
        if action not in cls.RATE_LIMITS:
            return
        
        config = cls.RATE_LIMITS[action]
        key = cls.get_rate_limit_key(action, identifier)
        
        current_count = cache.get(key, 0)
        cache.set(key, current_count + 1, config['window'])


class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Security headers
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        if settings.DEBUG is False:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class AuditLogger:
    """Comprehensive audit logging for security events"""
    
    SECURITY_EVENTS = [
        'LOGIN_SUCCESS',
        'LOGIN_FAILED',
        'LOGIN_BLOCKED',
        'PASSWORD_CHANGE',
        'PASSWORD_RESET',
        'ACCOUNT_LOCKED',
        'PERMISSION_DENIED',
        'DATA_ACCESS',
        'DATA_MODIFICATION',
        'BULK_OPERATION',
        'RATE_LIMIT_EXCEEDED',
        'SUSPICIOUS_ACTIVITY',
    ]
    
    @classmethod
    def log_security_event(cls, event_type: str, user_id: Optional[int], 
                          ip_address: str, details: Dict = None):
        """Log security event"""
        if event_type not in cls.SECURITY_EVENTS:
            logger.warning(f"Unknown security event type: {event_type}")
            return
        
        log_data = {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        
        logger.info(f"SECURITY_EVENT: {log_data}")
        
        # Store in cache for recent events (optional)
        cache_key = f"security_events:{ip_address}"
        events = cache.get(cache_key, [])
        events.append(log_data)
        
        # Keep only last 50 events per IP
        events = events[-50:]
        cache.set(cache_key, events, 86400)  # 24 hours


class SubscriptionSecurity:
    """Security measures for subscription management"""
    
    @classmethod
    def validate_subscription_access(cls, user, required_features: List[str] = None) -> Tuple[bool, str]:
        """Validate subscription access and features"""
        if not hasattr(user, 'subscription_status'):
            return False, "لا يوجد اشتراك نشط"
        
        subscription = user.subscription_status
        
        # Check if subscription is active
        if not subscription.get('active', False):
            return False, "انتهت صلاحية الاشتراك"
        
        # Check expiry date
        expires_at = subscription.get('expires_at')
        if expires_at and timezone.now() > timezone.datetime.fromisoformat(expires_at.replace('Z', '+00:00')):
            return False, "انتهت صلاحية الاشتراك"
        
        # Check required features
        if required_features:
            user_features = subscription.get('features', [])
            missing_features = [f for f in required_features if f not in user_features]
            if missing_features:
                return False, f"الميزة غير متاحة في باقتك الحالية: {', '.join(missing_features)}"
        
        # Check usage limits
        tier = subscription.get('tier', 'basic')
        limits = cls.get_tier_limits(tier)
        
        # Check service limits
        if hasattr(user, 'services') and user.services.count() >= limits['max_services']:
            return False, f"تم الوصول للحد الأقصى من الخدمات ({limits['max_services']})"
        
        # Check monthly booking limits
        current_month_bookings = cls.get_current_month_bookings(user)
        if current_month_bookings >= limits['max_bookings_per_month']:
            return False, f"تم الوصول للحد الأقصى من الحجوزات الشهرية ({limits['max_bookings_per_month']})"
        
        return True, "تم التحقق بنجاح"
    
    @classmethod
    def get_tier_limits(cls, tier: str) -> Dict:
        """Get limits for subscription tier"""
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
                'features': ['basic_booking', 'advanced_analytics', 'whatsapp_notifications']
            },
            'premium': {
                'max_services': -1,  # Unlimited
                'max_bookings_per_month': -1,  # Unlimited
                'max_customers': -1,  # Unlimited
                'features': ['basic_booking', 'advanced_analytics', 'whatsapp_notifications', 'api_access', 'custom_branding']
            }
        }
        return limits.get(tier, limits['basic'])
    
    @classmethod
    def get_current_month_bookings(cls, user) -> int:
        """Get current month booking count for user"""
        if not hasattr(user, 'business_profile'):
            return 0
        
        from datetime import datetime
        from django.db.models import Count
        from .models import Booking
        
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return Booking.objects.filter(
            business=user.business_profile,
            created_at__gte=current_month
        ).count()


class DataEncryption:
    """Data encryption utilities for sensitive information"""
    
    @classmethod
    def hash_sensitive_data(cls, data: str, salt: str = None) -> Tuple[str, str]:
        """Hash sensitive data with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use SHA-256 with salt
        hash_obj = hashlib.sha256()
        hash_obj.update(f"{data}{salt}".encode('utf-8'))
        
        return hash_obj.hexdigest(), salt
    
    @classmethod
    def verify_hash(cls, data: str, hash_value: str, salt: str) -> bool:
        """Verify hashed data"""
        computed_hash, _ = cls.hash_sensitive_data(data, salt)
        return secrets.compare_digest(computed_hash, hash_value)
    
    @classmethod
    def generate_secure_token(cls, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)


# Decorator for rate limiting views
def rate_limit(action: str, per_user: bool = False):
    """Decorator for rate limiting API views"""
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            # Determine identifier
            if per_user and request.user.is_authenticated:
                identifier = str(request.user.id)
            else:
                identifier = RateLimiter.get_client_ip(request)
            
            # Check rate limit
            is_limited, block_duration = RateLimiter.is_rate_limited(action, identifier)
            
            if is_limited:
                AuditLogger.log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    request.user.id if request.user.is_authenticated else None,
                    RateLimiter.get_client_ip(request),
                    {'action': action, 'identifier': identifier}
                )
                
                return Response({
                    'error': 'تم تجاوز الحد المسموح من الطلبات',
                    'retry_after': block_duration
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Increment counter
            RateLimiter.increment_counter(action, identifier)
            
            return view_func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


# Decorator for subscription validation
def require_subscription(features: List[str] = None):
    """Decorator to validate subscription access"""
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({
                    'error': 'يجب تسجيل الدخول أولاً'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            is_valid, message = SubscriptionSecurity.validate_subscription_access(
                request.user, features
            )
            
            if not is_valid:
                AuditLogger.log_security_event(
                    'PERMISSION_DENIED',
                    request.user.id,
                    RateLimiter.get_client_ip(request),
                    {'reason': 'subscription_invalid', 'message': message}
                )
                
                return Response({
                    'error': message,
                    'requires_upgrade': True
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            return view_func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator