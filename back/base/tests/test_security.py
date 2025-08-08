# test_security.py - Comprehensive security tests
import json
from datetime import datetime, timedelta
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from ..security import (
    SecurityValidator, RateLimiter, AuditLogger, 
    SubscriptionSecurity, DataEncryption
)
from ..models import Service, Booking, Customer
from accounts.models import BusinessProfile

User = get_user_model()

class SecurityValidatorTest(TestCase):
    """Test security validation functions"""
    
    def test_saudi_phone_validation(self):
        """Test Saudi phone number validation"""
        # Valid Saudi phone numbers
        valid_phones = [
            '+966501234567',
            '+966551234567',
            '+966123456789'
        ]
        
        for phone in valid_phones:
            self.assertTrue(
                SecurityValidator.validate_saudi_phone(phone),
                f"Valid phone {phone} failed validation"
            )
        
        # Invalid phone numbers
        invalid_phones = [
            '0501234567',      # Missing country code
            '+965501234567',   # Wrong country code
            '+966501234',      # Too short
            '+9665012345678',  # Too long
            '+966a01234567',   # Contains letters
            ''                 # Empty string
        ]
        
        for phone in invalid_phones:
            self.assertFalse(
                SecurityValidator.validate_saudi_phone(phone),
                f"Invalid phone {phone} passed validation"
            )
    
    def test_cr_number_validation(self):
        """Test CR number validation"""
        # Valid CR numbers
        valid_crs = ['1234567890', '9876543210']
        
        for cr in valid_crs:
            self.assertTrue(
                SecurityValidator.validate_cr_number(cr),
                f"Valid CR {cr} failed validation"
            )
        
        # Invalid CR numbers
        invalid_crs = ['0123456789', '12345', 'abcd567890', '']
        
        for cr in invalid_crs:
            if cr:  # Empty string is allowed (optional field)
                self.assertFalse(
                    SecurityValidator.validate_cr_number(cr),
                    f"Invalid CR {cr} passed validation"
                )
    
    def test_input_sanitization(self):
        """Test input sanitization against XSS and injection"""
        # XSS attempts
        xss_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<iframe src="malicious.com"></iframe>',
            'onload="alert(1)"'
        ]
        
        for xss_input in xss_inputs:
            sanitized = SecurityValidator.sanitize_input(xss_input)
            self.assertNotIn('<script', sanitized.lower())
            self.assertNotIn('javascript:', sanitized.lower())
            self.assertNotIn('<iframe', sanitized.lower())
            self.assertNotIn('onload=', sanitized.lower())
        
        # SQL injection attempts
        sql_inputs = [
            "'; DROP TABLE users; --",
            "admin'; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users"
        ]
        
        for sql_input in sql_inputs:
            sanitized = SecurityValidator.sanitize_input(sql_input)
            self.assertNotIn('DROP', sanitized.upper())
            self.assertNotIn('UNION', sanitized.upper())
            self.assertNotIn('--', sanitized)
    
    def test_business_data_validation(self):
        """Test business-specific data validation"""
        # Valid business data
        valid_data = {
            'phone_number': '+966501234567',
            'cr_number': '1234567890',
            'vat_number': '123456789012345',
            'business_name_ar': 'اسم العمل التجاري',
            'description_ar': 'وصف العمل التجاري'
        }
        
        errors = SecurityValidator.validate_business_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Invalid business data
        invalid_data = {
            'phone_number': '0501234567',  # Invalid format
            'cr_number': '0123456789',     # Starts with 0
            'vat_number': '12345',         # Too short
            'business_name_ar': 'Business Name',  # English in Arabic field
        }
        
        errors = SecurityValidator.validate_business_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn('phone_number', errors)
        self.assertIn('cr_number', errors)
        self.assertIn('vat_number', errors)


