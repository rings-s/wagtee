from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """Comprehensive notification management system"""
    
    # Arabic and English templates
    TEMPLATES = {
        'booking_confirmation': {
            'ar': 'مرحباً {customer_name}، تم تأكيد حجزك في {business_name} يوم {date} الساعة {time}. خدمة: {service_name}. المبلغ: {price} ريال. رقم الحجز: {booking_id}',
            'en': 'Hello {customer_name}, your booking at {business_name} is confirmed for {date} at {time}. Service: {service_name}. Amount: {price} SAR. Booking ID: {booking_id}'
        },
        'booking_reminder': {
            'ar': 'تذكير: لديك موعد في {business_name} غداً الساعة {time}. خدمة: {service_name}. العنوان: {address}. للإلغاء اتصل: {phone}',
            'en': 'Reminder: You have an appointment at {business_name} tomorrow at {time}. Service: {service_name}. Address: {address}. To cancel call: {phone}'
        },
        'booking_today': {
            'ar': 'موعدك اليوم! في {business_name} الساعة {time}. خدمة: {service_name}. العنوان: {address}. رقم الحجز: {booking_id}',
            'en': 'Your appointment is today! At {business_name} at {time}. Service: {service_name}. Address: {address}. Booking ID: {booking_id}'
        },
        'business_daily_summary': {
            'ar': 'ملخص اليوم - {business_name}:\n📅 مواعيد اليوم: {today_bookings}\n⏰ المواعيد القادمة: {upcoming_count}\n💰 إجمالي الإيرادات: {revenue} ريال\n📊 معدل التقييم: {rating}/5',
            'en': 'Daily Summary - {business_name}:\n📅 Today\'s appointments: {today_bookings}\n⏰ Upcoming: {upcoming_count}\n💰 Total revenue: {revenue} SAR\n📊 Rating: {rating}/5'
        },
        'subscription_reminder': {
            'ar': 'تنبيه: اشتراكك في وقتي سينتهي خلال {days} أيام. للتجديد ادخل على التطبيق. خطتك الحالية: {tier}',
            'en': 'Alert: Your Wagtee subscription expires in {days} days. Please renew in the app. Current plan: {tier}'
        },
        'subscription_expired': {
            'ar': 'انتهى اشتراكك في وقتي. لن تتمكن من إدارة مواعيدك حتى التجديد. اضغط هنا للتجديد: {renewal_link}',
            'en': 'Your Wagtee subscription has expired. You cannot manage appointments until renewal. Renew here: {renewal_link}'
        },
        'new_booking_business': {
            'ar': 'حجز جديد! 🎉\nالعميل: {customer_name}\nالخدمة: {service_name}\nالموعد: {date} - {time}\nالمبلغ: {price} ريال\nرقم الحجز: {booking_id}',
            'en': 'New booking! 🎉\nCustomer: {customer_name}\nService: {service_name}\nAppointment: {date} - {time}\nAmount: {price} SAR\nBooking ID: {booking_id}'
        },
        'booking_cancelled': {
            'ar': 'تم إلغاء حجزك في {business_name}. الخدمة: {service_name}. الموعد: {date} - {time}. سبب الإلغاء: {reason}',
            'en': 'Your booking at {business_name} has been cancelled. Service: {service_name}. Appointment: {date} - {time}. Reason: {reason}'
        },
        'review_request': {
            'ar': 'شكراً لزيارتك {business_name}! يرجى تقييم خدمتنا: {review_link}. رأيك يهمنا 🌟',
            'en': 'Thank you for visiting {business_name}! Please rate our service: {review_link}. Your feedback matters 🌟'
        }
    }
    
    @classmethod
    def send_booking_confirmation(cls, booking, language='ar') -> bool:
        """Send booking confirmation to customer"""
        try:
            from .whatsapp import send_whatsapp_message
            
            template = cls.TEMPLATES['booking_confirmation'][language]
            message = template.format(
                customer_name=booking.customer.name,
                business_name=booking.business.user.business_name,
                date=booking.appointment_date.strftime('%Y-%m-%d'),
                time=booking.appointment_time.strftime('%H:%M'),
                service_name=booking.service.name_ar if language == 'ar' else booking.service.name,
                price=booking.total_price,
                booking_id=booking.booking_id
            )
            
            result = send_whatsapp_message(
                booking.customer.phone_number,
                'booking_confirmation',
                booking_details={
                    'business_name': booking.business.user.business_name,
                    'service_name': booking.service.name_ar if language == 'ar' else booking.service.name,
                    'appointment_date': booking.appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': booking.appointment_time.strftime('%H:%M'),
                    'total_price': str(booking.total_price)
                }
            )
            
            # Create notification record
            cls._create_notification(
                user=None,
                customer=booking.customer,
                notification_type='booking_confirmation',
                title='Booking Confirmation' if language == 'en' else 'تأكيد الحجز',
                message=message,
                sent_via_whatsapp=result.get('success', False)
            )
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
            return False
    
    @classmethod
    def send_booking_reminder(cls, booking, language='ar') -> bool:
        """Send booking reminder to customer (24 hours before)"""
        try:
            from .whatsapp import send_whatsapp_message
            
            template = cls.TEMPLATES['booking_reminder'][language]
            message = template.format(
                customer_name=booking.customer.name,
                business_name=booking.business.user.business_name,
                time=booking.appointment_time.strftime('%H:%M'),
                service_name=booking.service.name_ar if language == 'ar' else booking.service.name,
                address=booking.business.address_ar if language == 'ar' else booking.business.address,
                phone=booking.business.user.phone_number
            )
            
            result = send_whatsapp_message(
                booking.customer.phone_number,
                'booking_reminder',
                booking_details={
                    'business_name': booking.business.user.business_name,
                    'service_name': booking.service.name_ar if language == 'ar' else booking.service.name,
                    'appointment_time': booking.appointment_time.strftime('%H:%M'),
                    'address': booking.business.address_ar if language == 'ar' else booking.business.address
                }
            )
            
            # Mark reminder as sent
            booking.reminder_sent = True
            booking.save()
            
            cls._create_notification(
                user=None,
                customer=booking.customer,
                notification_type='booking_reminder',
                title='Booking Reminder' if language == 'en' else 'تذكير بالموعد',
                message=message,
                sent_via_whatsapp=result.get('success', False)
            )
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to send booking reminder: {str(e)}")
            return False
    
    @classmethod
    def send_business_daily_summary(cls, business_user, language='ar') -> bool:
        """Send daily summary to business owner"""
        try:
            from .whatsapp import send_whatsapp_message
            from base.models import Booking, Review
            from django.db.models import Sum, Avg
            
            today = timezone.now().date()
            
            # Get today's bookings
            today_bookings = Booking.objects.filter(
                business=business_user.business_profile,
                appointment_date=today
            )
            
            # Get upcoming bookings (next 3 days)
            upcoming_bookings = Booking.objects.filter(
                business=business_user.business_profile,
                appointment_date__gt=today,
                appointment_date__lte=today + timedelta(days=3),
                status__in=['pending', 'confirmed']
            )
            
            # Calculate revenue
            revenue = today_bookings.filter(status='completed').aggregate(
                total=Sum('total_price')
            )['total'] or 0
            
            # Get average rating
            rating = Review.objects.filter(
                booking__business=business_user.business_profile
            ).aggregate(avg=Avg('rating'))['avg'] or 0
            
            template = cls.TEMPLATES['business_daily_summary'][language]
            message = template.format(
                business_name=business_user.business_name,
                today_bookings=today_bookings.count(),
                upcoming_count=upcoming_bookings.count(),
                revenue=revenue,
                rating=round(rating, 1)
            )
            
            result = send_whatsapp_message(
                business_user.phone_number,
                'business_summary',
                summary_data={
                    'today_bookings': today_bookings.count(),
                    'upcoming_count': upcoming_bookings.count(),
                    'revenue': str(revenue),
                    'rating': str(round(rating, 1))
                }
            )
            
            cls._create_notification(
                user=business_user,
                customer=None,
                notification_type='business_summary',
                title='Daily Summary' if language == 'en' else 'ملخص اليوم',
                message=message,
                sent_via_whatsapp=result.get('success', False)
            )
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")
            return False
    
    @classmethod
    def send_subscription_reminder(cls, user, days_remaining, language='ar') -> bool:
        """Send subscription expiry reminder"""
        try:
            from .whatsapp import send_whatsapp_message
            from accounts.models import Subscription
            
            subscription = Subscription.objects.filter(
                user=user, is_active=True
            ).first()
            
            tier = subscription.tier if subscription else 'basic'
            
            template = cls.TEMPLATES['subscription_reminder'][language]
            message = template.format(
                days=days_remaining,
                tier=tier.title()
            )
            
            result = send_whatsapp_message(
                user.phone_number,
                'subscription_reminder',
                subscription_data={
                    'days_remaining': str(days_remaining),
                    'tier': tier
                }
            )
            
            cls._create_notification(
                user=user,
                customer=None,
                notification_type='subscription_expiry',
                title='Subscription Reminder' if language == 'en' else 'تذكير الاشتراك',
                message=message,
                sent_via_whatsapp=result.get('success', False)
            )
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to send subscription reminder: {str(e)}")
            return False
    
    @classmethod
    def send_new_booking_notification(cls, booking, language='ar') -> bool:
        """Notify business owner of new booking"""
        try:
            from .whatsapp import send_whatsapp_message
            
            template = cls.TEMPLATES['new_booking_business'][language]
            message = template.format(
                customer_name=booking.customer.name,
                service_name=booking.service.name_ar if language == 'ar' else booking.service.name,
                date=booking.appointment_date.strftime('%Y-%m-%d'),
                time=booking.appointment_time.strftime('%H:%M'),
                price=booking.total_price,
                booking_id=booking.booking_id
            )
            
            result = send_whatsapp_message(
                booking.business.user.phone_number,
                'new_booking',
                booking_details={
                    'customer_name': booking.customer.name,
                    'service_name': booking.service.name_ar if language == 'ar' else booking.service.name,
                    'appointment_date': booking.appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': booking.appointment_time.strftime('%H:%M'),
                    'total_price': str(booking.total_price)
                }
            )
            
            cls._create_notification(
                user=booking.business.user,
                customer=None,
                notification_type='new_booking',
                title='New Booking' if language == 'en' else 'حجز جديد',
                message=message,
                sent_via_whatsapp=result.get('success', False)
            )
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Failed to send new booking notification: {str(e)}")
            return False
    
    @classmethod
    def _create_notification(cls, user=None, customer=None, notification_type='', 
                           title='', message='', sent_via_whatsapp=False):
        """Create notification record in database"""
        try:
            from base.models import Notification
            
            Notification.objects.create(
                user=user,
                customer=customer,
                notification_type=notification_type,
                title=title,
                message=message,
                sent_via_whatsapp=sent_via_whatsapp
            )
        except Exception as e:
            logger.error(f"Failed to create notification record: {str(e)}")
    
    @classmethod
    def get_pending_reminders(cls):
        """Get bookings that need reminder notifications"""
        try:
            from base.models import Booking
            
            tomorrow = timezone.now().date() + timedelta(days=1)
            
            return Booking.objects.filter(
                appointment_date=tomorrow,
                status__in=['pending', 'confirmed'],
                reminder_sent=False
            ).select_related('customer', 'service', 'business__user')
            
        except Exception as e:
            logger.error(f"Failed to get pending reminders: {str(e)}")
            return []
    
    @classmethod
    def get_businesses_for_daily_summary(cls):
        """Get businesses that should receive daily summary"""
        try:
            from django.contrib.auth import get_user_model
            from accounts.subscription_manager import SubscriptionManager
            
            User = get_user_model()
            
            business_users = User.objects.filter(
                role='business_owner',
                is_active=True,
                is_verified=True
            ).select_related('business_profile')
            
            # Filter by subscription (only active subscriptions get daily summaries)
            eligible_users = []
            for user in business_users:
                if SubscriptionManager.check_feature_access(user, 'whatsapp_reminders'):
                    eligible_users.append(user)
            
            return eligible_users
            
        except Exception as e:
            logger.error(f"Failed to get businesses for daily summary: {str(e)}")
            return []


