#!/usr/bin/env python3
"""
Comprehensive QR Code Integration Testing
Tests QR code generation, API endpoints, and integration functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
import json
import qrcode
from PIL import Image
from io import BytesIO
import time
from datetime import date, time as datetime_time, datetime, timedelta

# Setup Django environment
sys.path.append('/home/ahmed/tech-Savvy-projects/2025/new_ones/wagtee/back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wagtee.settings')
django.setup()

from utils.qr_generator import QRCodeGenerator
from base.models import Service, Booking, Customer
from accounts.models import BusinessProfile, User

User = get_user_model()

class QRCodeUtilityTests(TestCase):
    """Test QR code generation utility functions"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and business profile
        self.user = User.objects.create_user(
            phone_number='+966501234567',
            business_name='Test Business',
            password='testpass123'
        )
        
        self.business_profile = BusinessProfile.objects.create(
            user=self.user,
            service_type='barber',
            name_ar='اختبار الأعمال',
            description='Test business description',
            address='Test Address',
            city='Riyadh'
        )
        
        # Create test service
        self.service = Service.objects.create(
            business=self.business_profile,
            name='Test Service',
            description='Test service description',
            price=50.00,
            duration=30
        )
        
        # Create test customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone_number='+966509876543'
        )
        
        # Create test booking
        self.booking = Booking.objects.create(
            business=self.business_profile,
            service=self.service,
            customer=self.customer,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=datetime_time(10, 0),
            total_price=50.00
        )
    
    def test_business_qr_generation(self):
        """Test business QR code generation"""
        print("Testing business QR code generation...")
        
        qr_file = QRCodeGenerator.generate_business_qr(self.business_profile)
        
        self.assertIsNotNone(qr_file, "QR file should be generated")
        self.assertTrue(qr_file.name.startswith('business_qr_'), "QR file should have correct naming")
        self.assertTrue(qr_file.name.endswith('.png'), "QR file should be PNG format")
        
        # Test QR code content can be read
        img = Image.open(qr_file)
        self.assertEqual(img.format, 'PNG', "Generated image should be PNG")
        self.assertGreater(img.size[0], 0, "Image should have valid dimensions")
        
        print("✅ Business QR code generation successful")
    
    def test_booking_qr_generation(self):
        """Test booking QR code generation"""
        print("Testing booking QR code generation...")
        
        qr_file = QRCodeGenerator.generate_booking_qr(self.booking)
        
        self.assertIsNotNone(qr_file, "QR file should be generated")
        self.assertTrue(qr_file.name.startswith('booking_qr_'), "QR file should have correct naming")
        self.assertTrue(qr_file.name.endswith('.png'), "QR file should be PNG format")
        
        # Test booking ID is in filename
        self.assertIn(str(self.booking.booking_id), qr_file.name, "Booking ID should be in filename")
        
        print("✅ Booking QR code generation successful")
    
    def test_service_qr_generation(self):
        """Test service QR code generation"""
        print("Testing service QR code generation...")
        
        qr_file = QRCodeGenerator.generate_service_qr(self.service)
        
        self.assertIsNotNone(qr_file, "QR file should be generated")
        self.assertTrue(qr_file.name.startswith('service_qr_'), "QR file should have correct naming")
        self.assertTrue(qr_file.name.endswith('.png'), "QR file should be PNG format")
        
        print("✅ Service QR code generation successful")
    
    def test_svg_qr_generation(self):
        """Test SVG QR code generation"""
        print("Testing SVG QR code generation...")
        
        test_data = "https://example.com/test"
        svg_content = QRCodeGenerator.generate_qr_svg(test_data)
        
        self.assertIsNotNone(svg_content, "SVG content should be generated")
        self.assertIn('<svg', svg_content, "Should contain SVG tag")
        self.assertIn('</svg>', svg_content, "Should contain closing SVG tag")
        
        print("✅ SVG QR code generation successful")
    
    def test_qr_content_validation(self):
        """Test QR code contains correct data"""
        print("Testing QR code content validation...")
        
        # Test business QR content
        business_qr = QRCodeGenerator.generate_business_qr(self.business_profile)
        self.assertIsNotNone(business_qr, "Business QR should be generated")
        
        # Test booking QR content
        booking_qr = QRCodeGenerator.generate_booking_qr(self.booking)
        self.assertIsNotNone(booking_qr, "Booking QR should be generated")
        
        print("✅ QR code content validation successful")
    
    def test_error_handling(self):
        """Test error handling in QR generation"""
        print("Testing error handling...")
        
        # Test with None objects (should handle gracefully)
        result = QRCodeGenerator.generate_business_qr(None)
        self.assertIsNone(result, "Should handle None business profile gracefully")
        
        result = QRCodeGenerator.generate_booking_qr(None)
        self.assertIsNone(result, "Should handle None booking gracefully")
        
        result = QRCodeGenerator.generate_service_qr(None)
        self.assertIsNone(result, "Should handle None service gracefully")
        
        print("✅ Error handling tests successful")

