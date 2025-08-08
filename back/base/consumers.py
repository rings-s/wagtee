# consumers.py - WebSocket consumers for real-time features
import json
import logging
from datetime import datetime
from typing import Dict, List
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Booking, Service, Customer, Notification
from accounts.subscription_manager import SubscriptionManager
from .security import RateLimiter, AuditLogger

User = get_user_model()
logger = logging.getLogger(__name__)

class BookingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time booking updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (requires authentication middleware)
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return
        
        # Check subscription access
        has_access = await self.check_websocket_access()
        if not has_access:
            await self.close(code=4002)  # Payment required
            return
        
        # Join business-specific group
        self.business_id = await self.get_business_id()
        if not self.business_id:
            await self.close(code=4003)  # No business profile
            return
        
        self.room_group_name = f"booking_{self.business_id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection
        await self.log_websocket_event('WEBSOCKET_CONNECT', {
            'business_id': self.business_id,
            'group': self.room_group_name
        })
        
        # Send initial data
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Log disconnection
            await self.log_websocket_event('WEBSOCKET_DISCONNECT', {
                'close_code': close_code,
                'business_id': getattr(self, 'business_id', None)
            })
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Rate limiting for WebSocket messages
            client_ip = await self.get_client_ip()
            is_limited, _ = await sync_to_async(RateLimiter.is_rate_limited)(
                'api_general', f"ws_{self.user.id}"
            )
            
            if is_limited:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'تم تجاوز الحد المسموح من الطلبات'
                }))
                return
            
            # Increment rate limit counter
            await sync_to_async(RateLimiter.increment_counter)(
                'api_general', f"ws_{self.user.id}"
            )
            
            # Handle different message types
            if message_type == 'booking_update':
                await self.handle_booking_update(data)
            elif message_type == 'booking_status_change':
                await self.handle_booking_status_change(data)
            elif message_type == 'subscribe_notifications':
                await self.handle_notification_subscription(data)
            else:
                await self.send_error('نوع الرسالة غير معروف')
                
        except json.JSONDecodeError:
            await self.send_error('تنسيق الرسالة غير صحيح')
        except Exception as e:
            logger.error(f"WebSocket message handling error: {e}")
            await self.send_error('حدث خطأ في معالجة الرسالة')
    
    async def booking_update(self, event):
        """Send booking update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'booking_update',
            'booking': event['booking'],
            'action': event['action'],
            'timestamp': datetime.now().isoformat()
        }))
    
    async def booking_status_changed(self, event):
        """Send booking status change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'booking_status_changed',
            'booking_id': event['booking_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'timestamp': datetime.now().isoformat()
        }))
    
    async def notification_received(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'timestamp': datetime.now().isoformat()
        }))
    
    async def analytics_update(self, event):
        """Send analytics update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'analytics': event['analytics'],
            'timestamp': datetime.now().isoformat()
        }))
    
    @database_sync_to_async
    def check_websocket_access(self) -> bool:
        """Check if user has WebSocket access"""
        try:
            # Check subscription
            subscription = SubscriptionManager.get_user_subscription(self.user)
            if not subscription or not subscription.get('active', False):
                return False
            
            # Check if real-time features are included
            features = subscription.get('features', [])
            return 'realtime_updates' in features or subscription.get('tier') in ['standard', 'premium']
        except:
            return False
    
    @database_sync_to_async
    def get_business_id(self) -> str:
        """Get business ID for the user"""
        try:
            return str(self.user.business_profile.id)
        except:
            return None
    
    async def get_client_ip(self) -> str:
        """Get client IP from WebSocket scope"""
        headers = dict(self.scope.get('headers', []))
        x_forwarded_for = headers.get(b'x-forwarded-for')
        if x_forwarded_for:
            return x_forwarded_for.decode().split(',')[0].strip()
        return self.scope.get('client', ['unknown', None])[0]
    
    async def send_error(self, message: str):
        """Send error message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def send_initial_data(self):
        """Send initial data when connection is established"""
        try:
            # Get recent bookings
            bookings = await self.get_recent_bookings()
            
            # Get pending notifications
            notifications = await self.get_pending_notifications()
            
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'bookings': bookings,
                'notifications': notifications,
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    @database_sync_to_async
    def get_recent_bookings(self) -> List[Dict]:
        """Get recent bookings for the business"""
        try:
            bookings = Booking.objects.filter(
                business=self.user.business_profile
            ).select_related('service', 'customer').order_by('-created_at')[:10]
            
            return [{
                'id': booking.id,
                'customer_name': booking.customer.name if booking.customer else booking.customer_name,
                'service_name': booking.service.name,
                'appointment_date': booking.appointment_date.isoformat(),
                'appointment_time': booking.appointment_time.strftime('%H:%M'),
                'status': booking.status,
                'total_price': float(booking.total_price) if booking.total_price else None
            } for booking in bookings]
        except Exception as e:
            logger.error(f"Error getting recent bookings: {e}")
            return []
    
    @database_sync_to_async
    def get_pending_notifications(self) -> List[Dict]:
        """Get pending notifications for the user"""
        try:
            notifications = Notification.objects.filter(
                user=self.user,
                is_read=False
            ).order_by('-created_at')[:5]
            
            return [{
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat()
            } for notification in notifications]
        except Exception as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []
    
    async def handle_booking_update(self, data: Dict):
        """Handle booking update request"""
        try:
            booking_id = data.get('booking_id')
            if not booking_id:
                await self.send_error('معرف الحجز مطلوب')
                return
            
            # Verify booking belongs to user's business
            booking = await self.get_user_booking(booking_id)
            if not booking:
                await self.send_error('الحجز غير موجود')
                return
            
            # Process update
            update_data = data.get('data', {})
            updated_booking = await self.update_booking(booking_id, update_data)
            
            if updated_booking:
                # Broadcast update to all connected clients in the group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'booking_update',
                        'booking': updated_booking,
                        'action': 'updated'
                    }
                )
        except Exception as e:
            logger.error(f"Error handling booking update: {e}")
            await self.send_error('حدث خطأ في تحديث الحجز')
    
    async def handle_booking_status_change(self, data: Dict):
        """Handle booking status change request"""
        try:
            booking_id = data.get('booking_id')
            new_status = data.get('status')
            
            if not booking_id or not new_status:
                await self.send_error('معرف الحجز والحالة الجديدة مطلوبان')
                return
            
            # Update booking status
            result = await self.change_booking_status(booking_id, new_status)
            
            if result:
                # Broadcast status change
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'booking_status_changed',
                        'booking_id': booking_id,
                        'old_status': result['old_status'],
                        'new_status': new_status
                    }
                )
        except Exception as e:
            logger.error(f"Error handling booking status change: {e}")
            await self.send_error('حدث خطأ في تغيير حالة الحجز')
    
    async def handle_notification_subscription(self, data: Dict):
        """Handle notification subscription request"""
        try:
            notification_types = data.get('types', [])
            
            # Store subscription preferences in cache
            cache_key = f"notification_subscription_{self.user.id}"
            await sync_to_async(cache.set)(cache_key, notification_types, 86400)  # 24 hours
            
            await self.send(text_data=json.dumps({
                'type': 'subscription_updated',
                'subscribed_types': notification_types,
                'message': 'تم تحديث اشتراك الإشعارات'
            }))
        except Exception as e:
            logger.error(f"Error handling notification subscription: {e}")
            await self.send_error('حدث خطأ في تحديث اشتراك الإشعارات')
    
    @database_sync_to_async
    def get_user_booking(self, booking_id: int):
        """Get booking if it belongs to user's business"""
        try:
            return Booking.objects.get(
                id=booking_id,
                business=self.user.business_profile
            )
        except Booking.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_booking(self, booking_id: int, update_data: Dict) -> Dict:
        """Update booking with provided data"""
        try:
            booking = Booking.objects.get(
                id=booking_id,
                business=self.user.business_profile
            )
            
            # Sanitize update data
            allowed_fields = ['notes', 'appointment_date', 'appointment_time']
            for field, value in update_data.items():
                if field in allowed_fields:
                    setattr(booking, field, value)
            
            booking.save()
            
            return {
                'id': booking.id,
                'customer_name': booking.customer.name if booking.customer else booking.customer_name,
                'service_name': booking.service.name,
                'appointment_date': booking.appointment_date.isoformat(),
                'appointment_time': booking.appointment_time.strftime('%H:%M'),
                'status': booking.status,
                'notes': booking.notes
            }
        except Exception as e:
            logger.error(f"Error updating booking: {e}")
            return None
    
    @database_sync_to_async
    def change_booking_status(self, booking_id: int, new_status: str) -> Dict:
        """Change booking status"""
        try:
            booking = Booking.objects.get(
                id=booking_id,
                business=self.user.business_profile
            )
            
            old_status = booking.status
            booking.status = new_status
            booking.save()
            
            return {
                'old_status': old_status,
                'new_status': new_status
            }
        except Exception as e:
            logger.error(f"Error changing booking status: {e}")
            return None
    
    async def log_websocket_event(self, event_type: str, details: Dict):
        """Log WebSocket events for security auditing"""
        await sync_to_async(AuditLogger.log_security_event)(
            event_type,
            self.user.id if hasattr(self, 'user') and self.user else None,
            await self.get_client_ip(),
            details
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Handle WebSocket connection for notifications"""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Join user-specific notification group
        self.room_group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming notification WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                await self.mark_notification_read(data.get('notification_id'))
            elif message_type == 'mark_all_read':
                await self.mark_all_notifications_read()
                
        except Exception as e:
            logger.error(f"Error handling notification message: {e}")
    
    async def send_notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id: int):
        """Mark specific notification as read"""
        try:
            Notification.objects.filter(
                id=notification_id,
                user=self.user
            ).update(is_read=True)
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user"""
        try:
            Notification.objects.filter(
                user=self.user,
                is_read=False
            ).update(is_read=True)
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")


# WebSocket utility functions for broadcasting updates
class WebSocketBroadcaster:
    """Utility class for broadcasting WebSocket messages"""
    
    @staticmethod
    async def broadcast_booking_update(business_id: str, booking_data: Dict, action: str):
        """Broadcast booking update to all connected clients"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        if channel_layer:
            await channel_layer.group_send(
                f"booking_{business_id}",
                {
                    'type': 'booking_update',
                    'booking': booking_data,
                    'action': action
                }
            )
    
    @staticmethod
    async def broadcast_notification(user_id: int, notification_data: Dict):
        """Broadcast notification to specific user"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        if channel_layer:
            await channel_layer.group_send(
                f"notifications_{user_id}",
                {
                    'type': 'send_notification',
                    'notification': notification_data
                }
            )
    
    @staticmethod
    async def broadcast_analytics_update(business_id: str, analytics_data: Dict):
        """Broadcast analytics update to business"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        if channel_layer:
            await channel_layer.group_send(
                f"booking_{business_id}",
                {
                    'type': 'analytics_update',
                    'analytics': analytics_data
                }
            )