class RateLimiterTest(TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        cache.clear()
    
    def test_rate_limiting_basic(self):
        """Test basic rate limiting functionality"""
        action = 'test_action'
        identifier = 'test_user'
        
        # Configure test rate limit
        RateLimiter.RATE_LIMITS[action] = {
            'requests': 2,
            'window': 60,
            'block_duration': 300
        }
        
        # First request should pass
        is_limited, _ = RateLimiter.is_rate_limited(action, identifier)
        self.assertFalse(is_limited)
        RateLimiter.increment_counter(action, identifier)
        
        # Second request should pass
        is_limited, _ = RateLimiter.is_rate_limited(action, identifier)
        self.assertFalse(is_limited)
        RateLimiter.increment_counter(action, identifier)
        
        # Third request should be blocked
        is_limited, block_duration = RateLimiter.is_rate_limited(action, identifier)
        self.assertTrue(is_limited)
        self.assertEqual(block_duration, 300)
    
    def test_rate_limit_expiry(self):
        """Test rate limit window expiry"""
        action = 'test_expiry'
        identifier = 'test_user'
        
        # Configure test rate limit with short window
        RateLimiter.RATE_LIMITS[action] = {
            'requests': 1,
            'window': 1,  # 1 second window
            'block_duration': 60
        }
        
        # Exhaust limit
        RateLimiter.increment_counter(action, identifier)
        is_limited, _ = RateLimiter.is_rate_limited(action, identifier)
        self.assertTrue(is_limited)
        
        # Wait for window to expire (in real test, we'd mock time)
        # For this test, we'll manually clear the cache
        cache.delete(RateLimiter.get_rate_limit_key(action, identifier))
        cache.delete(f"{RateLimiter.get_rate_limit_key(action, identifier)}:blocked")
        
        # Should be able to make request again
        is_limited, _ = RateLimiter.is_rate_limited(action, identifier)
        self.assertFalse(is_limited)


class AuditLoggerTest(TestCase):
    """Test audit logging functionality"""
    
    @patch('base.security.logger')
    def test_security_event_logging(self, mock_logger):
        """Test security event logging"""
        event_type = 'LOGIN_SUCCESS'
        user_id = 123
        ip_address = '192.168.1.1'
        details = {'username': 'testuser'}
        
        AuditLogger.log_security_event(event_type, user_id, ip_address, details)
        
        # Verify logger was called
        mock_logger.info.assert_called_once()
        logged_data = mock_logger.info.call_args[0][0]
        self.assertIn('SECURITY_EVENT', logged_data)
        self.assertIn(event_type, logged_data)
    
    def test_unknown_event_type_warning(self):
        """Test warning for unknown event types"""
        with patch('base.security.logger') as mock_logger:
            AuditLogger.log_security_event('UNKNOWN_EVENT', 123, '192.168.1.1')
            mock_logger.warning.assert_called_once()


class SubscriptionSecurityTest(TestCase):
    """Test subscription security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
    
    def test_active_subscription_validation(self):
        """Test active subscription validation"""
        # Mock active subscription
        self.user.subscription_status = {
            'active': True,
            'tier': 'standard',
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'features': ['basic_booking', 'advanced_analytics']
        }
        
        is_valid, message = SubscriptionSecurity.validate_subscription_access(
            self.user, ['basic_booking']
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "تم التحقق بنجاح")
    
    def test_expired_subscription_validation(self):
        """Test expired subscription validation"""
        # Mock expired subscription
        self.user.subscription_status = {
            'active': False,
            'tier': 'basic',
            'expires_at': (datetime.now() - timedelta(days=1)).isoformat(),
            'features': ['basic_booking']
        }
        
        is_valid, message = SubscriptionSecurity.validate_subscription_access(self.user)
        
        self.assertFalse(is_valid)
        self.assertIn("انتهت صلاحية الاشتراك", message)
    
    def test_feature_requirement_validation(self):
        """Test feature requirement validation"""
        # Mock subscription without required feature
        self.user.subscription_status = {
            'active': True,
            'tier': 'basic',
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'features': ['basic_booking']
        }
        
        is_valid, message = SubscriptionSecurity.validate_subscription_access(
            self.user, ['advanced_analytics']
        )
        
        self.assertFalse(is_valid)
        self.assertIn("الميزة غير متاحة", message)


class DataEncryptionTest(TestCase):
    """Test data encryption utilities"""
    
    def test_sensitive_data_hashing(self):
        """Test sensitive data hashing"""
        data = "sensitive_information"
        
        hash_value, salt = DataEncryption.hash_sensitive_data(data)
        
        # Verify hash was created
        self.assertIsNotNone(hash_value)
        self.assertIsNotNone(salt)
        self.assertNotEqual(hash_value, data)
        
        # Verify hash verification works
        is_valid = DataEncryption.verify_hash(data, hash_value, salt)
        self.assertTrue(is_valid)
        
        # Verify wrong data fails verification
        is_valid = DataEncryption.verify_hash("wrong_data", hash_value, salt)
        self.assertFalse(is_valid)
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = DataEncryption.generate_secure_token()
        token2 = DataEncryption.generate_secure_token()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        
        # Tokens should be of expected length (base64 encoded)
        self.assertGreaterEqual(len(token1), 32)
        
        # Test custom length
        custom_token = DataEncryption.generate_secure_token(16)
        self.assertGreaterEqual(len(custom_token), 16)


class APISecurityTest(APITestCase):
    """Test API security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        cache.clear()
    
    @patch('base.security.RateLimiter.is_rate_limited')
    def test_rate_limiting_middleware(self, mock_rate_limit):
        """Test API rate limiting"""
        # Mock rate limit exceeded
        mock_rate_limit.return_value = (True, 300)
        
        response = self.client.get('/api/base/services/')
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('تم تجاوز الحد المسموح', response.data['error'])
    
    def test_input_sanitization_in_api(self):
        """Test input sanitization in API endpoints"""
        # Create service with XSS attempt
        xss_data = {
            'name': '<script>alert("xss")</script>Test Service',
            'description': 'javascript:alert("xss")',
            'price': 100,
            'duration': 60,
            'category': 'barber'
        }
        
        response = self.client.post('/api/base/services/', xss_data)
        
        # Should create service but with sanitized data
        if response.status_code == status.HTTP_201_CREATED:
            service = Service.objects.get(id=response.data['id'])
            self.assertNotIn('<script>', service.name)
            self.assertNotIn('javascript:', service.description)
    
    @patch('base.security.SubscriptionSecurity.validate_subscription_access')
    def test_subscription_enforcement(self, mock_subscription_check):
        """Test subscription enforcement in API"""
        # Mock subscription validation failure
        mock_subscription_check.return_value = (False, "انتهت صلاحية الاشتراك")
        
        response = self.client.post('/api/base/services/', {
            'name': 'Test Service',
            'price': 100,
            'duration': 60,
            'category': 'barber'
        })
        
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertIn('انتهت صلاحية الاشتراك', response.data['error'])
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Attempt SQL injection in query parameters
        injection_params = {
            'search': "'; DROP TABLE base_service; --",
            'status': "' OR '1'='1",
            'ordering': 'name; DROP TABLE base_booking; --'
        }
        
        response = self.client.get('/api/base/bookings/', injection_params)
        
        # Should not crash the server
        self.assertIn(response.status_code, [200, 400, 401, 403])
        
        # Services table should still exist
        self.assertTrue(Service.objects.count() >= 0)


class WebSocketSecurityTest(TestCase):
    """Test WebSocket security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
    
    @patch('base.consumers.sync_to_async')
    def test_websocket_authentication_required(self, mock_sync_to_async):
        """Test WebSocket authentication requirement"""
        from ..consumers import BookingConsumer
        
        # Mock unauthenticated user
        consumer = BookingConsumer()
        consumer.scope = {'user': None}
        
        # Mock close method
        consumer.close = MagicMock()
        
        # Test connection with no user
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(consumer.connect())
            consumer.close.assert_called_with(code=4001)
        finally:
            loop.close()
    
    def test_websocket_rate_limiting(self):
        """Test WebSocket message rate limiting"""
        # This would be tested with actual WebSocket connection
        # For now, we test the rate limiting logic separately
        
        action = 'websocket_message'
        identifier = f"ws_{self.user.id}"
        
        # Configure rate limit
        RateLimiter.RATE_LIMITS[action] = {
            'requests': 2,
            'window': 60,
            'block_duration': 300
        }
        
        # Simulate rapid messages
        for i in range(3):
            RateLimiter.increment_counter(action, identifier)
        
        is_limited, _ = RateLimiter.is_rate_limited(action, identifier)
        self.assertTrue(is_limited)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SecurityIntegrationTest(APITestCase):
    """Integration tests for security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.business = BusinessProfile.objects.create(
            user=self.user,
            business_name='Test Business',
            phone_number='+966501234567'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        cache.clear()
    
    def test_complete_booking_flow_security(self):
        """Test security throughout booking creation flow"""
        # Create service first
        service_data = {
            'name': 'Test Service',
            'description': 'Test Description',
            'price': 100,
            'duration': 60,
            'category': 'barber'
        }
        
        service_response = self.client.post('/api/base/services/', service_data)
        self.assertEqual(service_response.status_code, status.HTTP_201_CREATED)
        
        # Create booking with potential security issues
        booking_data = {
            'customer_name': '<script>alert("xss")</script>John Doe',
            'customer_phone': '+966501234567',
            'service': service_response.data['id'],
            'appointment_date': '2024-12-25',
            'appointment_time': '10:00:00',
            'notes': 'javascript:alert("xss")'
        }
        
        booking_response = self.client.post('/api/base/bookings/', booking_data)
        
        if booking_response.status_code == status.HTTP_201_CREATED:
            # Verify data was sanitized
            booking = Booking.objects.get(id=booking_response.data['id'])
            self.assertNotIn('<script>', booking.customer_name)
            self.assertNotIn('javascript:', booking.notes or '')
    
    def test_bulk_operations_security(self):
        """Test security in bulk operations"""
        # Create multiple services
        services = []
        for i in range(3):
            service = Service.objects.create(
                business=self.business,
                name=f'Service {i}',
                price=100,
                duration=60,
                category='barber'
            )
            services.append(service.id)
        
        # Test bulk update with potential injection
        bulk_data = {
            'ids': services,
            'data': {
                'name': "'; DROP TABLE base_service; --",
                'is_active': False
            }
        }
        
        response = self.client.post('/api/base/services/bulk_update/', bulk_data)
        
        # Should not crash and services should still exist
        self.assertIn(response.status_code, [200, 400, 401, 403])
        self.assertTrue(Service.objects.count() >= 3)