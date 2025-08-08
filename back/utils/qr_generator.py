# utils/qr_generator.py
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """Generate QR codes for bookings and business profiles"""
    
    @classmethod
    def generate_booking_qr(cls, booking):
        """
        Generate QR code for booking lookup
        Contains booking ID and verification phone for customer access
        """
        try:
            # Create lookup URL that customers can use
            lookup_url = f"{settings.FRONTEND_URL}/book/lookup/{booking.booking_id}"
            
            # QR code data includes booking ID and last 4 digits of phone for verification
            qr_data = {
                'type': 'booking_lookup',
                'booking_id': str(booking.booking_id),
                'phone_hint': booking.customer.phone_number[-4:],
                'business': booking.business.user.business_name,
                'service': booking.service.name,
                'date': booking.appointment_date.strftime('%Y-%m-%d'),
                'time': booking.appointment_time.strftime('%H:%M'),
                'url': lookup_url
            }
            
            # For QR code, use a simple format that opens the lookup URL
            qr_content = lookup_url
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create Django file
            filename = f"booking_qr_{booking.booking_id}.png"
            return ContentFile(buffer.getvalue(), name=filename)
            
        except Exception as e:
            logger.error(f"Failed to generate booking QR code: {str(e)}")
            return None
    
    @classmethod
    def generate_business_qr(cls, business_profile):
        """
        Generate QR code for business profile
        Allows customers to quickly access booking page
        """
        try:
            # Create booking URL for the business
            booking_url = f"{settings.FRONTEND_URL}/book/{business_profile.id}"
            
            # QR code data
            qr_data = {
                'type': 'business_booking',
                'business_id': business_profile.id,
                'business_name': business_profile.user.business_name,
                'service_type': business_profile.service_type,
                'url': booking_url
            }
            
            # For QR code, use the booking URL
            qr_content = booking_url
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create Django file
            filename = f"business_qr_{business_profile.id}.png"
            return ContentFile(buffer.getvalue(), name=filename)
            
        except Exception as e:
            logger.error(f"Failed to generate business QR code: {str(e)}")
            return None
    
    @classmethod
    def generate_service_qr(cls, service):
        """
        Generate QR code for specific service booking
        Direct link to book a specific service
        """
        try:
            # Create direct service booking URL
            service_url = f"{settings.FRONTEND_URL}/book/{service.business.id}/service/{service.id}"
            
            # QR code data
            qr_data = {
                'type': 'service_booking',
                'business_id': service.business.id,
                'service_id': service.id,
                'business_name': service.business.user.business_name,
                'service_name': service.name,
                'price': str(service.price),
                'url': service_url
            }
            
            # For QR code, use the service URL
            qr_content = service_url
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create Django file
            filename = f"service_qr_{service.id}.png"
            return ContentFile(buffer.getvalue(), name=filename)
            
        except Exception as e:
            logger.error(f"Failed to generate service QR code: {str(e)}")
            return None
    
    @classmethod
    def generate_qr_svg(cls, data, title="QR Code"):
        """
        Generate SVG QR code for web display
        Returns SVG string that can be embedded directly in HTML
        """
        try:
            # Create QR code factory for SVG
            factory = qrcode.image.svg.SvgImage
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
                image_factory=factory
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Generate SVG
            img = qr.make_image()
            
            # Convert to string
            buffer = BytesIO()
            img.save(buffer)
            svg_content = buffer.getvalue().decode('utf-8')
            
            return svg_content
            
        except Exception as e:
            logger.error(f"Failed to generate SVG QR code: {str(e)}")
            return None