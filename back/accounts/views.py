# accounts/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from .serializers import (
    WagteeTokenObtainPairSerializer, WagteeTokenRefreshSerializer,
    OTPRequestSerializer, OTPVerifySerializer, EmailRegistrationSerializer,
    UserSerializer, BusinessProfileSerializer,
    SubscriptionSerializer, BusinessProfileCreateSerializer
)
from .permissions import (
    IsBusinessOwner, IsOwnerOrReadOnly, IsVerifiedUser, CanManageSubscription
)
from .models import BusinessProfile, Subscription
from utils.otp import OTPService
from django.conf import settings
import logging
# WhatsApp integration removed to avoid any potential charges

logger = logging.getLogger(__name__)

User = get_user_model()

class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'

class RefreshRateThrottle(UserRateThrottle):
    scope = 'refresh'

@extend_schema(
    tags=['Authentication'],
    summary='Login with email and password',
    description='Authenticate user with email address and password to get JWT tokens',
    responses={
        200: {
            'description': 'Login successful',
            'example': {
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'email': 'user@business.sa',
                    'role': 'business_owner',
                    'is_verified': True,
                    'subscription_active': True
                }
            }
        },
        401: {
            'description': 'Invalid credentials',
            'example': {
                'detail': 'Invalid credentials provided.'
            }
        }
    }
)
class TokenObtainPairView(TokenObtainPairView):
    """Advanced JWT authentication with security features and rate limiting"""
    serializer_class = WagteeTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        """Enhanced login with comprehensive security logging"""
        client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
        email = request.data.get('email')
        
        # Log authentication attempt (detailed logging is in serializer)
        logger.info(f"Login attempt for email: {email} from IP: {client_ip}")
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f"Successful login for email: {email} from IP: {client_ip}")
        else:
            logger.warning(f"Failed login attempt for email: {email} from IP: {client_ip}")
        
        return response


@extend_schema(
    tags=['Authentication'],
    summary='Refresh JWT access token',
    description='Refresh the access token using a valid refresh token',
    responses={
        200: {
            'description': 'Token refresh successful',
            'example': {
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            }
        },
        401: {
            'description': 'Invalid or expired refresh token',
            'example': {
                'detail': 'Token is invalid or expired'
            }
        }
    }
)
class TokenRefreshView(TokenRefreshView):
    """Enhanced token refresh with user data updates and security logging"""
    serializer_class = WagteeTokenRefreshSerializer
    throttle_classes = [RefreshRateThrottle]
    
    def post(self, request, *args, **kwargs):
        """Enhanced refresh with security logging"""
        client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
        
        logger.info(f"Token refresh attempt from IP: {client_ip}")
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f"Successful token refresh from IP: {client_ip}")
        else:
            logger.warning(f"Failed token refresh from IP: {client_ip}")
        
        return response

