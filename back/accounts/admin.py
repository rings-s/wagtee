from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BusinessProfile, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_verified', 'subscription_active', 'created_at')
    list_filter = ('role', 'is_verified', 'subscription_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'business_name', 'cr_number', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Business info', {'fields': ('role', 'business_name', 'cr_number', 'vat_number', 'city', 'district')}),
        ('Subscription', {'fields': ('subscription_tier', 'subscription_active', 'subscription_expires')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'phone_number'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'rating', 'is_active')
    list_filter = ('service_type', 'is_active', 'rating')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__business_name', 'description')
    readonly_fields = ('rating', 'qr_code')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'service_type', 'description', 'description_ar')}),
        ('Location', {'fields': ('address', 'address_ar', 'latitude', 'longitude')}),
        ('Settings', {'fields': ('working_hours', 'images', 'is_active')}),
        ('Statistics', {'fields': ('rating', 'qr_code')}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'price', 'is_active', 'start_date', 'end_date')
    list_filter = ('tier', 'is_active', 'start_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__business_name')
    date_hierarchy = 'start_date'
