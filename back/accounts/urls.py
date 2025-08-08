from django.urls import path
from . import views

urlpatterns = [

      
    # Registration endpoint
    path('register/', views.email_register, name='email_register'),
    
    # Authentication endpoints (clean, consolidated)
    path('login/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.TokenBlacklistView.as_view(), name='token_blacklist'),
    path('logout-all/', views.logout_all_devices, name='logout_all_devices'),
  
    # OTP endpoints (legacy support)
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp_and_register, name='verify_otp_register'),
    
    # User management
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Business profile endpoints
    path('business-profile/', views.BusinessProfileView.as_view(), name='business_profile'),
    path('business-profile/create/', views.BusinessProfileCreateView.as_view(), name='business_profile_create'),
    
    # Subscription endpoints
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
]