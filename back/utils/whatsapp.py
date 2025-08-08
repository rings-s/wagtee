import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """WhatsApp Business API service for sending messages"""
    
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_otp_message(self, phone_number: str, otp: str) -> dict:
        """
        Send OTP via WhatsApp
        
        Args:
            phone_number: Phone number in international format (+966xxxxxxxxx)
            otp: 6-digit OTP code
            
        Returns:
            dict: API response status
        """
        if not self.api_url or not self.access_token:
            logger.warning("WhatsApp API not configured")
            return {
                'success': False,
                'message': 'WhatsApp service not available',
                'error_code': 'SERVICE_UNAVAILABLE'
            }
        
        # Format phone number (remove + for WhatsApp API)
        formatted_phone = phone_number.replace('+', '')
        
        message_data = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": "otp_verification",  # Template name in WhatsApp Business
                "language": {
                    "code": "ar"  # Arabic language
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": otp
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=message_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"OTP sent successfully to {phone_number}")
                return {
                    'success': True,
                    'message': 'OTP sent via WhatsApp',
                    'message_id': response.json().get('messages', [{}])[0].get('id')
                }
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'message': 'Failed to send OTP',
                    'error_code': 'WHATSAPP_API_ERROR'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API request failed: {str(e)}")
            return {
                'success': False,
                'message': 'Network error while sending OTP',
                'error_code': 'NETWORK_ERROR'
            }
    
    def send_booking_confirmation(self, phone_number: str, booking_details: dict) -> dict:
        """
        Send booking confirmation via WhatsApp
        
        Args:
            phone_number: Customer phone number
            booking_details: Booking information
            
        Returns:
            dict: API response status
        """
        if not self.api_url or not self.access_token:
            return {
                'success': False,
                'message': 'WhatsApp service not available'
            }
        
        formatted_phone = phone_number.replace('+', '')
        
        message_data = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": "booking_confirmation",
                "language": {
                    "code": "ar"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": booking_details.get('business_name', '')},
                            {"type": "text", "text": booking_details.get('service_name', '')},
                            {"type": "text", "text": booking_details.get('appointment_date', '')},
                            {"type": "text", "text": booking_details.get('appointment_time', '')},
                            {"type": "text", "text": str(booking_details.get('total_price', '0'))}
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/messages",
                headers=self.headers,
                json=message_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Booking confirmation sent to {phone_number}")
                return {'success': True, 'message': 'Confirmation sent'}
            else:
                logger.error(f"WhatsApp API error: {response.status_code}")
                return {'success': False, 'message': 'Failed to send confirmation'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API request failed: {str(e)}")
            return {'success': False, 'message': 'Network error'}


def send_whatsapp_message(phone_number: str, message_type: str, **kwargs) -> dict:
    """
    Convenience function for sending WhatsApp messages
    
    Args:
        phone_number: Recipient phone number
        message_type: Type of message (otp, booking_confirmation, etc.)
        **kwargs: Additional message parameters
        
    Returns:
        dict: Response status
    """
    service = WhatsAppService()
    
    if message_type == 'otp':
        return service.send_otp_message(phone_number, kwargs.get('otp'))
    elif message_type == 'booking_confirmation':
        return service.send_booking_confirmation(phone_number, kwargs.get('booking_details', {}))
    else:
        return {
            'success': False,
            'message': f'Unknown message type: {message_type}'
        }