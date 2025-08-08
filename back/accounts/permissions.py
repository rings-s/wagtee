from rest_framework import permissions
from .role_manager import RoleManager, Resource, Action
from .subscription_manager import SubscriptionManager


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class RoleBasedPermission(permissions.BasePermission):
    """
    Advanced role-based permission using RoleManager
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get resource and action from view
        resource = getattr(view, 'required_resource', None)
        action = getattr(view, 'required_action', None)
        
        if resource and action:
            return RoleManager.has_permission(request.user, resource, action)
        
        # Default permission check for authenticated users
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if user can access this specific object
        resource_owner = getattr(obj, 'user', None) or getattr(obj, 'business', None)
        if hasattr(resource_owner, 'user'):
            resource_owner = resource_owner.user
        
        resource = getattr(view, 'required_resource', None)
        if resource:
            return RoleManager.can_access_resource(
                request.user, 
                resource, 
                resource_owner
            )
        
        return True


class IsBusinessOwner(permissions.BasePermission):
    """
    Custom permission for business owners only.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'business_owner'
        )


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission for admin and super admin users only.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )


class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission for super admin users only.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'super_admin'
        )


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission for verified users only.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_verified
        )


class IsBusinessOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for business owners and admins.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['business_owner', 'admin', 'super_admin']
        )


class CanManageSubscription(permissions.BasePermission):
    """
    Permission to manage subscriptions - business owners can manage their own,
    admins can manage any.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['business_owner', 'admin', 'super_admin']
        )
    
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'super_admin']:
            return True
        return obj.user == request.user


class SubscriptionRequired(permissions.BasePermission):
    """
    Permission that checks active subscription
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Skip subscription check for admins
        if request.user.role in ['admin', 'super_admin']:
            return True
        
        subscription = SubscriptionManager.get_active_subscription(request.user)
        return subscription['is_active']


class FeaturePermission(permissions.BasePermission):
    """
    Permission that checks subscription feature access
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Skip for admins
        if request.user.role in ['admin', 'super_admin']:
            return True
        
        feature = getattr(view, 'required_feature', None)
        if feature:
            return SubscriptionManager.check_feature_access(request.user, feature)
        
        return True


class BusinessResourcePermission(permissions.BasePermission):
    """
    Permission for business-specific resources with role and subscription checks
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Role-based check
        if hasattr(view, 'required_resource') and hasattr(view, 'required_action'):
            if not RoleManager.has_permission(
                request.user, 
                view.required_resource, 
                view.required_action
            ):
                return False
        
        # Subscription check for business owners
        if request.user.role == 'business_owner':
            subscription_check = SubscriptionManager.enforce_subscription(request.user)
            return subscription_check['allowed']
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check object-level permissions
        resource_owner = getattr(obj, 'user', None)
        if hasattr(obj, 'business') and hasattr(obj.business, 'user'):
            resource_owner = obj.business.user
        
        return RoleManager.can_access_resource(
            request.user,
            getattr(view, 'required_resource', None),
            resource_owner
        )