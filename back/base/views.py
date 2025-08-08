from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q, F, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from rest_framework.pagination import PageNumberPagination
from .models import Service, Customer, Booking, Review, BusinessHours, Notification
from .serializers import (
    ServiceSerializer, CustomerSerializer, BookingCreateSerializer,
    BookingSerializer, BookingUpdateSerializer, ReviewSerializer,
    BusinessHoursSerializer, NotificationSerializer, BusinessDashboardSerializer,
    ServiceCreateUpdateSerializer, BusinessAnalyticsSerializer, CustomerDetailSerializer
)
from accounts.permissions import (
    IsBusinessOwner, IsVerifiedUser, IsOwnerOrReadOnly, BusinessResourcePermission,
    RoleBasedPermission, SubscriptionRequired, FeaturePermission
)
from accounts.role_manager import RoleManager, Resource, Action, RolePermissionMixin
from accounts.subscription_manager import SubscriptionManager, SubscriptionEnforcementMixin
from .booking_manager import BookingManager
from utils.notification_manager import NotificationManager
from .security import (
    SecurityValidator, RateLimiter, AuditLogger, SubscriptionSecurity,
    rate_limit, require_subscription
)


# Pagination class
class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for list views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ServiceListCreateView(generics.ListCreateAPIView, SubscriptionEnforcementMixin, RolePermissionMixin):
    serializer_class = ServiceSerializer
    permission_classes = [BusinessResourcePermission]
    required_resource = Resource.SERVICES
    required_action = Action.CREATE
    subscription_limit = 'max_services'
    
    def get_queryset(self):
        return RoleManager.filter_queryset_by_role(
            self.request.user,
            Service.objects.select_related('business__user'),
            user_field='business__user'
        )
    
    @rate_limit('api_general', per_user=True)
    @require_subscription(['basic_booking'])
    def list(self, request, *args, **kwargs):
        # Log data access
        AuditLogger.log_security_event(
            'DATA_ACCESS',
            request.user.id if request.user.is_authenticated else None,
            RateLimiter.get_client_ip(request),
            {'resource': 'services', 'action': 'list'}
        )
        return super().list(request, *args, **kwargs)
    
    @rate_limit('api_heavy', per_user=True)
    @require_subscription(['basic_booking'])
    def create(self, request, *args, **kwargs):
        # Validate and sanitize input data
        data = request.data.copy()
        
        # Sanitize text fields
        for field in ['name', 'description', 'name_ar', 'description_ar']:
            if field in data:
                data[field] = SecurityValidator.sanitize_input(data[field])
        
        # Validate business-specific data
        validation_errors = SecurityValidator.validate_business_data(data)
        if validation_errors:
            return Response({
                'error': 'بيانات غير صحيحة',
                'details': validation_errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check subscription limits
        is_valid, message = SubscriptionSecurity.validate_subscription_access(
            request.user, ['basic_booking']
        )
        
        if not is_valid:
            return Response({
                'error': message,
                'subscription_required': True,
                'upgrade_url': '/api/accounts/subscriptions/'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        # Log creation attempt
        AuditLogger.log_security_event(
            'DATA_MODIFICATION',
            request.user.id,
            RateLimiter.get_client_ip(request),
            {'resource': 'services', 'action': 'create', 'data': data}
        )
        
        # Create with sanitized data
        request._full_data = data
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        try:
            serializer.save(business=self.request.user.business_profile)
        except Exception as e:
            logger.error(f"Service creation failed: {e}")
            raise Response({'error': 'Business profile required'}, status=400)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_queryset(self):
        try:
            return Service.objects.filter(business=self.request.user.business_profile)
        except:
            return Service.objects.none()


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        try:
            queryset = Booking.objects.filter(business=self.request.user.business_profile)
            
            # Filter by status
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Filter by date range
            date_from = self.request.query_params.get('date_from')
            date_to = self.request.query_params.get('date_to')
            if date_from:
                queryset = queryset.filter(appointment_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(appointment_date__lte=date_to)
            
            return queryset.select_related('customer', 'service').order_by('-created_at')
        except:
            return Booking.objects.none()


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        try:
            return Booking.objects.filter(business=self.request.user.business_profile)
        except:
            return Booking.objects.none()


class PublicBookingCreateView(generics.CreateAPIView):
    """Public endpoint for customers to create bookings without registration"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Create booking using BookingManager"""
        result = BookingManager.create_anonymous_booking(request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            if result.get('error_code') == 'NOT_AVAILABLE':
                status_code = status.HTTP_409_CONFLICT
            elif result.get('error_code') == 'TIME_CONFLICT':
                status_code = status.HTTP_409_CONFLICT
                
            return Response(result, status=status_code)


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_queryset(self):
        try:
            return Review.objects.filter(
                booking__business=self.request.user.business_profile
            ).select_related('booking__customer', 'booking__service').order_by('-created_at')
        except:
            return Review.objects.none()


class BusinessHoursListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessHoursSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_queryset(self):
        try:
            return BusinessHours.objects.filter(business=self.request.user.business_profile)
        except:
            return BusinessHours.objects.none()
    
    def perform_create(self, serializer):
        try:
            serializer.save(business=self.request.user.business_profile)
        except:
            raise Response({'error': 'Business profile required'}, status=400)


class BusinessHoursDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessHoursSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_queryset(self):
        try:
            return BusinessHours.objects.filter(business=self.request.user.business_profile)
        except:
            return BusinessHours.objects.none()


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsVerifiedUser]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def business_dashboard(request):
    """Business dashboard with statistics"""
    try:
        business_profile = request.user.business_profile
        
        # Date filters
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        
        # Booking statistics
        bookings = Booking.objects.filter(business=business_profile)
        
        total_bookings = bookings.count()
        pending_bookings = bookings.filter(status='pending').count()
        completed_bookings = bookings.filter(status='completed').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        
        # Revenue statistics
        completed_bookings_qs = bookings.filter(status='completed')
        total_revenue = completed_bookings_qs.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        monthly_revenue = completed_bookings_qs.filter(
            appointment_date__gte=this_month_start
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Review statistics
        reviews = Review.objects.filter(booking__business=business_profile)
        average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        total_reviews = reviews.count()
        
        # Upcoming bookings (next 7 days)
        upcoming_bookings = bookings.filter(
            appointment_date__gte=today,
            appointment_date__lte=today + timedelta(days=7),
            status__in=['pending', 'confirmed']
        ).select_related('customer', 'service')[:5]
        
        # Recent reviews
        recent_reviews = reviews.select_related(
            'booking__customer', 'booking__service'
        ).order_by('-created_at')[:5]
        
        dashboard_data = {
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'average_rating': round(float(average_rating), 2) if average_rating else 0,
            'total_reviews': total_reviews,
            'upcoming_bookings': upcoming_bookings,
            'recent_reviews': recent_reviews,
        }
        
        serializer = BusinessDashboardSerializer(dashboard_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Dashboard error for user {request.user.id}: {str(e)}")
        return Response({
            'error': 'Dashboard data unavailable',
            'error_code': 'DASHBOARD_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_booking_lookup(request, booking_id):
    """Look up booking details by booking ID (for customers)"""
    booking_details = BookingManager.get_booking_by_id(booking_id)
    
    if booking_details:
        return Response({
            'success': True,
            'booking': booking_details
        })
    else:
        return Response({
            'success': False,
            'error': 'Booking not found',
            'error_code': 'NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def public_booking_cancel(request):
    """Cancel booking using booking ID and phone verification"""
    booking_id = request.data.get('booking_id')
    phone_number = request.data.get('phone_number')
    reason = request.data.get('reason', '')
    
    if not booking_id or not phone_number:
        return Response({
            'success': False,
            'error': 'Booking ID and phone number are required',
            'error_code': 'MISSING_FIELDS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = BookingManager.cancel_booking(booking_id, phone_number, reason)
    
    if result['success']:
        return Response(result)
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        if result.get('error_code') == 'BOOKING_NOT_FOUND':
            status_code = status.HTTP_404_NOT_FOUND
        elif result.get('error_code') == 'TOO_LATE_TO_CANCEL':
            status_code = status.HTTP_409_CONFLICT
            
        return Response(result, status=status_code)

# New endpoints for enhanced functionality

class CustomerListView(generics.ListAPIView):
    """List all customers for a business with advanced filtering"""
    serializer_class = CustomerDetailSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone_number', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        try:
            # Get customers who have bookings with this business
            return Customer.objects.filter(
                booking__business=self.request.user.business_profile
            ).distinct().annotate(
                total_bookings=Count('booking'),
                total_spent=Sum('booking__total_price', filter=Q(booking__status='completed')),
                last_booking=Max('booking__created_at'),
                avg_rating=Avg('booking__review__rating')
            )
        except AttributeError:
            return Customer.objects.none()
            
class CustomerDetailView(generics.RetrieveAPIView):
    """Get detailed customer information including booking history"""
    serializer_class = CustomerDetailSerializer
    permission_classes = [IsBusinessOwner, IsVerifiedUser]
    
    def get_queryset(self):
        try:
            return Customer.objects.filter(
                booking__business=self.request.user.business_profile
            ).distinct()
        except AttributeError:
            return Customer.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        customer = self.get_object()
        
        # Get customer's booking history with this business
        bookings = Booking.objects.filter(
            customer=customer,
            business=request.user.business_profile
        ).select_related('service').order_by('-created_at')
        
        # Get customer statistics
        stats = bookings.aggregate(
            total_bookings=Count('id'),
            completed_bookings=Count('id', filter=Q(status='completed')),
            cancelled_bookings=Count('id', filter=Q(status='cancelled')),
            total_spent=Sum('total_price', filter=Q(status='completed')),
            avg_rating=Avg('review__rating')
        )
        
        serializer = self.get_serializer(customer)
        data = serializer.data
        data.update({
            'statistics': stats,
            'recent_bookings': BookingSerializer(bookings[:5], many=True).data,
            'favorite_services': list(bookings.values('service__name').annotate(
                count=Count('service')
            ).order_by('-count')[:3])
        })
        
        return Response(data)

@api_view(['GET'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def business_analytics(request):
    """Advanced business analytics endpoint with premium Plotly visualizations"""
    try:
        from utils.premium_analytics import PremiumAnalytics
        
        business_profile = request.user.business_profile
        period = request.query_params.get('period', 'month')
        include_charts = request.query_params.get('charts', 'true').lower() == 'true'
        
        # Date range calculation
        today = timezone.now().date()
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = end_date = today
        
        # Comprehensive analytics
        bookings = Booking.objects.filter(business=business_profile)
        
        # Revenue trends (by day/week/month)
        if period == 'week':
            revenue_trend = bookings.filter(
                appointment_date__range=[start_date, end_date],
                status='completed'
            ).values('appointment_date').annotate(
                revenue=Sum('total_price'),
                bookings=Count('id')
            ).order_by('appointment_date')
        else:
            revenue_trend = bookings.filter(
                appointment_date__range=[start_date, end_date],
                status='completed'
            ).extra(
                select={'period': "DATE_TRUNC('month', appointment_date)"}
            ).values('period').annotate(
                revenue=Sum('total_price'),
                bookings=Count('id')
            ).order_by('period')
        
        # Service performance
        service_performance = bookings.filter(
            appointment_date__range=[start_date, end_date],
            status='completed'
        ).values('service__name').annotate(
            revenue=Sum('total_price'),
            bookings=Count('id'),
            avg_rating=Avg('review__rating')
        ).order_by('-revenue')
        
        # Customer insights
        customer_insights = {
            'new_customers': Customer.objects.filter(
                booking__business=business_profile,
                created_at__range=[start_date, end_date]
            ).distinct().count(),
            'repeat_rate': Customer.objects.filter(
                booking__business=business_profile
            ).annotate(
                booking_count=Count('booking')
            ).filter(booking_count__gt=1).count(),
            'avg_bookings_per_customer': bookings.values('customer').annotate(
                booking_count=Count('id')
            ).aggregate(avg=Avg('booking_count'))['avg'] or 0
        }
        
        # Peak hours analysis
        peak_hours = bookings.filter(
            appointment_date__range=[start_date, end_date]
        ).extra(
            select={'hour': "EXTRACT(hour FROM appointment_time)"}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Cancellation analysis
        cancellation_stats = bookings.filter(
            appointment_date__range=[start_date, end_date]
        ).values('status').annotate(count=Count('id'))
        
        total_period_bookings = sum(stat['count'] for stat in cancellation_stats)
        cancellation_rate = 0
        if total_period_bookings > 0:
            cancelled = next((stat['count'] for stat in cancellation_stats if stat['status'] == 'cancelled'), 0)
            cancellation_rate = (cancelled / total_period_bookings) * 100
        
        analytics_data = {
            'period': period,
            'date_range': {'start': start_date, 'end': end_date},
            'revenue_trend': list(revenue_trend),
            'service_performance': list(service_performance),
            'customer_insights': customer_insights,
            'peak_hours': list(peak_hours),
            'cancellation_rate': round(cancellation_rate, 2),
            'status_breakdown': {stat['status']: stat['count'] for stat in cancellation_stats}
        }
        
        # Generate premium Plotly visualizations if requested
        if include_charts:
            try:
                # Get booking data for heatmap
                booking_data = list(bookings.filter(
                    appointment_date__range=[start_date, end_date]
                ).values('appointment_date', 'status', 'total_price'))
                
                # Generate premium charts
                analytics_data['activity_heatmap'] = PremiumAnalytics.generate_activity_heatmap(
                    booking_data, period
                )
                
                analytics_data['revenue_chart'] = PremiumAnalytics.generate_revenue_chart(
                    list(revenue_trend), period
                )
                
                analytics_data['service_performance_chart'] = PremiumAnalytics.generate_service_performance_chart(
                    list(service_performance)
                )
                
                # Calculate growth metrics
                if period != 'day':
                    # Get previous period data for comparison
                    if period == 'week':
                        prev_start = start_date - timedelta(days=7)
                        prev_end = start_date - timedelta(days=1)
                    elif period == 'month':
                        if start_date.month == 1:
                            prev_start = start_date.replace(year=start_date.year - 1, month=12, day=1)
                            prev_end = start_date.replace(year=start_date.year - 1, month=12, day=31)
                        else:
                            prev_start = start_date.replace(month=start_date.month - 1, day=1)
                            prev_end = start_date - timedelta(days=1)
                    else:  # year
                        prev_start = start_date.replace(year=start_date.year - 1)
                        prev_end = end_date.replace(year=end_date.year - 1)
                    
                    prev_revenue_trend = bookings.filter(
                        appointment_date__range=[prev_start, prev_end],
                        status='completed'
                    ).values('appointment_date').annotate(
                        revenue=Sum('total_price'),
                        bookings=Count('id')
                    ).order_by('appointment_date')
                    
                    analytics_data['growth_metrics'] = PremiumAnalytics.calculate_growth_metrics(
                        list(revenue_trend), list(prev_revenue_trend)
                    )
                
            except Exception as chart_error:
                logger.error(f"Chart generation error: {str(chart_error)}")
                # Don't fail the entire request if charts fail
                analytics_data['chart_error'] = 'Chart generation temporarily unavailable'
        
        return Response(analytics_data)
        
    except Exception as e:
        logger.error(f"Analytics error for user {request.user.id}: {str(e)}")
        return Response({
            'error': 'Analytics data unavailable',
            'error_code': 'ANALYTICS_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def bulk_update_bookings(request):
    """Bulk update multiple bookings"""
    booking_ids = request.data.get('booking_ids', [])
    update_data = request.data.get('update_data', {})
    
    if not booking_ids or not update_data:
        return Response({
            'error': 'booking_ids and update_data are required',
            'error_code': 'MISSING_FIELDS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate that all bookings belong to the user's business
        bookings = Booking.objects.filter(
            id__in=booking_ids,
            business=request.user.business_profile
        )
        
        if bookings.count() != len(booking_ids):
            return Response({
                'error': 'Some bookings not found or access denied',
                'error_code': 'INVALID_BOOKINGS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform bulk update
        updated_count = bookings.update(**update_data)
        
        return Response({
            'message': f'{updated_count} bookings updated successfully',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Bulk update error: {str(e)}")
        return Response({
            'error': 'Bulk update failed',
            'error_code': 'BULK_UPDATE_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def bulk_delete_services(request):
    """Bulk delete multiple services"""
    service_ids = request.data.get('service_ids', [])
    
    if not service_ids:
        return Response({
            'error': 'service_ids is required',
            'error_code': 'MISSING_FIELDS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check for active bookings
        active_bookings = Booking.objects.filter(
            service_id__in=service_ids,
            status__in=['pending', 'confirmed'],
            appointment_date__gte=timezone.now().date()
        ).exists()
        
        if active_bookings:
            return Response({
                'error': 'Cannot delete services with active bookings',
                'error_code': 'ACTIVE_BOOKINGS_EXIST'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform soft delete (mark as inactive)
        deleted_count = Service.objects.filter(
            id__in=service_ids,
            business=request.user.business_profile
        ).update(is_active=False)
        
        return Response({
            'message': f'{deleted_count} services deactivated successfully',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Bulk delete error: {str(e)}")
        return Response({
            'error': 'Bulk delete failed',
            'error_code': 'BULK_DELETE_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def bulk_update_services(request):
    """Bulk update multiple services"""
    service_ids = request.data.get('service_ids', [])
    update_data = request.data.get('update_data', {})
    
    if not service_ids or not update_data:
        return Response({
            'error': 'service_ids and update_data are required',
            'error_code': 'MISSING_FIELDS'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate that all services belong to the user's business
        services = Service.objects.filter(
            id__in=service_ids,
            business=request.user.business_profile
        )
        
        if services.count() != len(service_ids):
            return Response({
                'error': 'Some services not found or access denied',
                'error_code': 'SERVICES_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Security: Sanitize update data
        sanitized_data = SecurityValidator.sanitize_bulk_data(update_data)
        
        # Validate allowed fields for bulk update
        allowed_fields = {'is_active', 'price', 'name', 'description', 'category', 'duration'}
        sanitized_data = {k: v for k, v in sanitized_data.items() if k in allowed_fields}
        
        if not sanitized_data:
            return Response({
                'error': 'No valid update fields provided',
                'error_code': 'INVALID_UPDATE_FIELDS'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform bulk update
        updated_count = services.update(**sanitized_data)
        
        # Log the bulk update action
        AuditLogger.log_security_event(
            'BULK_UPDATE_SERVICES',
            request.user.id,
            request.META.get('REMOTE_ADDR'),
            {
                'updated_count': updated_count,
                'service_ids': service_ids,
                'update_data': sanitized_data
            }
        )
        
        return Response({
            'message': f'{updated_count} services updated successfully',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Bulk update error: {str(e)}")
        return Response({
            'error': 'Bulk update failed',
            'error_code': 'BULK_UPDATE_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    updated = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    return Response({
        'message': f'{updated} notifications marked as read',
        'updated_count': updated
    })

@api_view(['DELETE'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.delete()
        
        return Response({'message': 'Notification deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_available_slots(request, business_id, service_id):
    """Get available time slots for booking"""
    date = request.query_params.get('date')
    
    if not date:
        return Response({
            'success': False,
            'error': 'Date parameter is required (YYYY-MM-DD format)',
            'error_code': 'MISSING_DATE'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = BookingManager.get_available_slots(business_id, service_id, date)
    return Response(result)


@api_view(['GET'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def subscription_status(request):
    """Get comprehensive subscription status for business owner"""
    status_data = SubscriptionManager.get_subscription_status(request.user)
    return Response(status_data)


@api_view(['GET'])
@permission_classes([RoleBasedPermission])
def user_permissions(request):
    """Get user's role-based permissions"""
    permissions_data = RoleManager.get_user_permissions(request.user)
    return Response({
        'role': request.user.role,
        'permissions': permissions_data
    })


@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def generate_business_qr(request):
    """Generate QR code for business profile"""
    try:
        business_profile = request.user.business_profile
        
        from utils.qr_generator import QRCodeGenerator
        qr_file = QRCodeGenerator.generate_business_qr(business_profile)
        
        if qr_file:
            business_profile.qr_code.save(qr_file.name, qr_file, save=True)
            
            return Response({
                'message': 'QR code generated successfully',
                'qr_code_url': business_profile.qr_code.url if business_profile.qr_code else None
            })
        else:
            return Response({
                'error': 'Failed to generate QR code',
                'error_code': 'QR_GENERATION_FAILED'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        return Response({
            'error': 'QR code generation failed',
            'error_code': 'QR_GENERATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def generate_service_qr(request, service_id):
    """Generate QR code for specific service"""
    try:
        service = Service.objects.get(
            id=service_id,
            business=request.user.business_profile
        )
        
        from utils.qr_generator import QRCodeGenerator
        qr_svg = QRCodeGenerator.generate_qr_svg(
            f"https://your-domain.com/book/{service.business.id}/service/{service.id}",
            f"Book {service.name}"
        )
        
        if qr_svg:
            return Response({
                'message': 'Service QR code generated successfully',
                'qr_svg': qr_svg,
                'service_name': service.name,
                'booking_url': f"https://your-domain.com/book/{service.business.id}/service/{service.id}"
            })
        else:
            return Response({
                'error': 'Failed to generate service QR code',
                'error_code': 'QR_GENERATION_FAILED'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Service.DoesNotExist:
        return Response({
            'error': 'Service not found',
            'error_code': 'SERVICE_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Service QR generation error: {str(e)}")
        return Response({
            'error': 'Service QR code generation failed',
            'error_code': 'QR_GENERATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsBusinessOwner, IsVerifiedUser])
def booking_qr_code(request, booking_id):
    """Get QR code for a specific booking"""
    try:
        booking = Booking.objects.get(
            id=booking_id,
            business=request.user.business_profile
        )
        
        if not booking.qr_code:
            # Generate QR code if it doesn't exist
            from utils.qr_generator import QRCodeGenerator
            qr_file = QRCodeGenerator.generate_booking_qr(booking)
            if qr_file:
                booking.qr_code.save(qr_file.name, qr_file, save=True)
        
        return Response({
            'booking_id': str(booking.booking_id),
            'qr_code_url': booking.qr_code.url if booking.qr_code else None,
            'customer_name': booking.customer.name,
            'service_name': booking.service.name,
            'appointment_date': booking.appointment_date,
            'appointment_time': booking.appointment_time
        })
        
    except Booking.DoesNotExist:
        return Response({
            'error': 'Booking not found',
            'error_code': 'BOOKING_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Booking QR retrieval error: {str(e)}")
        return Response({
            'error': 'Failed to retrieve booking QR code',
            'error_code': 'QR_RETRIEVAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
