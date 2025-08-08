import secrets
import logging
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OTPService:
    """Secure OTP service with rate limiting and expiration"""
    
    OTP_EXPIRY = 300  # 5 minutes
    MAX_ATTEMPTS = 3  # Maximum OTP attempts
    RATE_LIMIT_WINDOW = 3600  # 1 hour rate limit window
    MAX_OTP_REQUESTS = 5  # Maximum OTP requests per hour
    
    @classmethod
    def generate_secure_otp(cls) -> str:
        """Generate a cryptographically secure 6-digit OTP"""
        return str(secrets.randbelow(900000) + 100000)
    
    @classmethod
    def send_otp(cls, phone_number: str) -> dict:
        """
        Generate and store OTP for phone number with rate limiting
        
        Returns:
            dict: Status and message
        """
        # Check rate limiting
        rate_limit_key = f'otp_requests_{phone_number}'
        request_count = cache.get(rate_limit_key, 0)
        
        if request_count >= cls.MAX_OTP_REQUESTS:
            return {
                'success': False,
                'message': 'Too many OTP requests. Please try again later.',
                'error_code': 'RATE_LIMIT_EXCEEDED'
            }
        
        # Generate secure OTP
        otp = cls.generate_secure_otp()
        
        # Store OTP with expiration
        otp_key = f'otp_{phone_number}'
        attempts_key = f'otp_attempts_{phone_number}'
        
        cache.set(otp_key, otp, timeout=cls.OTP_EXPIRY)
        cache.set(attempts_key, 0, timeout=cls.OTP_EXPIRY)
        
        # Update rate limiting
        cache.set(rate_limit_key, request_count + 1, timeout=cls.RATE_LIMIT_WINDOW)
        
        # Log OTP for development and testing (completely free)
        logger.info(f"OTP for {phone_number}: {otp}")
        
        return {
            'success': True,
            'message': 'OTP generated successfully. Check server logs for the code.',
            'expires_in': cls.OTP_EXPIRY,
            'otp': otp if settings.DEBUG else None  # Include OTP in debug mode only
        }
    
    @classmethod
    def verify_otp(cls, phone_number: str, provided_otp: str) -> dict:
        """
        Verify OTP for phone number with attempt limiting
        
        Returns:
            dict: Verification result
        """
        otp_key = f'otp_{phone_number}'
        attempts_key = f'otp_attempts_{phone_number}'
        
        # Check if OTP exists
        stored_otp = cache.get(otp_key)
        if not stored_otp:
            return {
                'success': False,
                'message': 'OTP expired or not found',
                'error_code': 'OTP_EXPIRED'
            }
        
        # Check attempt count
        attempts = cache.get(attempts_key, 0)
        if attempts >= cls.MAX_ATTEMPTS:
            # Clear OTP after max attempts
            cache.delete(otp_key)
            cache.delete(attempts_key)
            return {
                'success': False,
                'message': 'Maximum OTP attempts exceeded',
                'error_code': 'MAX_ATTEMPTS_EXCEEDED'
            }
        
        # Verify OTP
        if provided_otp == stored_otp:
            # Clear OTP after successful verification
            cache.delete(otp_key)
            cache.delete(attempts_key)
            return {
                'success': True,
                'message': 'OTP verified successfully'
            }
        else:
            # Increment attempt count
            cache.set(attempts_key, attempts + 1, timeout=cls.OTP_EXPIRY)
            remaining_attempts = cls.MAX_ATTEMPTS - (attempts + 1)
            
            return {
                'success': False,
                'message': f'Invalid OTP. {remaining_attempts} attempts remaining',
                'error_code': 'INVALID_OTP',
                'remaining_attempts': remaining_attempts
            }
    
    @classmethod
    def clear_otp(cls, phone_number: str) -> None:
        """Clear OTP data for phone number"""
        otp_key = f'otp_{phone_number}'
        attempts_key = f'otp_attempts_{phone_number}'
        
        cache.delete(otp_key)
        cache.delete(attempts_key)