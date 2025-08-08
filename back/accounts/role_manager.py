from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Action(Enum):
    """Available actions in the system"""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'
    MANAGE = 'manage'
    ANALYTICS = 'analytics'
    EXPORT = 'export'
    BULK_OPERATIONS = 'bulk_operations'
    SYSTEM_CONFIG = 'system_config'


class Resource(Enum):
    """Available resources in the system"""
    # Business Resources
    BUSINESS_PROFILE = 'business_profile'
    SERVICES = 'services'
    BUSINESS_HOURS = 'business_hours'
    
    # Booking Resources
    BOOKINGS = 'bookings'
    CUSTOMERS = 'customers'
    REVIEWS = 'reviews'
    
    # System Resources
    USERS = 'users'
    SUBSCRIPTIONS = 'subscriptions'
    NOTIFICATIONS = 'notifications'
    
    # Admin Resources
    SYSTEM_SETTINGS = 'system_settings'
    AUDIT_LOGS = 'audit_logs'
    REPORTS = 'reports'


class RoleManager:
    """Advanced role-based access control manager"""
    
    # Role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        'business_owner': 1,
        'admin': 2,
        'super_admin': 3
    }
    
    # Comprehensive role permissions matrix
    ROLE_PERMISSIONS = {
        'business_owner': {
            # Own business resources - full access
            Resource.BUSINESS_PROFILE: [Action.READ, Action.UPDATE],
            Resource.SERVICES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
            Resource.BUSINESS_HOURS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
            
            # Own bookings - full access
            Resource.BOOKINGS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ANALYTICS],
            Resource.CUSTOMERS: [Action.READ, Action.UPDATE],  # Only customers who booked with them
            Resource.REVIEWS: [Action.READ],  # Only reviews for their business
            
            # Limited system access
            Resource.NOTIFICATIONS: [Action.READ, Action.UPDATE],  # Own notifications only
            Resource.SUBSCRIPTIONS: [Action.READ],  # Own subscription only
            
            # Restricted actions
            Resource.USERS: [],  # Cannot manage other users
            Resource.SYSTEM_SETTINGS: [],
            Resource.AUDIT_LOGS: [],
            Resource.REPORTS: [Action.READ],  # Own business reports only
        },
        
        'admin': {
            # All business resources - full access to multiple businesses
            Resource.BUSINESS_PROFILE: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
            Resource.SERVICES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.BULK_OPERATIONS],
            Resource.BUSINESS_HOURS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.BULK_OPERATIONS],
            
            # All bookings - full access across businesses
            Resource.BOOKINGS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ANALYTICS, Action.EXPORT],
            Resource.CUSTOMERS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.EXPORT],
            Resource.REVIEWS: [Action.READ, Action.UPDATE, Action.DELETE, Action.ANALYTICS],
            
            # User management
            Resource.USERS: [Action.CREATE, Action.READ, Action.UPDATE],  # Cannot delete users
            Resource.SUBSCRIPTIONS: [Action.CREATE, Action.READ, Action.UPDATE, Action.MANAGE],
            Resource.NOTIFICATIONS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
            
            # Limited system access
            Resource.SYSTEM_SETTINGS: [Action.READ],  # Read-only system settings
            Resource.AUDIT_LOGS: [Action.READ],
            Resource.REPORTS: [Action.READ, Action.ANALYTICS, Action.EXPORT],
        },
        
        'super_admin': {
            # Full system access
            Resource.BUSINESS_PROFILE: [action for action in Action],
            Resource.SERVICES: [action for action in Action],
            Resource.BUSINESS_HOURS: [action for action in Action],
            Resource.BOOKINGS: [action for action in Action],
            Resource.CUSTOMERS: [action for action in Action],
            Resource.REVIEWS: [action for action in Action],
            Resource.USERS: [action for action in Action],
            Resource.SUBSCRIPTIONS: [action for action in Action],
            Resource.NOTIFICATIONS: [action for action in Action],
            Resource.SYSTEM_SETTINGS: [action for action in Action],
            Resource.AUDIT_LOGS: [action for action in Action],
            Resource.REPORTS: [action for action in Action],
        }
    }
    
    @classmethod
    def has_permission(cls, user, resource: Resource, action: Action, target_user=None) -> bool:
        """
        Check if user has permission for specific resource and action
        
        Args:
            user: User object
            resource: Resource enum
            action: Action enum
            target_user: Target user for cross-user operations
            
        Returns:
            bool: True if permission granted
        """
        if not user or not user.is_authenticated:
            return False
        
        # Cache key for permission check
        cache_key = f'permission_{user.id}_{resource.value}_{action.value}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        user_role = getattr(user, 'role', 'business_owner')
        
        # Get role permissions
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role, {})
        allowed_actions = role_permissions.get(resource, [])
        
        # Check basic permission
        has_basic_permission = action in allowed_actions
        
        # Additional checks for cross-user operations
        if has_basic_permission and target_user:
            has_basic_permission = cls._check_cross_user_permission(
                user, target_user, resource, action
            )
        
        # Cache result for 5 minutes
        cache.set(cache_key, has_basic_permission, 300)
        return has_basic_permission
    
    @classmethod
    def _check_cross_user_permission(cls, user, target_user, resource: Resource, action: Action) -> bool:
        """Check permissions for operations involving other users"""
        user_hierarchy = cls.ROLE_HIERARCHY.get(user.role, 0)
        target_hierarchy = cls.ROLE_HIERARCHY.get(target_user.role, 0)
        
        # Business owners can only access their own data
        if user.role == 'business_owner':
            return user.id == target_user.id
        
        # Admins can manage business owners but not other admins/super_admins
        if user.role == 'admin':
            if target_user.role == 'business_owner':
                return True
            return user.id == target_user.id
        
        # Super admins can manage everyone
        if user.role == 'super_admin':
            return True
        
        return False
    
    @classmethod
    def get_user_permissions(cls, user) -> dict:
        """Get all permissions for a user"""
        if not user or not user.is_authenticated:
            return {}
        
        cache_key = f'user_permissions_{user.id}'
        cached_permissions = cache.get(cache_key)
        if cached_permissions:
            return cached_permissions
        
        user_role = getattr(user, 'role', 'business_owner')
        permissions = cls.ROLE_PERMISSIONS.get(user_role, {})
        
        # Convert to serializable format
        serializable_permissions = {}
        for resource, actions in permissions.items():
            serializable_permissions[resource.value] = [action.value for action in actions]
        
        # Cache for 10 minutes
        cache.set(cache_key, serializable_permissions, 600)
        return serializable_permissions
    
    @classmethod
    def can_access_resource(cls, user, resource: Resource, resource_owner=None) -> bool:
        """Check if user can access a specific resource instance"""
        if not user or not user.is_authenticated:
            return False
        
        # Super admins can access everything
        if user.role == 'super_admin':
            return True
        
        # Admins can access most resources except super admin data
        if user.role == 'admin':
            if resource_owner and hasattr(resource_owner, 'role'):
                return resource_owner.role != 'super_admin'
            return True
        
        # Business owners can only access their own resources
        if user.role == 'business_owner':
            if resource_owner:
                return user.id == resource_owner.id
            return True
        
        return False
    
    @classmethod
    def filter_queryset_by_role(cls, user, queryset, user_field='user'):
        """Filter queryset based on user role and permissions"""
        if not user or not user.is_authenticated:
            return queryset.none()
        
        # Super admins see everything
        if user.role == 'super_admin':
            return queryset
        
        # Admins see all business owner data
        if user.role == 'admin':
            if hasattr(queryset.model, user_field):
                return queryset.exclude(**{f'{user_field}__role': 'super_admin'})
            return queryset
        
        # Business owners see only their own data
        if user.role == 'business_owner':
            if hasattr(queryset.model, user_field):
                return queryset.filter(**{user_field: user})
            elif hasattr(queryset.model, 'business'):
                try:
                    return queryset.filter(business=user.business_profile)
                except:
                    return queryset.none()
        
        return queryset.none()
    
    @classmethod
    def invalidate_user_cache(cls, user):
        """Invalidate all cached permissions for a user"""
        cache_patterns = [
            f'permission_{user.id}_*',
            f'user_permissions_{user.id}',
        ]
        
        for pattern in cache_patterns:
            cache.delete(pattern)


class RolePermissionMixin:
    """Mixin for views that need role-based permission checking"""
    
    required_resource = None
    required_action = None
    
    def check_role_permission(self, resource=None, action=None, target_user=None):
        """Check role-based permission"""
        if not self.request.user.is_authenticated:
            return False
        
        resource = resource or self.required_resource
        action = action or self.required_action
        
        if not resource or not action:
            return False
        
        return RoleManager.has_permission(
            self.request.user,
            resource,
            action,
            target_user
        )
    
    def filter_queryset(self, queryset):
        """Apply role-based filtering to queryset"""
        return RoleManager.filter_queryset_by_role(
            self.request.user,
            queryset
        )


def require_permission(resource: Resource, action: Action):
    """Decorator for function-based views requiring specific permissions"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not RoleManager.has_permission(request.user, resource, action):
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'Permission denied',
                    'required_permission': f'{action.value} {resource.value}',
                    'error_code': 'PERMISSION_DENIED'
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator