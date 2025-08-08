from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import BusinessProfile, Subscription
from .role_manager import RoleManager
from .subscription_manager import SubscriptionManager
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
import logging

logger = logging.getLogger('security')

User = get_user_model()


class WagteeTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Advanced JWT authentication serializer with email-based login and comprehensive security features
    """
    username_field = User.USERNAME_FIELD  # Use email as username field
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField(
            error_messages={
                'required': 'البريد الإلكتروني مطلوب / Email is required',
                'blank': 'البريد الإلكتروني لا يمكن أن يكون فارغاً / Email cannot be blank',
                'invalid': 'أدخل عنوان بريد إلكتروني صحيح / Enter a valid email address'
            }
        )
        self.fields['password'] = serializers.CharField(
            write_only=True,
            error_messages={
                'required': 'كلمة المرور مطلوبة / Password is required',
                'blank': 'كلمة المرور لا يمكن أن تكون فارغة / Password cannot be blank'
            }
        )

    @classmethod
    def get_token(cls, user):
        """Generate JWT token with comprehensive claims"""
        token = super().get_token(user)
        
        # Security claims
        token['user_id'] = user.id
        token['email'] = user.email
        token['role'] = user.role
        token['is_verified'] = user.is_verified
        token['iss'] = 'wagtee.sa'
        
        # Business profile info if exists
        if hasattr(user, 'business_profile'):
            token['business_id'] = user.business_profile.id
            token['service_type'] = user.business_profile.service_type
        
        # Subscription info
        token['subscription_active'] = user.subscription_active
        
        # Add permissions and subscription features
        try:
            permissions = RoleManager.get_user_permissions(user)
            token['permissions'] = permissions
            
            subscription_status = SubscriptionManager.get_subscription_status(user)
            token['subscription'] = {
                'tier': subscription_status['subscription']['tier'],
                'is_active': subscription_status['subscription']['is_active'],
                'features': subscription_status['features']
            }
        except Exception as e:
            logger.warning(f"Error adding permissions/subscription to token: {e}")
        
        # Security logging
        logger.info(f"Token generated for user {user.email} (ID: {user.id}, Role: {user.role})")
        
        return token
    
    def validate(self, attrs):
        """Enhanced validation with security checks and logging"""
        email = attrs.get(self.username_field)
        password = attrs.get('password')
        request = self.context.get('request')
        client_ip = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
        
        # Log authentication attempt
        logger.info(f'Authentication attempt for email: {email} from IP: {client_ip}')
        
        if not email:
            logger.warning(f"Token request without email from IP: {client_ip}")
            raise serializers.ValidationError({
                'email': 'Email is required for authentication.'
            })
        
        # Authenticate user
        user = authenticate(
            request=request,
            username=email,
            password=password
        )
        
        if user is None:
            logger.warning(f"Failed login attempt for email: {email} from IP: {client_ip}")
            raise serializers.ValidationError({
                'detail': 'البريد الإلكتروني أو كلمة المرور غير صحيحة / Invalid email or password'
            })
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            raise serializers.ValidationError({
                'detail': 'حساب المستخدم غير مفعل / User account is deactivated'
            })
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Get refresh token
        refresh = self.get_token(user)
        
        # Log successful authentication
        logger.info(f"Successful authentication for user: {email} (Role: {user.role}) from IP: {client_ip}")
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified,
                'subscription_active': user.subscription_active,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }


class WagteeTokenRefreshSerializer(TokenRefreshSerializer):
    """Enhanced token refresh with security logging and user data updates"""
    
    def validate(self, attrs):
        """Enhanced refresh with logging and updated user data in token"""
        try:
            data = super().validate(attrs)
            
            # Get user from refresh token
            refresh_token = RefreshToken(attrs['refresh'])
            user_id = refresh_token.payload.get('user_id')
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    logger.info(f'Token refresh successful for user: {user.email} (ID: {user.id})')
                    
                    # Generate new tokens with updated user data
                    new_refresh = WagteeTokenObtainPairSerializer.get_token(user)
                    data['refresh'] = str(new_refresh)
                    data['access'] = str(new_refresh.access_token)
                    
                except User.DoesNotExist:
                    logger.warning(f'Token refresh failed - user not found: {user_id}')
                    raise InvalidToken('المستخدم غير موجود / User not found')
            
            return data
            
        except TokenError as e:
            logger.warning(f'Token refresh failed - invalid token: {str(e)}')
            raise InvalidToken('الرمز المميز غير صالح أو منتهي الصلاحية / Token is invalid or expired')
        except Exception as e:
            logger.error(f'Token refresh error: {str(e)}')
            raise serializers.ValidationError({
                'non_field_errors': ['فشل في تحديث الرمز المميز / Token refresh failed']
            })


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+966[0-9]{9}$',
            message="رقم الهاتف يجب أن يكون بالتنسيق: '+966xxxxxxxxx' / Phone number must be in format: '+966xxxxxxxxx'"
        )],
        error_messages={
            'required': 'رقم الهاتف مطلوب / Phone number is required',
            'blank': 'رقم الهاتف لا يمكن أن يكون فارغاً / Phone number cannot be blank'
        }
    )
    
    def validate_phone_number(self, value):
        # Log OTP request
        logger.info(f'OTP request for phone: {value}')
        return value


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+966[0-9]{9}$',
            message="رقم الهاتف يجب أن يكون بالتنسيق: '+966xxxxxxxxx' / Phone number must be in format: '+966xxxxxxxxx'"
        )],
        error_messages={
            'required': 'رقم الهاتف مطلوب / Phone number is required',
            'blank': 'رقم الهاتف لا يمكن أن يكون فارغاً / Phone number cannot be blank'
        }
    )
    otp = serializers.CharField(
        max_length=6, 
        min_length=6,
        error_messages={
            'required': 'رمز التحقق مطلوب / OTP code is required',
            'blank': 'رمز التحقق لا يمكن أن يكون فارغاً / OTP code cannot be blank',
            'min_length': 'رمز التحقق يجب أن يكون 6 أرقام / OTP code must be 6 digits',
            'max_length': 'رمز التحقق يجب أن يكون 6 أرقام / OTP code must be 6 digits'
        }
    )
    
    def validate(self, attrs):
        # Log OTP verification attempt
        logger.info(f'OTP verification attempt for phone: {attrs.get("phone_number")}')
        return attrs




class EmailRegistrationSerializer(serializers.ModelSerializer):
    """Email-first registration without OTP"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    # Business profile fields - these are extra fields for business profile creation
    service_type = serializers.CharField(required=True, write_only=True)
    address = serializers.CharField(required=True, write_only=True)
    address_ar = serializers.CharField(required=False, allow_blank=True, write_only=True)
    terms_accepted = serializers.BooleanField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone_number', 
            'password', 'confirm_password', 'role', 'business_name', 
            'city', 'district', 'cr_number', 'vat_number',
            'service_type', 'address', 'address_ar', 'terms_accepted'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': False},  # Make phone optional
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Check if email is already registered"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("البريد الإلكتروني مستخدم بالفعل / Email is already registered")
        return value

    def validate_username(self, value):
        """Check if username is already taken"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("اسم المستخدم مستخدم بالفعل / Username is already taken")
        return value

    def validate_phone_number(self, value):
        """Validate Saudi phone number format"""
        if not value.startswith('+966'):
            raise serializers.ValidationError("رقم الهاتف يجب أن يبدأ بـ +966 / Phone number must start with +966")
        if len(value) != 13:  # +966 + 9 digits
            raise serializers.ValidationError("رقم الهاتف يجب أن يكون 13 رقماً بما في ذلك +966 / Phone number must be 13 digits including +966")
        return value

    def validate_terms_accepted(self, value):
        """Ensure terms are accepted"""
        if not value:
            raise serializers.ValidationError("يجب الموافقة على الشروط والأحكام / Terms and conditions must be accepted")
        return value

    def validate(self, attrs):
        """Validate password confirmation and business data"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'password': 'كلمات المرور غير متطابقة / Passwords don\'t match'
            })
        
        # Validate service types
        valid_service_types = [
            'barber', 'salon', 'beauty_center', 'car_wash', 'cleaning',
            'gym', 'photographer', 'makeup_artist', 'bazar', 'events'
        ]
        if attrs.get('service_type') not in valid_service_types:
            raise serializers.ValidationError({
                'service_type': f'نوع الخدمة غير صحيح / Invalid service type. Must be one of: {valid_service_types}'
            })
        
        # Validate VAT number format if provided
        vat_number = attrs.get('vat_number')
        if vat_number and vat_number.strip():
            if not vat_number.isdigit() or len(vat_number) != 15:
                raise serializers.ValidationError({
                    'vat_number': 'رقم ضريبة القيمة المضافة يجب أن يكون 15 رقماً / VAT number must be 15 digits'
                })
        
        # Validate CR number format if provided
        cr_number = attrs.get('cr_number')
        if cr_number and cr_number.strip():
            if not cr_number.isdigit() or len(cr_number) != 10:
                raise serializers.ValidationError({
                    'cr_number': 'رقم السجل التجاري يجب أن يكون 10 أرقام / CR number must be 10 digits'
                })
        
        return attrs

    def create(self, validated_data):
        """Create user and business profile"""
        # Extract business profile fields first (before popping)
        business_name = validated_data.pop('business_name')
        service_type = validated_data.pop('service_type')
        address = validated_data.pop('address')
        address_ar = validated_data.pop('address_ar', '')
        city = validated_data.pop('city')
        district = validated_data.pop('district')
        cr_number = validated_data.pop('cr_number', '')
        vat_number = validated_data.pop('vat_number', '')
        
        # Remove non-User fields
        validated_data.pop('confirm_password')
        validated_data.pop('terms_accepted')
        
        # Prepare business profile data
        business_data = {
            'service_type': service_type,
            'address': address,
            'address_ar': address_ar,
            'description': f"A {business_name} in {city}",
            'description_ar': f"{business_name} في {city}",
            'is_active': True,
        }
        
        # Create user with User model fields only
        password = validated_data.pop('password')
        
        # Add business profile fields to User fields that exist in User model
        validated_data['business_name'] = business_name
        validated_data['city'] = city
        validated_data['district'] = district
        validated_data['cr_number'] = cr_number
        validated_data['vat_number'] = vat_number
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.is_verified = False  # Will be verified via email
        user.save()
        
        # Create business profile
        BusinessProfile.objects.create(user=user, **business_data)
        
        # Log registration
        logger.info(f"New user registered: {user.email} ({user.role})")
        
        return user


class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone_number', 'email', 'first_name', 'last_name',
            'role', 'business_name', 'cr_number', 'vat_number', 'city', 'district',
            'is_verified', 'subscription_tier', 'subscription_active',
            'subscription_expires', 'created_at', 'updated_at',
            'permissions', 'subscription_status'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at', 'permissions', 'subscription_status']
    
    def get_permissions(self, obj):
        """Get user permissions"""
        return RoleManager.get_user_permissions(obj)
    
    def get_subscription_status(self, obj):
        """Get subscription status"""
        return SubscriptionManager.get_subscription_status(obj)


class BusinessProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'user', 'service_type', 'description', 'description_ar', 
            'address', 'address_ar', 'latitude', 'longitude', 'working_hours', 
            'images', 'rating', 'is_active', 'qr_code'
        ]
        read_only_fields = ['id', 'rating', 'qr_code']

    def validate_working_hours(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("ساعات العمل يجب أن تكون كائن JSON / Working hours must be a JSON object")
        
        valid_days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for day in value.keys():
            if day not in valid_days:
                raise serializers.ValidationError(f"يوم غير صالح: {day} / Invalid day: {day}")
        
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'tier', 'price', 'is_active',
            'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'start_date', 'created_at', 'updated_at']


class BusinessProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = [
            'service_type', 'description', 'description_ar', 'address', 'address_ar',
            'latitude', 'longitude', 'working_hours', 'images'
        ]
        extra_kwargs = {
            'description_ar': {'required': False},
            'address_ar': {'required': False},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        business_profile = super().create(validated_data)
        
        # Generate QR code after creation
        from utils.qr_generator import QRCodeGenerator
        qr_file = QRCodeGenerator.generate_business_qr(business_profile)
        if qr_file:
            business_profile.qr_code.save(qr_file.name, qr_file, save=True)
        
        return business_profile

    def validate_working_hours(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("ساعات العمل يجب أن تكون كائن JSON / Working hours must be a JSON object")
        
        valid_days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for day in value.keys():
            if day not in valid_days:
                raise serializers.ValidationError(f"يوم غير صالح: {day} / Invalid day: {day}")
        
        return value