# base/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from datetime import timedelta
from .models import Service, Customer, Booking, Review, BusinessHours, Notification
from accounts.models import BusinessProfile

User = get_user_model()


# ============================================================================
# Base Nested Serializers - Following DRF Best Practices
# ============================================================================

class BusinessProfileNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for BusinessProfile - read-only"""
    business_name = serializers.CharField(source='user.business_name', read_only=True)
    business_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'business_name', 'service_type', 'business_type_display',
            'description', 'description_ar', 'address', 'address_ar', 'rating'
        ]
        read_only_fields = fields


class UserNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for User - read-only"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'business_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class ServiceNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Service - read-only for relationships"""
    duration_formatted = serializers.SerializerMethodField()
    price_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'name_ar', 'description', 'description_ar',
            'price', 'price_formatted', 'duration', 'duration_formatted'
        ]
        read_only_fields = fields
    
    def get_duration_formatted(self, obj):
        """Format duration as 'HH:MM' for frontend display"""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"
    
    def get_price_formatted(self, obj):
        """Format price with SAR currency"""
        return f"{obj.price} SAR"


class CustomerNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for Customer - read-only for relationships"""
    phone_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'phone_formatted', 'email']
        read_only_fields = fields
    
    def get_phone_formatted(self, obj):
        """Format Saudi phone number for display"""
        if obj.phone_number and obj.phone_number.startswith('+966'):
            return f"({obj.phone_number[4:7]}) {obj.phone_number[7:10]}-{obj.phone_number[10:]}"
        return obj.phone_number


# ============================================================================
# Main Model Serializers
# ============================================================================

class ServiceSerializer(serializers.ModelSerializer):
    """Main Service serializer with nested business information"""
    business = BusinessProfileNestedSerializer(read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    price_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'business', 'name', 'name_ar', 'description', 'description_ar',
            'price', 'price_formatted', 'duration', 'duration_formatted',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'business']
    
    def get_duration_formatted(self, obj):
        """Format duration as 'HH:MM' for frontend display"""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"
    
    def get_price_formatted(self, obj):
        """Format price with SAR currency"""
        return f"{obj.price} SAR"
    
    def create(self, validated_data):
        """Automatically set business from request user"""
        user = self.context['request'].user
        try:
            business_profile = user.business_profile
            validated_data['business'] = business_profile
        except BusinessProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"business": "User must have a business profile to create services"}
            )
        return super().create(validated_data)


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for service creation/updates with duration handling"""
    duration_hours = serializers.IntegerField(write_only=True, required=False, min_value=0, max_value=24)
    duration_minutes = serializers.IntegerField(write_only=True, required=False, min_value=0, max_value=59)
    
    class Meta:
        model = Service
        fields = [
            'name', 'name_ar', 'description', 'description_ar', 'price',
            'duration', 'duration_hours', 'duration_minutes', 'is_active'
        ]
    
    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate(self, attrs):
        """Handle duration conversion from hours/minutes to timedelta"""
        hours = attrs.pop('duration_hours', None)
        minutes = attrs.pop('duration_minutes', None)
        
        if hours is not None or minutes is not None:
            total_minutes = (hours or 0) * 60 + (minutes or 0)
            if total_minutes == 0:
                raise serializers.ValidationError(
                    {"duration": "Service duration must be greater than 0 minutes"}
                )
            attrs['duration'] = timedelta(minutes=total_minutes)
        elif 'duration' not in attrs:
            raise serializers.ValidationError(
                {"duration": "Either provide duration or duration_hours/duration_minutes"}
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create service with business from request user"""
        user = self.context['request'].user
        try:
            business_profile = user.business_profile
            validated_data['business'] = business_profile
        except BusinessProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"business": "User must have a business profile to create services"}
            )
        return super().create(validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    """Customer serializer with enhanced validation"""
    phone_formatted = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'phone_number', 'phone_formatted', 'name', 'email',
            'total_bookings', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_bookings']
    
    def get_phone_formatted(self, obj):
        """Format Saudi phone number for display"""
        if obj.phone_number and obj.phone_number.startswith('+966'):
            return f"({obj.phone_number[4:7]}) {obj.phone_number[7:10]}-{obj.phone_number[10:]}"
        return obj.phone_number
    
    def get_total_bookings(self, obj):
        """Get total bookings count for this customer"""
        if hasattr(obj, '_prefetched_total_bookings'):
            return obj._prefetched_total_bookings
        return obj.booking_set.count()
    
    def validate_phone_number(self, value):
        """Saudi phone number validation"""
        if not value.startswith('+966') or len(value) != 13:
            raise serializers.ValidationError(
                "Phone number must be in Saudi format: +966xxxxxxxxx"
            )
        if not value[4:].isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits after country code"
            )
        return value


class CustomerDetailSerializer(CustomerSerializer):
    """Detailed customer serializer with analytics"""
    total_spent = serializers.SerializerMethodField()
    last_booking_date = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    booking_frequency = serializers.SerializerMethodField()
    favorite_services = serializers.SerializerMethodField()
    
    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + [
            'total_spent', 'last_booking_date', 'average_rating',
            'booking_frequency', 'favorite_services'
        ]
    
    def get_total_spent(self, obj):
        """Calculate total amount spent by customer"""
        if hasattr(obj, '_prefetched_total_spent'):
            return obj._prefetched_total_spent
        return obj.booking_set.filter(status='completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
    
    def get_last_booking_date(self, obj):
        """Get date of last booking"""
        if hasattr(obj, '_prefetched_last_booking'):
            return obj._prefetched_last_booking
        last_booking = obj.booking_set.order_by('-created_at').first()
        return last_booking.created_at if last_booking else None
    
    def get_average_rating(self, obj):
        """Calculate average rating from reviews"""
        if hasattr(obj, '_prefetched_avg_rating'):
            return obj._prefetched_avg_rating
        avg = obj.booking_set.filter(
            review__isnull=False
        ).aggregate(avg_rating=Avg('review__rating'))['avg_rating']
        return round(avg, 2) if avg else None
    
    def get_booking_frequency(self, obj):
        """Calculate booking frequency (bookings per month)"""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        total_bookings = obj.booking_set.count()
        if total_bookings == 0:
            return 0
        
        first_booking = obj.booking_set.order_by('created_at').first()
        if not first_booking:
            return 0
        
        # Calculate months between first booking and now
        months_active = max(1, (
            timezone.now().date() - first_booking.created_at.date()
        ).days / 30.44)  # Average days per month
        
        return round(total_bookings / months_active, 2)
    
    def get_favorite_services(self, obj):
        """Get customer's most booked services"""
        services = obj.booking_set.values(
            'service__name', 'service__name_ar'
        ).annotate(
            count=Count('service')
        ).order_by('-count')[:3]
        
        return [
            {
                'service_name': s['service__name'],
                'service_name_ar': s['service__name_ar'],
                'booking_count': s['count']
            } for s in services
        ]


class BookingSerializer(serializers.ModelSerializer):
    """Main Booking serializer with nested relationships"""
    customer = CustomerNestedSerializer(read_only=True)
    service = ServiceNestedSerializer(read_only=True)
    business = BusinessProfileNestedSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    booking_method_display = serializers.CharField(source='get_booking_method_display', read_only=True)
    appointment_datetime = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'business', 'service', 'customer',
            'appointment_date', 'appointment_time', 'appointment_datetime',
            'status', 'status_display', 'booking_method', 'booking_method_display',
            'total_price', 'notes', 'reminder_sent', 'qr_code',
            'can_cancel', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'booking_id', 'business', 'qr_code',
            'created_at', 'updated_at', 'can_cancel'
        ]
    
    def get_appointment_datetime(self, obj):
        """Combine date and time for frontend convenience"""
        from datetime import datetime
        if obj.appointment_date and obj.appointment_time:
            return datetime.combine(obj.appointment_date, obj.appointment_time)
        return None
    
    def get_can_cancel(self, obj):
        """Check if booking can still be cancelled"""
        from django.utils import timezone
        from datetime import datetime
        
        if obj.status not in ['pending', 'confirmed']:
            return False
        
        # Can cancel up to 2 hours before appointment
        appointment_datetime = datetime.combine(obj.appointment_date, obj.appointment_time)
        cancellation_deadline = appointment_datetime - timedelta(hours=2)
        
        return timezone.now() < timezone.make_aware(cancellation_deadline)


class BookingCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for booking creation with customer handling"""
    # Customer fields for creation/lookup
    customer_phone = serializers.CharField(max_length=15, write_only=True)
    customer_name = serializers.CharField(max_length=255, write_only=True)
    customer_email = serializers.EmailField(required=False, write_only=True, allow_blank=True)
    
    # Configuration options
    auto_confirm = serializers.BooleanField(default=False, write_only=True)
    
    # Read-only nested data for response
    customer = CustomerNestedSerializer(read_only=True)
    service = ServiceNestedSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'service', 'customer_phone', 'customer_name', 'customer_email',
            'appointment_date', 'appointment_time', 'booking_method',
            'total_price', 'notes', 'auto_confirm',
            # Read-only response fields
            'id', 'booking_id', 'customer', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'booking_id', 'status', 'created_at']
    
    def validate_customer_phone(self, value):
        """Validate Saudi phone number format"""
        if not value.startswith('+966') or len(value) != 13:
            raise serializers.ValidationError(
                "Phone number must be in Saudi format: +966xxxxxxxxx"
            )
        if not value[4:].isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only digits after country code"
            )
        return value
    
    def validate(self, attrs):
        """Validate appointment date/time and business hours"""
        from datetime import datetime
        from django.utils import timezone
        
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')
        service = attrs.get('service')
        
        if appointment_date and appointment_time:
            # Check if appointment is in the future
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            if appointment_datetime <= timezone.now():
                raise serializers.ValidationError({
                    "appointment_date": "Appointment must be in the future"
                })
            
            # Check business hours
            if service and service.business:
                business_hours = service.business.hours.filter(
                    day=appointment_date.strftime('%A').lower()
                ).first()
                
                if business_hours and not business_hours.is_closed:
                    if not (business_hours.open_time <= appointment_time <= business_hours.close_time):
                        raise serializers.ValidationError({
                            "appointment_time": f"Business is closed at this time. "
                                               f"Open hours: {business_hours.open_time} - {business_hours.close_time}"
                        })
                elif business_hours and business_hours.is_closed:
                    raise serializers.ValidationError({
                        "appointment_date": "Business is closed on this day"
                    })
        
        return attrs
    
    def create(self, validated_data):
        """Create booking with customer lookup/creation"""
        # Extract customer data
        customer_phone = validated_data.pop('customer_phone')
        customer_name = validated_data.pop('customer_name')
        customer_email = validated_data.pop('customer_email', '')
        auto_confirm = validated_data.pop('auto_confirm', False)
        
        # Get or create customer
        customer_data = {
            'phone_number': customer_phone,
            'name': customer_name
        }
        if customer_email:
            customer_data['email'] = customer_email
        
        customer, created = Customer.objects.get_or_create(
            phone_number=customer_phone,
            defaults=customer_data
        )
        
        # Update customer info if not newly created
        if not created and customer_email and not customer.email:
            customer.email = customer_email
            customer.save()
        
        # Set derived fields
        service = validated_data['service']
        validated_data['business'] = service.business
        validated_data['customer'] = customer
        
        # Auto-confirm if requested
        if auto_confirm:
            validated_data['status'] = 'confirmed'
        
        # Auto-calculate price if not provided
        if not validated_data.get('total_price'):
            validated_data['total_price'] = service.price
        
        # Create booking
        booking = super().create(validated_data)
        
        # Generate QR code after creation
        try:
            from utils.qr_generator import QRCodeGenerator
            qr_file = QRCodeGenerator.generate_booking_qr(booking)
            if qr_file:
                booking.qr_code.save(qr_file.name, qr_file, save=True)
        except Exception:
            # Don't fail booking creation if QR generation fails
            pass
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for booking updates with status validation"""
    
    class Meta:
        model = Booking
        fields = ['status', 'notes', 'appointment_date', 'appointment_time']
    
    def validate_status(self, value):
        """Validate status transitions"""
        if not self.instance:
            return value
        
        current_status = self.instance.status
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['in_progress', 'cancelled', 'no_show'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],  # Cannot change from completed
            'cancelled': [],  # Cannot change from cancelled
            'no_show': [],   # Cannot change from no_show
        }
        
        if current_status and value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from '{current_status}' to '{value}'"
            )
        
        return value
    
    def validate(self, attrs):
        """Validate appointment changes"""
        if self.instance and (attrs.get('appointment_date') or attrs.get('appointment_time')):
            # Don't allow date/time changes for completed, cancelled, or no_show bookings
            if self.instance.status in ['completed', 'cancelled', 'no_show']:
                raise serializers.ValidationError(
                    "Cannot change appointment time for completed, cancelled, or no-show bookings"
                )
            
            # Validate future appointment
            from datetime import datetime
            from django.utils import timezone
            
            new_date = attrs.get('appointment_date', self.instance.appointment_date)
            new_time = attrs.get('appointment_time', self.instance.appointment_time)
            
            appointment_datetime = datetime.combine(new_date, new_time)
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            if appointment_datetime <= timezone.now():
                raise serializers.ValidationError({
                    "appointment_date": "New appointment must be in the future"
                })
        
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer with nested booking information"""
    booking = BookingSerializer(read_only=True)
    customer_name = serializers.CharField(source='booking.customer.name', read_only=True)
    service_name = serializers.CharField(source='booking.service.name', read_only=True)
    rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'customer_name', 'service_name',
            'rating', 'rating_display', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_rating_display(self, obj):
        """Display rating as stars"""
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    
    def validate_rating(self, value):
        """Validate rating range"""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        """Only allow reviews for completed bookings"""
        booking = validated_data.get('booking')
        if booking and booking.status != 'completed':
            raise serializers.ValidationError({
                "booking": "Reviews can only be created for completed bookings"
            })
        return super().create(validated_data)


class BusinessHoursSerializer(serializers.ModelSerializer):
    """Business hours serializer with validation"""
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    hours_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessHours
        fields = [
            'id', 'business', 'day', 'day_display',
            'open_time', 'close_time', 'hours_formatted', 'is_closed'
        ]
        read_only_fields = ['id', 'business']
    
    def get_hours_formatted(self, obj):
        """Format hours for display"""
        if obj.is_closed:
            return "Closed"
        return f"{obj.open_time.strftime('%H:%M')} - {obj.close_time.strftime('%H:%M')}"
    
    def validate(self, attrs):
        """Validate business hours logic"""
        if not attrs.get('is_closed'):
            open_time = attrs.get('open_time')
            close_time = attrs.get('close_time')
            
            if not open_time or not close_time:
                raise serializers.ValidationError(
                    "Open time and close time are required when not closed"
                )
            
            if open_time >= close_time:
                raise serializers.ValidationError(
                    "Opening time must be before closing time"
                )
        
        return attrs
    
    def create(self, validated_data):
        """Set business from request user"""
        user = self.context['request'].user
        try:
            validated_data['business'] = user.business_profile
        except BusinessProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"business": "User must have a business profile"}
            )
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer with type display"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'customer', 'notification_type', 'notification_type_display',
            'title', 'message', 'is_read', 'sent_via_whatsapp',
            'time_ago', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_time_ago(self, obj):
        """Human-readable time since notification"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(obj.created_at, timezone.now())