class NotificationScheduler:
    """Schedule and manage notification sending"""
    
    @classmethod
    def send_daily_reminders(cls):
        """Send all pending reminder notifications"""
        reminders = NotificationManager.get_pending_reminders()
        
        success_count = 0
        for booking in reminders:
            try:
                if NotificationManager.send_booking_reminder(booking):
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to send reminder for booking {booking.id}: {str(e)}")
        
        logger.info(f"Sent {success_count}/{len(reminders)} reminder notifications")
        return success_count
    
    @classmethod
    def send_daily_summaries(cls):
        """Send daily business summaries"""
        businesses = NotificationManager.get_businesses_for_daily_summary()
        
        success_count = 0
        for user in businesses:
            try:
                if NotificationManager.send_business_daily_summary(user):
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to send summary for business {user.id}: {str(e)}")
        
        logger.info(f"Sent {success_count}/{len(businesses)} daily summaries")
        return success_count
    
    @classmethod
    def check_subscription_expiries(cls):
        """Check and notify about subscription expiries"""
        try:
            from django.contrib.auth import get_user_model
            from accounts.models import Subscription
            
            User = get_user_model()
            now = timezone.now()
            
            # Users with subscriptions expiring in 3 days
            expiring_soon = Subscription.objects.filter(
                is_active=True,
                end_date__lte=now + timedelta(days=3),
                end_date__gt=now
            ).select_related('user')
            
            success_count = 0
            for subscription in expiring_soon:
                days_remaining = (subscription.end_date - now).days
                try:
                    if NotificationManager.send_subscription_reminder(
                        subscription.user, 
                        days_remaining
                    ):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send subscription reminder: {str(e)}")
            
            logger.info(f"Sent {success_count}/{len(expiring_soon)} subscription reminders")
            return success_count
            
        except Exception as e:
            logger.error(f"Failed to check subscription expiries: {str(e)}")
            return 0