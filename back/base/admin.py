from django.contrib import admin
from .models import Service, Customer, Booking, Review, BusinessHours, Notification


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'price', 'duration', 'is_active', 'created_at')
    list_filter = ('is_active', 'business__service_type', 'created_at')
    search_fields = ('name', 'name_ar', 'business__user__business_name')
    readonly_fields = ('created_at',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'created_at')
    search_fields = ('name', 'phone_number', 'email')
    readonly_fields = ('created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'business', 'customer', 'service', 'appointment_date', 'status', 'total_price')
    list_filter = ('status', 'booking_method', 'appointment_date', 'created_at')
    search_fields = ('booking_id', 'customer__name', 'customer__phone_number', 'business__user__business_name')
    date_hierarchy = 'appointment_date'
    readonly_fields = ('booking_id', 'qr_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Booking Info', {'fields': ('booking_id', 'business', 'service', 'customer')}),
        ('Appointment', {'fields': ('appointment_date', 'appointment_time', 'status', 'booking_method')}),
        ('Payment', {'fields': ('total_price',)}),
        ('Additional Info', {'fields': ('notes', 'reminder_sent', 'qr_code')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('booking__customer__name', 'comment')
    readonly_fields = ('created_at',)


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('business', 'day', 'open_time', 'close_time', 'is_closed')
    list_filter = ('day', 'is_closed')
    search_fields = ('business__user__business_name',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'sent_via_whatsapp', 'created_at')
    search_fields = ('title', 'message', 'user__phone_number', 'customer__name')
    readonly_fields = ('created_at',)