class OTPRateThrottle(AnonRateThrottle):
    scope = 'otp'

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def send_otp(request):
    """Send OTP for phone verification"""
    serializer = OTPRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    
    # Use secure OTP service
    result = OTPService.send_otp(phone_number)
    
    if result['success']:
        response_data = {
            'message': result['message'],
            'expires_in': result['expires_in']
        }
        
        # Include OTP in debug mode for easy testing (completely free)
        if settings.DEBUG and result.get('otp'):
            response_data['otp'] = result['otp']
            response_data['debug_note'] = 'OTP included in response for development only'
        
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': result['message'],
            'error_code': result['error_code']
        }, status=status.HTTP_429_TOO_MANY_REQUESTS if result['error_code'] == 'RATE_LIMIT_EXCEEDED' else status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_otp_and_register(request):
    """Verify OTP and register/login user"""
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp = serializer.validated_data['otp']
    
    # Verify OTP using secure service
    verification_result = OTPService.verify_otp(phone_number, otp)
    
    if not verification_result['success']:
        return Response({
            'error': verification_result['message'],
            'error_code': verification_result['error_code'],
            'remaining_attempts': verification_result.get('remaining_attempts')
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get additional data
    business_data = request.data.get('business_data', {})
    user_data = request.data.get('user_data', {})
    
    try:
        # Create or get user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'username': phone_number,
                'is_verified': True,
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'email': user_data.get('email', ''),
                'role': user_data.get('role', 'business_owner'),
                'business_name': user_data.get('business_name', ''),
                'cr_number': user_data.get('cr_number', ''),
                'city': user_data.get('city', ''),
                'district': user_data.get('district', ''),
            }
        )
        
        if not created:
            # Update verification status for existing users
            user.is_verified = True
            user.save()
        
        # Create business profile if provided and user is new
        if created and business_data and user.role == 'business_owner':
            try:
                BusinessProfile.objects.create(user=user, **business_data)
            except Exception as e:
                logger.error(f"Failed to create business profile for {phone_number}: {str(e)}")
        
        # Generate enhanced tokens with additional claims
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Add additional claims to access token
        access_token['phone_number'] = user.phone_number
        access_token['role'] = user.role
        access_token['is_verified'] = user.is_verified
        access_token['subscription_active'] = user.subscription_active
        
        # Get user data with permissions and subscription status
        user_serializer = UserSerializer(user)
        user_data = user_serializer.data
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': user_data,
            'created': created,
            'token_type': 'Bearer',
            'expires_in': 1800,  # 30 minutes in seconds
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Registration error for {phone_number}: {str(e)}")
        return Response({
            'error': 'Registration failed. Please try again.',
            'error_code': 'REGISTRATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    tags=['Authentication'],
    summary='Register new business account',
    description='Register a new business owner account with email authentication',
    request=EmailRegistrationSerializer,
    responses={
        201: {
            'description': 'Registration successful',
            'example': {
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'username': 'businessowner',
                    'email': 'owner@business.sa',
                    'role': 'business_owner',
                    'is_verified': False,
                    'subscription_active': True
                },
                'token_type': 'Bearer',
                'expires_in': 1800,
                'message': 'Registration successful. Please verify your email.'
            }
        },
        400: {
            'description': 'Validation error',
            'example': {
                'email': ['This field is required.'],
                'password': ['This field is required.']
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])  # Reuse login throttle for registration
def email_register(request):
    """Email-first registration without OTP"""
    serializer = EmailRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create user and business profile
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Add additional claims to access token
        access_token['email'] = user.email
        access_token['role'] = user.role
        access_token['is_verified'] = user.is_verified
        access_token['subscription_active'] = user.subscription_active
        
        # Get user data with permissions and subscription status
        user_serializer = UserSerializer(user)
        user_data = user_serializer.data
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': user_data,
            'token_type': 'Bearer',
            'expires_in': 1800,  # 30 minutes in seconds
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Email registration error for {request.data.get('email')}: {str(e)}")
        return Response({
            'error': 'Registration failed. Please try again.',
            'error_code': 'REGISTRATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsVerifiedUser]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """Enhanced profile with comprehensive user information"""
        response = super().retrieve(request, *args, **kwargs)
        
        # The serializer now includes permissions and subscription_status
        # through SerializerMethodField, so no need to add them manually
        
        return response


class BusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_object(self):
        try:
            return self.request.user.business_profile
        except BusinessProfile.DoesNotExist:
            raise Response(
                {'error': 'Business profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class BusinessProfileCreateView(generics.CreateAPIView):
    serializer_class = BusinessProfileCreateSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionListView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [CanManageSubscription]
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'super_admin']:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        if self.request.user.role == 'business_owner':
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [CanManageSubscription]
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'super_admin']:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsVerifiedUser])
def logout_view(request):
    """Enhanced logout with token blacklisting"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f'User {request.user.phone_number} logged out successfully')
            
            return Response({
                'message': 'تم تسجيل الخروج بنجاح / Logged out successfully',
                'success': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'لم يتم توفير رمز التحديث / Refresh token not provided',
                'error_code': 'MISSING_REFRESH_TOKEN'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except TokenError as e:
        logger.warning(f'Logout token error for user {request.user.phone_number}: {str(e)}')
        return Response({
            'error': 'رمز غير صالح / Invalid token',
            'error_code': 'INVALID_TOKEN'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f'Logout error for user {request.user.phone_number}: {str(e)}')
        return Response({
            'error': 'فشل في تسجيل الخروج / Logout failed',
            'error_code': 'LOGOUT_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsVerifiedUser]) 
def logout_all_devices(request):
    """Logout from all devices by blacklisting all user's tokens"""
    try:
        # Get all outstanding tokens for the user
        tokens = OutstandingToken.objects.filter(user=request.user)
        
        # Blacklist all tokens
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except:
                continue
        
        logger.info(f'User {request.user.phone_number} logged out from all devices')
        
        return Response({
            'message': 'تم تسجيل الخروج من جميع الأجهزة بنجاح / Logged out from all devices successfully',
            'success': True,
            'tokens_blacklisted': tokens.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f'Logout all error for user {request.user.phone_number}: {str(e)}')
        return Response({
            'error': 'فشل في تسجيل الخروج من جميع الأجهزة / Failed to logout from all devices',
            'error_code': 'LOGOUT_ALL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Authentication'],
    summary='Logout (Blacklist Token)',
    description='Blacklist refresh token to logout securely',
    responses={
        200: {'description': 'Logout successful'},
        400: {'description': 'Invalid token'}
    }
)
class TokenBlacklistView(TokenBlacklistView):
    """Enhanced token blacklist (logout) with security logging"""
    permission_classes = []  # Allow any user to logout
    
    def post(self, request, *args, **kwargs):
        """Enhanced logout with security logging"""
        client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
        
        # Try to get user info from token before blacklisting
        refresh_token = request.data.get('refresh')
        user_info = "Unknown"
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                user_id = token.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        user_info = f"{user.email} (ID: {user.id})"
                    except User.DoesNotExist:
                        pass
            except Exception:
                pass
        
        # Log logout attempt
        logger.info(f"Logout attempt for user: {user_info} from IP: {client_ip}")
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f"Successful logout for user: {user_info} from IP: {client_ip}")
        else:
            logger.warning(f"Failed logout attempt for user: {user_info} from IP: {client_ip}")
        
        return response