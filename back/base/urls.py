from django.urls import path
from . import views

urlpatterns = [
    # Services
    path('services/', views.ServiceListCreateView.as_view(), name='service_list_create'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/bulk-delete/', views.bulk_delete_services, name='bulk_delete_services'),
    path('services/bulk-update/', views.bulk_update_services, name='bulk_update_services'),
    
    # Bookings (Business Management)
    path('bookings/', views.BookingListCreateView.as_view(), name='booking_list_create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/bulk-update/', views.bulk_update_bookings, name='bulk_update_bookings'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    
    # Reviews
    path('reviews/', views.ReviewListCreateView.as_view(), name='review_list_create'),
    
    # Business hours
    path('business-hours/', views.BusinessHoursListCreateView.as_view(), name='business_hours_list_create'),
    path('business-hours/<int:pk>/', views.BusinessHoursDetailView.as_view(), name='business_hours_detail'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Dashboard & Analytics
    path('dashboard/', views.business_dashboard, name='business_dashboard'),
    path('analytics/', views.business_analytics, name='business_analytics'),
    path('subscription-status/', views.subscription_status, name='subscription_status'),
    path('permissions/', views.user_permissions, name='user_permissions'),
    
    # QR Code generation endpoints
    path('qr/business/', views.generate_business_qr, name='generate_business_qr'),
    path('qr/service/<int:service_id>/', views.generate_service_qr, name='generate_service_qr'),
    path('qr/booking/<int:booking_id>/', views.booking_qr_code, name='booking_qr_code'),
    
    # Public endpoints (Customer-facing, no authentication required)
    path('public/booking/', views.PublicBookingCreateView.as_view(), name='public_booking_create'),
    path('public/booking/<str:booking_id>/', views.public_booking_lookup, name='public_booking_lookup'),
    path('public/booking/cancel/', views.public_booking_cancel, name='public_booking_cancel'),
    path('public/business/<int:business_id>/service/<int:service_id>/slots/', views.public_available_slots, name='public_available_slots'),
]