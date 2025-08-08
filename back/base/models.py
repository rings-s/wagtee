# base/models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Service(models.Model):
    business = models.ForeignKey('accounts.BusinessProfile', on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True, help_text="Arabic description")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.DurationField(help_text="Service duration")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['business', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

class Customer(models.Model):
    """Customer model for walk-in bookings without signup"""
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['phone_number', 'name']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    STATUS_CHOICES_AR = [
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'مؤكد'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
        ('no_show', 'لم يحضر'),
    ]
    
    BOOKING_METHODS = [
        ('online', 'Online'),
        ('walk_in', 'Walk-in'),
        ('phone', 'Phone'),
        ('qr_scan', 'QR Code Scan'),
    ]
    
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True)
    business = models.ForeignKey('accounts.BusinessProfile', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_method = models.CharField(max_length=20, choices=BOOKING_METHODS, default='online')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='booking_qr/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['business', 'appointment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['booking_id']),
        ]

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BusinessHours(models.Model):
    DAYS_OF_WEEK = [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    business = models.ForeignKey('accounts.BusinessProfile', on_delete=models.CASCADE, related_name='hours')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['business', 'day']

class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_reminder', 'Booking Reminder'),
        ('booking_cancellation', 'Booking Cancellation'),
        ('payment_success', 'Payment Success'),
        ('subscription_expiry', 'Subscription Expiry'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_via_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)