# ============================================================================
# Dashboard and Analytics Serializers
# ============================================================================

class BusinessDashboardSerializer(serializers.Serializer):
    """Comprehensive business dashboard statistics"""
    
    # Basic metrics
    total_bookings = serializers.IntegerField()
    period_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    period_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Status breakdown
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    
    # Customer metrics
    total_customers = serializers.IntegerField()
    new_customers_this_period = serializers.IntegerField()
    customer_retention_rate = serializers.FloatField()
    
    # Review metrics
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    
    # Growth metrics
    booking_growth_rate = serializers.FloatField()
    revenue_growth_rate = serializers.FloatField()
    
    # Top performing services
    top_services = serializers.ListField(child=serializers.DictField())
    
    # Recent activity
    recent_bookings = BookingSerializer(many=True, read_only=True)
    upcoming_bookings = BookingSerializer(many=True, read_only=True)
    recent_reviews = ReviewSerializer(many=True, read_only=True)
    
    # Period information
    period_start = serializers.DateField()
    period_end = serializers.DateField()


class BusinessAnalyticsSerializer(serializers.Serializer):
    """Advanced business analytics with visualizations"""
    
    # Time period
    period = serializers.CharField()
    date_range = serializers.DictField()
    
    # Revenue analysis
    revenue_trend = serializers.ListField()
    revenue_by_service = serializers.ListField()
    revenue_growth = serializers.DictField()
    
    # Booking analysis
    booking_trends = serializers.ListField()
    booking_patterns = serializers.DictField()
    peak_hours = serializers.ListField()
    
    # Customer insights
    customer_segments = serializers.DictField()
    customer_lifetime_value = serializers.FloatField()
    customer_acquisition_cost = serializers.FloatField()
    
    # Service performance
    service_performance = serializers.ListField()
    service_ratings = serializers.DictField()
    
    # Operational metrics
    cancellation_rate = serializers.FloatField()
    no_show_rate = serializers.FloatField()
    average_booking_value = serializers.FloatField()
    
    # Visualizations (HTML strings for charts)
    revenue_chart = serializers.CharField(required=False)
    booking_heatmap = serializers.CharField(required=False)
    customer_segment_chart = serializers.CharField(required=False)