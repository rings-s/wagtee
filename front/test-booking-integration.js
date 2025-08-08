// Simple integration test for booking functionality
// Run with: node test-booking-integration.js

const API_BASE = 'http://localhost:8000/api';

// Mock data for testing
const testBookingData = {
	service_id: 1,
	customer_name: 'أحمد محمد',
	customer_phone: '+966501234567',
	customer_email: 'ahmed@example.com',
	appointment_date: '2025-01-10',
	appointment_time: '10:00',
	booking_method: 'online',
	notes: 'اختبار الحجز',
	auto_confirm: false
};

// Mock auth token (replace with real token for testing)
const mockToken = 'your-test-token-here';

async function testBookingCreation() {
	console.log('🧪 Testing booking creation...');
	
	try {
		const response = await fetch(`${API_BASE}/base/bookings/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${mockToken}`
			},
			body: JSON.stringify({
				service: testBookingData.service_id,
				customer_phone: testBookingData.customer_phone,
				customer_name: testBookingData.customer_name,
				customer_email: testBookingData.customer_email,
				appointment_date: testBookingData.appointment_date,
				appointment_time: testBookingData.appointment_time,
				booking_method: testBookingData.booking_method,
				notes: testBookingData.notes,
				auto_confirm: testBookingData.auto_confirm
			})
		});

		const data = await response.json();
		
		if (response.ok) {
			console.log('✅ Booking created successfully:', data);
			return data.id;
		} else {
			console.log('❌ Failed to create booking:', data);
			return null;
		}
	} catch (error) {
		console.log('❌ Network error:', error.message);
		return null;
	}
}

async function testBookingRetrieval(bookingId) {
	console.log('🧪 Testing booking retrieval...');
	
	try {
		const response = await fetch(`${API_BASE}/base/bookings/${bookingId}/`, {
			headers: {
				'Authorization': `Bearer ${mockToken}`
			}
		});

		const data = await response.json();
		
		if (response.ok) {
			console.log('✅ Booking retrieved successfully:', data);
			console.log('📅 Nested data check:');
			console.log('  - Customer:', data.customer);
			console.log('  - Service:', data.service);
			return true;
		} else {
			console.log('❌ Failed to retrieve booking:', data);
			return false;
		}
	} catch (error) {
		console.log('❌ Network error:', error.message);
		return false;
	}
}

async function testBookingList() {
	console.log('🧪 Testing booking list with filters...');
	
	try {
		const params = new URLSearchParams({
			date_from: '2025-01-01',
			date_to: '2025-01-31',
			ordering: 'appointment_date,appointment_time'
		});

		const response = await fetch(`${API_BASE}/base/bookings/?${params}`, {
			headers: {
				'Authorization': `Bearer ${mockToken}`
			}
		});

		const data = await response.json();
		
		if (response.ok) {
			console.log('✅ Booking list retrieved successfully:');
			console.log(`  - Total results: ${data.count}`);
			console.log(`  - Current page results: ${data.results.length}`);
			
			if (data.results.length > 0) {
				console.log('📋 Sample booking structure:');
				console.log('  - ID:', data.results[0].id);
				console.log('  - Booking ID:', data.results[0].booking_id);
				console.log('  - Status:', data.results[0].status);
				console.log('  - Customer name:', data.results[0].customer?.name);
				console.log('  - Service name:', data.results[0].service?.name);
			}
			
			return true;
		} else {
			console.log('❌ Failed to retrieve booking list:', data);
			return false;
		}
	} catch (error) {
		console.log('❌ Network error:', error.message);
		return false;
	}
}

async function testPublicBooking() {
	console.log('🧪 Testing anonymous/public booking...');
	
	try {
		const response = await fetch(`${API_BASE}/base/public/bookings/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				business: 1, // Assuming business ID 1 exists
				service: 1,  // Assuming service ID 1 exists
				customer_phone: '+966501234568',
				customer_name: 'زائر مجهول',
				customer_email: 'anonymous@example.com',
				appointment_date: '2025-01-11',
				appointment_time: '14:00',
				notes: 'حجز عام للاختبار'
			})
		});

		const data = await response.json();
		
		if (response.ok) {
			console.log('✅ Public booking created successfully:');
			console.log('  - Booking ID:', data.booking_id);
			console.log('  - Booking data:', data.booking);
			return data.booking_id;
		} else {
			console.log('❌ Failed to create public booking:', data);
			return null;
		}
	} catch (error) {
		console.log('❌ Network error:', error.message);
		return null;
	}
}

async function testConflictDetection() {
	console.log('🧪 Testing booking conflict detection...');
	
	try {
		const params = new URLSearchParams({
			service: '1',
			date: '2025-01-10',
			time: '10:00'
		});

		const response = await fetch(`${API_BASE}/base/bookings/check-conflicts/?${params}`, {
			headers: {
				'Authorization': `Bearer ${mockToken}`
			}
		});

		const data = await response.json();
		
		if (response.ok) {
			console.log('✅ Conflict check completed:');
			console.log('  - Has conflict:', data.hasConflict);
			console.log('  - Conflicting bookings:', data.conflictingBookings.length);
			return true;
		} else {
			console.log('❌ Failed to check conflicts:', data);
			return false;
		}
	} catch (error) {
		console.log('❌ Network error:', error.message);
		return false;
	}
}

// Main test execution
async function runTests() {
	console.log('🚀 Starting BookingManager Integration Tests\n');
	console.log('ℹ️  Note: Make sure the backend server is running on localhost:8000');
	console.log('ℹ️  Update the mockToken variable with a valid JWT token for authenticated tests\n');
	
	// Test 1: Create booking
	const bookingId = await testBookingCreation();
	console.log('');
	
	// Test 2: Retrieve booking (if creation succeeded)
	if (bookingId) {
		await testBookingRetrieval(bookingId);
		console.log('');
	}
	
	// Test 3: List bookings
	await testBookingList();
	console.log('');
	
	// Test 4: Public booking
	const publicBookingId = await testPublicBooking();
	console.log('');
	
	// Test 5: Conflict detection
	await testConflictDetection();
	console.log('');
	
	console.log('🏁 Test execution completed!');
	console.log('');
	console.log('📝 Manual tests to perform:');
	console.log('  1. Open the frontend and navigate to /test-booking');
	console.log('  2. Try creating a new booking through the UI');
	console.log('  3. Test drag-and-drop functionality');
	console.log('  4. Test calendar navigation');
	console.log('  5. Test filtering and search');
	console.log('  6. Test bulk operations');
	console.log('  7. Test Arabic RTL layout');
}

// Run the tests
runTests().catch(console.error);