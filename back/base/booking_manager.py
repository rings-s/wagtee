from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class BookingManager:
    """Manage customer bookings without registration requirement"""
    
    @classmethod
    def create_anonymous_booking(cls, booking_data: Dict) -> Dict:
        """
        Create booking for customer without requiring registration
        
        Args:
            booking_data: Dictionary containing booking information
            
        Returns:
            Dictionary with booking result and details
        """
        try:
            with transaction.atomic():
                # Validate required fields
                required_fields = [
                    'business_id', 'service_id', 'customer_name', 
                    'customer_phone', 'appointment_date', 'appointment_time'
                ]
                
                for field in required_fields:
                    if field not in booking_data or not booking_data[field]:
                        return {
                            'success': False,
                            'error': f'Missing required field: {field}',
                            'error_code': 'MISSING_FIELD'
                        }
                
                # Import models
                from .models import Service, Customer, Booking
                from accounts.models import BusinessProfile
                
                # Validate business and service
                try:
                    business = BusinessProfile.objects.get(
                        id=booking_data['business_id'],
                        is_active=True
                    )
                    service = Service.objects.get(
                        id=booking_data['service_id'],
                        business=business,
                        is_active=True
                    )
                except (BusinessProfile.DoesNotExist, Service.DoesNotExist):
                    return {
                        'success': False,
                        'error': 'Business or service not found',
                        'error_code': 'NOT_FOUND'
                    }
                
                # Validate phone number format
                phone = booking_data['customer_phone'].strip()
                if not phone.startswith('+966') or len(phone) != 13:
                    return {
                        'success': False,
                        'error': 'Phone number must be in Saudi format: +966xxxxxxxxx',
                        'error_code': 'INVALID_PHONE'
                    }
                
                # Parse and validate appointment date/time
                try:
                    if isinstance(booking_data['appointment_date'], str):
                        appointment_date = datetime.strptime(
                            booking_data['appointment_date'], '%Y-%m-%d'
                        ).date()
                    else:
                        appointment_date = booking_data['appointment_date']
                    
                    if isinstance(booking_data['appointment_time'], str):
                        appointment_time = datetime.strptime(
                            booking_data['appointment_time'], '%H:%M'
                        ).time()
                    else:
                        appointment_time = booking_data['appointment_time']
                        
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid date or time format',
                        'error_code': 'INVALID_DATE_TIME'
                    }
                
                # Validate appointment is in the future
                appointment_datetime = datetime.combine(appointment_date, appointment_time)
                if appointment_datetime <= timezone.now():
                    return {
                        'success': False,
                        'error': 'Appointment must be in the future',
                        'error_code': 'PAST_APPOINTMENT'
                    }
                
                # Check business hours
                availability_check = cls._check_business_availability(
                    business, appointment_date, appointment_time
                )
                if not availability_check['available']:
                    return {
                        'success': False,
                        'error': availability_check['reason'],
                        'error_code': 'NOT_AVAILABLE'
                    }
                
                # Check for conflicts
                conflict_check = cls._check_booking_conflicts(
                    business, service, appointment_date, appointment_time
                )
                if conflict_check['has_conflict']:
                    return {
                        'success': False,
                        'error': conflict_check['reason'],
                        'error_code': 'TIME_CONFLICT'
                    }
                
                # Get or create customer
                customer, created = Customer.objects.get_or_create(
                    phone_number=phone,
                    name=booking_data['customer_name'].strip(),
                    defaults={
                        'email': booking_data.get('customer_email', '').strip()
                    }
                )
                
                # Create booking
                booking = Booking.objects.create(
                    business=business,
                    service=service,
                    customer=customer,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    total_price=service.price,
                    notes=booking_data.get('notes', ''),
                    booking_method='online',
                    status='pending'
                )
                
                # Send confirmation notifications
                cls._send_booking_notifications(booking)
                
                return {
                    'success': True,
                    'booking_id': str(booking.booking_id),
                    'booking': {
                        'id': booking.id,
                        'booking_id': str(booking.booking_id),
                        'business_name': business.user.business_name,
                        'service_name': service.name,
                        'customer_name': customer.name,
                        'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                        'appointment_time': appointment_time.strftime('%H:%M'),
                        'total_price': float(service.price),
                        'status': booking.status
                    }
                }
                
        except Exception as e:
            logger.error(f"Anonymous booking creation failed: {str(e)}")
            return {
                'success': False,
                'error': 'Booking creation failed. Please try again.',
                'error_code': 'CREATION_ERROR'
            }
    
    @classmethod
    def get_booking_by_id(cls, booking_id: str) -> Optional[Dict]:
        """Get booking details by booking ID (for customers without accounts)"""
        try:
            from .models import Booking
            
            booking = Booking.objects.select_related(
                'business__user', 'service', 'customer'
            ).get(booking_id=booking_id)
            
            return {
                'id': booking.id,
                'booking_id': str(booking.booking_id),
                'business_name': booking.business.user.business_name,
                'business_address': booking.business.address,
                'business_phone': booking.business.user.phone_number,
                'service_name': booking.service.name,
                'service_name_ar': booking.service.name_ar,
                'customer_name': booking.customer.name,
                'customer_phone': booking.customer.phone_number,
                'appointment_date': booking.appointment_date.strftime('%Y-%m-%d'),
                'appointment_time': booking.appointment_time.strftime('%H:%M'),
                'total_price': float(booking.total_price),
                'status': booking.status,
                'notes': booking.notes,
                'created_at': booking.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Booking lookup failed: {str(e)}")
            return None
    
    @classmethod
    def cancel_booking(cls, booking_id: str, phone_number: str, reason: str = '') -> Dict:
        """Cancel booking using booking ID and phone verification"""
        try:
            from .models import Booking
            
            booking = Booking.objects.select_related(
                'business__user', 'service', 'customer'
            ).get(
                booking_id=booking_id,
                customer__phone_number=phone_number,
                status__in=['pending', 'confirmed']
            )
            
            # Check if cancellation is allowed (e.g., not too close to appointment)
            appointment_datetime = datetime.combine(
                booking.appointment_date, 
                booking.appointment_time
            )
            
            # Allow cancellation up to 2 hours before appointment
            if appointment_datetime <= timezone.now() + timedelta(hours=2):
                return {
                    'success': False,
                    'error': 'Cannot cancel booking less than 2 hours before appointment',
                    'error_code': 'TOO_LATE_TO_CANCEL'
                }
            
            # Update booking status
            booking.status = 'cancelled'
            booking.notes = f"{booking.notes}\nCancellation reason: {reason}".strip()
            booking.save()
            
            # Send cancellation notifications
            cls._send_cancellation_notifications(booking, reason)
            
            return {
                'success': True,
                'message': 'Booking cancelled successfully',
                'booking_id': str(booking.booking_id)
            }
            
        except Booking.DoesNotExist:
            return {
                'success': False,
                'error': 'Booking not found or cannot be cancelled',
                'error_code': 'BOOKING_NOT_FOUND'
            }
        except Exception as e:
            logger.error(f"Booking cancellation failed: {str(e)}")
            return {
                'success': False,
                'error': 'Cancellation failed. Please try again.',
                'error_code': 'CANCELLATION_ERROR'
            }
    
    @classmethod
    def get_available_slots(cls, business_id: int, service_id: int, date: str) -> Dict:
        """Get available time slots for a specific business, service, and date"""
        try:
            from .models import Service, Booking, BusinessHours
            from accounts.models import BusinessProfile
            
            # Validate inputs
            try:
                business = BusinessProfile.objects.get(id=business_id, is_active=True)
                service = Service.objects.get(id=service_id, business=business, is_active=True)
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
            except (BusinessProfile.DoesNotExist, Service.DoesNotExist, ValueError):
                return {
                    'success': False,
                    'error': 'Invalid business, service, or date',
                    'available_slots': []
                }
            
            # Check if date is in the future
            if target_date <= timezone.now().date():
                return {
                    'success': False,
                    'error': 'Date must be in the future',
                    'available_slots': []
                }
            
            # Get business hours for the day
            day_name = target_date.strftime('%A').lower()
            
            try:
                business_hours = BusinessHours.objects.get(
                    business=business,
                    day=day_name
                )
                
                if business_hours.is_closed:
                    return {
                        'success': True,
                        'message': 'Business is closed on this day',
                        'available_slots': []
                    }
                    
            except BusinessHours.DoesNotExist:
                # Default hours if not set
                business_hours = None
            
            # Generate time slots
            available_slots = cls._generate_time_slots(
                business, service, target_date, business_hours
            )
            
            return {
                'success': True,
                'date': date,
                'business_name': business.user.business_name,
                'service_name': service.name,
                'available_slots': available_slots
            }
            
        except Exception as e:
            logger.error(f"Available slots lookup failed: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get available slots',
                'available_slots': []
            }
    
    @classmethod
    def _check_business_availability(cls, business, date, time) -> Dict:
        """Check if business is open at the requested time"""
        try:
            from .models import BusinessHours
            
            day_name = date.strftime('%A').lower()
            
            try:
                hours = BusinessHours.objects.get(business=business, day=day_name)
                
                if hours.is_closed:
                    return {
                        'available': False,
                        'reason': 'Business is closed on this day'
                    }
                
                if time < hours.open_time or time > hours.close_time:
                    return {
                        'available': False,
                        'reason': f'Business is closed at {time.strftime("%H:%M")}'
                    }
                    
            except BusinessHours.DoesNotExist:
                # If no specific hours set, assume open 9 AM to 9 PM
                if time.hour < 9 or time.hour >= 21:
                    return {
                        'available': False,
                        'reason': 'Outside business hours'
                    }
            
            return {'available': True, 'reason': ''}
            
        except Exception as e:
            logger.error(f"Business availability check failed: {str(e)}")
            return {'available': False, 'reason': 'Unable to check availability'}
    
    @classmethod
    def _check_booking_conflicts(cls, business, service, date, time) -> Dict:
        """Check for booking conflicts"""
        try:
            from .models import Booking
            
            # Check for existing bookings at the same time
            conflicts = Booking.objects.filter(
                business=business,
                appointment_date=date,
                appointment_time=time,
                status__in=['pending', 'confirmed', 'in_progress']
            )
            
            if conflicts.exists():
                return {
                    'has_conflict': True,
                    'reason': 'Time slot is already booked'
                }
            
            # Check for overlapping bookings based on service duration
            service_duration = service.duration
            start_time = datetime.combine(date, time)
            end_time = start_time + service_duration
            
            overlapping_bookings = Booking.objects.filter(
                business=business,
                appointment_date=date,
                status__in=['pending', 'confirmed', 'in_progress']
            )
            
            for booking in overlapping_bookings:
                booking_start = datetime.combine(date, booking.appointment_time)
                booking_end = booking_start + booking.service.duration
                
                # Check for overlap
                if (start_time < booking_end and end_time > booking_start):
                    return {
                        'has_conflict': True,
                        'reason': 'Time slot conflicts with another booking'
                    }
            
            return {'has_conflict': False, 'reason': ''}
            
        except Exception as e:
            logger.error(f"Conflict check failed: {str(e)}")
            return {'has_conflict': True, 'reason': 'Unable to check conflicts'}
    
    @classmethod
    def _generate_time_slots(cls, business, service, date, business_hours) -> list:
        """Generate available time slots for the day"""
        try:
            from .models import Booking
            
            # Default business hours
            if business_hours:
                start_time = business_hours.open_time
                end_time = business_hours.close_time
            else:
                start_time = datetime.strptime('09:00', '%H:%M').time()
                end_time = datetime.strptime('21:00', '%H:%M').time()
            
            # Generate 30-minute slots
            slots = []
            current_time = datetime.combine(date, start_time)
            end_datetime = datetime.combine(date, end_time)
            
            while current_time < end_datetime:
                slot_time = current_time.time()
                
                # Check if slot is available
                conflict_check = cls._check_booking_conflicts(
                    business, service, date, slot_time
                )
                
                if not conflict_check['has_conflict']:
                    # Check if it's not in the past
                    if datetime.combine(date, slot_time) > timezone.now():
                        slots.append(slot_time.strftime('%H:%M'))
                
                current_time += timedelta(minutes=30)
            
            return slots
            
        except Exception as e:
            logger.error(f"Time slot generation failed: {str(e)}")
            return []
    
    @classmethod
    def _send_booking_notifications(cls, booking):
        """Send booking notifications to customer and business"""
        try:
            from utils.notification_manager import NotificationManager
            
            # Send confirmation to customer
            NotificationManager.send_booking_confirmation(booking)
            
            # Send new booking notification to business
            NotificationManager.send_new_booking_notification(booking)
            
        except Exception as e:
            logger.error(f"Failed to send booking notifications: {str(e)}")
    
    @classmethod
    def _send_cancellation_notifications(cls, booking, reason):
        """Send cancellation notifications"""
        try:
            from utils.notification_manager import NotificationManager
            # Implementation would be similar to other notifications
            # For now, just log the cancellation
            logger.info(f"Booking {booking.booking_id} cancelled: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to send cancellation notifications: {str(e)}")