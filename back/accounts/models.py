# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Set username to email to avoid unique constraint issues
        extra_fields.setdefault('username', email)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('username', email)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('business_owner', 'Business Owner'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+966[0-9]{9}$',
        message="Phone number must be in format: '+966xxxxxxxxx'"
    )
    
    cr_regex = RegexValidator(
        regex=r'^[1-9][0-9]{9}$',
        message="CR number must be 10 digits starting with 1-9"
    )
    
    # Email field is inherited from AbstractUser but ensure it's unique and required
    email = models.EmailField(unique=True, null=False, blank=False, verbose_name='Email')
    
    # Override first_name and last_name to have English verbose names
    first_name = models.CharField(max_length=150, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Last name')
    
    # User role and profile information
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='business_owner')
    
    # Phone number - optional but kept for WhatsApp notifications
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Used for WhatsApp notifications (optional)"
    )
    
    # Verification and business details
    is_verified = models.BooleanField(default=False)
    business_name = models.CharField(max_length=255, blank=True)
    cr_number = models.CharField(validators=[cr_regex], max_length=10, blank=True, help_text="Commercial Registration Number")
    vat_number = models.CharField(max_length=15, blank=True, help_text="15-digit VAT number")
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    
    # Subscription management
    subscription_tier = models.CharField(max_length=20, blank=True, null=True)
    subscription_active = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Authentication configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Custom manager
    objects = UserManager()
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set', 
        related_query_name='custom_user',
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),  # Keep for WhatsApp lookups
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['subscription_active']),
        ]
        
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

class BusinessProfile(models.Model):
    SERVICE_TYPES = [
        ('barber', 'Barber'),
        ('salon', 'Hair Salon'),
        ('beauty_center', 'Beauty Center'),
        ('car_wash', 'Car Wash'),
        ('cleaning', 'Cleaning Center'),
        ('gym', 'Gym'),
        ('photographer', 'Photographer'),
        ('makeup_artist', 'Makeup Artist'),
        ('bazar', 'Bazar'),
        ('events', 'Events'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True, help_text="Arabic description")
    address = models.TextField()
    address_ar = models.TextField(blank=True, help_text="Arabic address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    working_hours = models.JSONField(default=dict)
    images = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['service_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['rating']),
        ]
    
class Subscription(models.Model):
    TIER_CHOICES = [
        ('basic', 'Basic - 30 SAR'),
        ('standard', 'Standard - 45 SAR'),
        ('premium', 'Premium - 60 SAR'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    # Payment gateway integration removed for testing mode
    # moyasser_subscribtion_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['tier']),
            models.Index(fields=['end_date']),
        ]