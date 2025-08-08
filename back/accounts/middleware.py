# accounts/middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from .subscription_manager import SubscriptionManager
from .role_manager import RoleManager
import logging

logger = logging.getLogger('security')


class SubscriptionEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware to enforce subscription rules across all API endpoints
    """
    
    # Endpoints that require active subscription
    SUBSCRIPTION_REQUIRED_PATHS = [
        '/api/base/services/',
        '/api/base/bookings/',
        '/api/base/customers/',
        '/api/accounts/business-profile/',
    ]
    
    # Endpoints that require premium features
    PREMIUM_REQUIRED_PATHS = [
        '/api/base/analytics/',
        '/api/base/reports/',
        '/api/accounts/business-profile/qr/',
    ]
    
    # Paths to skip subscription check
    EXEMPT_PATHS = [
        '/api/accounts/login/',
        '/api/accounts/token/refresh/',
        '/api/accounts/logout/',
        '/api/accounts/send-otp/',
        '/api/accounts/verify-otp/',
        '/api/accounts/profile/',
        '/api/accounts/subscriptions/',
        '/api/base/public/',  # Public booking endpoints
        '/admin/',
    ]
    
    def process_request(self, request):
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Skip exempt paths
        if any(request.path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            return None
        
        # Skip if user is not authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Skip for admin and super admin users
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'super_admin']:
            return None
        
        # Check subscription requirements
        subscription_check = self._check_subscription_access(request)
        if not subscription_check['allowed']:
            logger.warning(f'Subscription access denied for user {request.user.phone_number} on path {request.path}')
            return JsonResponse({
                'error': subscription_check['message'],
                'error_code': 'SUBSCRIPTION_REQUIRED',
                'subscription_required': subscription_check.get('subscription_required', False),
                'upgrade_url': subscription_check.get('upgrade_url'),
                'current_tier': subscription_check.get('current_tier'),
                'required_tier': subscription_check.get('required_tier'),
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        return None
    
    def _check_subscription_access(self, request):
        """Check if user has required subscription access"""
        path = request.path
        user = request.user
        
        # Check premium features
        if any(path.startswith(premium_path) for premium_path in self.PREMIUM_REQUIRED_PATHS):
            return SubscriptionManager.enforce_subscription(
                user, 
                feature='analytics'  # Premium feature check
            )
        
        # Check basic subscription
        if any(path.startswith(sub_path) for sub_path in self.SUBSCRIPTION_REQUIRED_PATHS):
            subscription = SubscriptionManager.get_active_subscription(user)
            if not subscription['is_active'] and subscription['tier'] == 'trial':
                return {
                    'allowed': False,
                    'message': 'يجب الاشتراك للوصول لهذه الميزة / Subscription required to access this feature',
                    'subscription_required': True,
                    'upgrade_url': '/api/accounts/subscriptions/',
                    'current_tier': 'trial',
                    'required_tier': 'basic'
                }
        
        return {'allowed': True}


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Add CORS headers for API responses
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        
        return response


class AuthenticationLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log authentication events and suspicious activities
    """
    
    SENSITIVE_PATHS = [
        '/api/accounts/login/',
        '/api/accounts/logout/',
        '/api/accounts/verify-otp/',
        '/admin/',
    ]
    
    def process_request(self, request):
        # Log access to sensitive endpoints
        if any(request.path.startswith(path) for path in self.SENSITIVE_PATHS):
            user_info = 'anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"user:{request.user.phone_number}"
            
            logger.info(
                f'Access to sensitive endpoint: {request.path} by {user_info} '
                f'from IP: {self._get_client_ip(request)} '
                f'User-Agent: {request.META.get("HTTP_USER_AGENT", "unknown")}'
            )
        
        return None
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if (request.path.startswith('/api/accounts/login/') and 
            response.status_code in [400, 401, 403]):
            
            logger.warning(
                f'Failed authentication attempt on {request.path} '
                f'from IP: {self._get_client_ip(request)} '
                f'Status: {response.status_code}'
            )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access control
    """
    
    ADMIN_ONLY_PATHS = [
        '/api/admin/',
        '/api/accounts/subscriptions/',  # Subscription management
    ]
    
    SUPER_ADMIN_ONLY_PATHS = [
        '/api/admin/system/',
        '/api/admin/users/',
    ]
    
    def process_request(self, request):
        # Skip if user is not authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        user = request.user
        path = request.path
        
        # Check super admin only paths
        if any(path.startswith(super_path) for super_path in self.SUPER_ADMIN_ONLY_PATHS):
            if not hasattr(user, 'role') or user.role != 'super_admin':
                logger.warning(f'Unauthorized super admin access attempt by {user.phone_number} to {path}')
                return JsonResponse({
                    'error': 'صلاحيات المدير العام مطلوبة / Super admin access required',
                    'error_code': 'INSUFFICIENT_PERMISSIONS',
                    'required_role': 'super_admin',
                    'current_role': getattr(user, 'role', 'unknown')
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check admin only paths
        elif any(path.startswith(admin_path) for admin_path in self.ADMIN_ONLY_PATHS):
            if not hasattr(user, 'role') or user.role not in ['admin', 'super_admin']:
                logger.warning(f'Unauthorized admin access attempt by {user.phone_number} to {path}')
                return JsonResponse({
                    'error': 'صلاحيات الإدارة مطلوبة / Admin access required',
                    'error_code': 'INSUFFICIENT_PERMISSIONS',
                    'required_role': 'admin',
                    'current_role': getattr(user, 'role', 'unknown')
                }, status=status.HTTP_403_FORBIDDEN)
        
        return None