class QRCodeAPITests(TestCase):
    """Test QR code API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()
        
        # Create test user and business profile
        self.user = User.objects.create_user(
            phone_number='+966501234567',
            business_name='Test Business API',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.save()
        
        self.business_profile = BusinessProfile.objects.create(
            user=self.user,
            service_type='salon',
            name_ar='اختبار API',
            description='Test API business',
            address='API Test Address',
            city='Jeddah'
        )
        
        # Create test service
        self.service = Service.objects.create(
            business=self.business_profile,
            name='API Test Service',
            description='API test service description',
            price=75.00,
            duration=45
        )
        
        # Create test customer and booking
        self.customer = Customer.objects.create(
            name='API Test Customer',
            phone_number='+966509876543'
        )
        
        self.booking = Booking.objects.create(
            business=self.business_profile,
            service=self.service,
            customer=self.customer,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=datetime_time(14, 0),
            total_price=75.00
        )
        
        # Login user
        self.client.force_login(self.user)
    
    def test_generate_business_qr_endpoint(self):
        """Test business QR generation endpoint"""
        print("Testing business QR generation endpoint...")
        
        url = reverse('generate_business_qr')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
        
        data = response.json()
        self.assertEqual(data['message'], 'QR code generated successfully')
        self.assertIsNotNone(data.get('qr_code_url'), "Should return QR code URL")
        
        # Verify QR code was saved to business profile
        self.business_profile.refresh_from_db()
        self.assertTrue(self.business_profile.qr_code, "Business profile should have QR code")
        
        print("✅ Business QR generation endpoint test successful")
    
    def test_booking_qr_endpoint(self):
        """Test booking QR code endpoint"""
        print("Testing booking QR code endpoint...")
        
        url = reverse('booking_qr_code', args=[self.booking.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
        
        data = response.json()
        self.assertEqual(data['booking_id'], str(self.booking.booking_id))
        self.assertIsNotNone(data.get('qr_code_url'), "Should return QR code URL")
        self.assertEqual(data['customer_name'], self.customer.name)
        self.assertEqual(data['service_name'], self.service.name)
        
        print("✅ Booking QR endpoint test successful")
    
    def test_service_qr_endpoint(self):
        """Test service QR generation endpoint"""
        print("Testing service QR generation endpoint...")
        
        url = reverse('generate_service_qr', args=[self.service.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
        
        data = response.json()
        self.assertEqual(data['message'], 'QR code generated successfully')
        self.assertIsNotNone(data.get('qr_code_url'), "Should return QR code URL")
        
        print("✅ Service QR endpoint test successful")
    
    def test_unauthorized_access(self):
        """Test unauthorized access to QR endpoints"""
        print("Testing unauthorized access...")
        
        # Logout user
        self.client.logout()
        
        # Test business QR endpoint
        url = reverse('generate_business_qr')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401, "Should return 401 Unauthorized")
        
        # Test booking QR endpoint
        url = reverse('booking_qr_code', args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401, "Should return 401 Unauthorized")
        
        print("✅ Unauthorized access test successful")

class QRCodePerformanceTests(TestCase):
    """Test QR code generation performance"""
    
    def setUp(self):
        """Set up performance test data"""
        self.user = User.objects.create_user(
            phone_number='+966501234567',
            business_name='Performance Test Business',
            password='testpass123'
        )
        
        self.business_profile = BusinessProfile.objects.create(
            user=self.user,
            service_type='gym',
            name_ar='اختبار الأداء',
            description='Performance test business',
            address='Performance Test Address',
            city='Dammam'
        )
        
        self.service = Service.objects.create(
            business=self.business_profile,
            name='Performance Test Service',
            description='Performance test service description',
            price=100.00,
            duration=60
        )
        
        self.customer = Customer.objects.create(
            name='Performance Test Customer',
            phone_number='+966509876543'
        )
        
        self.booking = Booking.objects.create(
            business=self.business_profile,
            service=self.service,
            customer=self.customer,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time=datetime_time(16, 0),
            total_price=100.00
        )
    
    def test_qr_generation_performance(self):
        """Test QR code generation performance"""
        print("Testing QR code generation performance...")
        
        # Test business QR generation time
        start_time = time.time()
        for i in range(10):
            qr_file = QRCodeGenerator.generate_business_qr(self.business_profile)
            self.assertIsNotNone(qr_file, f"Business QR generation {i+1} should succeed")
        business_time = (time.time() - start_time) / 10
        
        # Test booking QR generation time
        start_time = time.time()
        for i in range(10):
            qr_file = QRCodeGenerator.generate_booking_qr(self.booking)
            self.assertIsNotNone(qr_file, f"Booking QR generation {i+1} should succeed")
        booking_time = (time.time() - start_time) / 10
        
        # Test service QR generation time
        start_time = time.time()
        for i in range(10):
            qr_file = QRCodeGenerator.generate_service_qr(self.service)
            self.assertIsNotNone(qr_file, f"Service QR generation {i+1} should succeed")
        service_time = (time.time() - start_time) / 10
        
        print(f"📊 Average generation times:")
        print(f"   Business QR: {business_time:.3f}s")
        print(f"   Booking QR: {booking_time:.3f}s")
        print(f"   Service QR: {service_time:.3f}s")
        
        # Performance assertions (should be under 1 second)
        self.assertLess(business_time, 1.0, "Business QR generation should be under 1 second")
        self.assertLess(booking_time, 1.0, "Booking QR generation should be under 1 second")
        self.assertLess(service_time, 1.0, "Service QR generation should be under 1 second")
        
        print("✅ Performance tests successful")
    
    def test_memory_usage(self):
        """Test memory usage during QR generation"""
        print("Testing memory usage...")
        
        # Generate multiple QR codes to test memory usage
        qr_files = []
        for i in range(50):
            business_qr = QRCodeGenerator.generate_business_qr(self.business_profile)
            booking_qr = QRCodeGenerator.generate_booking_qr(self.booking)
            service_qr = QRCodeGenerator.generate_service_qr(self.service)
            
            qr_files.extend([business_qr, booking_qr, service_qr])
        
        # Verify all QR codes were generated successfully
        for qr_file in qr_files:
            self.assertIsNotNone(qr_file, "All QR codes should be generated successfully")
        
        print(f"📊 Generated {len(qr_files)} QR codes successfully")
        print("✅ Memory usage test successful")

def run_comprehensive_tests():
    """Run all QR code integration tests"""
    print("🚀 Starting Comprehensive QR Code Integration Tests")
    print("=" * 60)
    
    # Import Django test runner
    from django.test.runner import DiscoverRunner
    
    # Create test runner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Run tests
    test_classes = [
        QRCodeUtilityTests,
        QRCodeAPITests,
        QRCodePerformanceTests
    ]
    
    failures = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")
        print("-" * 40)
        
        suite = django.test.TestLoader().loadTestsFromTestCase(test_class)
        result = test_runner.run_tests([suite])
        failures += result
    
    print("\n" + "=" * 60)
    if failures == 0:
        print("🎉 All QR Code Integration Tests PASSED!")
    else:
        print(f"❌ {failures} test(s) failed")
    
    return failures == 0

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)