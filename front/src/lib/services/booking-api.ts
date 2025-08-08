// Enhanced booking API service with proper nested serializers support
import type { Booking, BookingForm, Customer } from '$lib/types';
import { authStore } from '$lib/stores/auth.svelte';

const API_BASE = '/api';

interface ApiResponse<T> {
	success: boolean;
	data?: T;
	error?: string;
	message?: string;
}

interface PaginatedResponse<T> {
	results: T[];
	count: number;
	next?: string;
	previous?: string;
}

class BookingApiService {
	private async makeRequest<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<ApiResponse<T>> {
		try {
			const token = authStore.token;
			const headers = {
				'Content-Type': 'application/json',
				...(token && { Authorization: `Bearer ${token}` }),
				...options.headers,
			};

			const response = await fetch(`${API_BASE}${endpoint}`, {
				...options,
				headers,
			});

			const data = await response.json();

			if (response.ok) {
				return {
					success: true,
					data: data,
				};
			} else {
				return {
					success: false,
					error: data.message || data.error || 'Request failed',
				};
			}
		} catch (error) {
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Network error',
			};
		}
	}

	// Get all bookings with filtering
	async getBookings(params?: {
		status?: string;
		date_from?: string;
		date_to?: string;
		service?: string;
		customer?: string;
		page?: number;
		ordering?: string;
	}): Promise<ApiResponse<PaginatedResponse<Booking>>> {
		const searchParams = new URLSearchParams();
		
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined && value !== null && value !== '') {
					searchParams.append(key, value.toString());
				}
			});
		}

		const queryString = searchParams.toString();
		const endpoint = `/base/bookings/${queryString ? `?${queryString}` : ''}`;
		
		return this.makeRequest<PaginatedResponse<Booking>>(endpoint);
	}

	// Get a specific booking by ID
	async getBooking(id: number): Promise<ApiResponse<Booking>> {
		return this.makeRequest<Booking>(`/base/bookings/${id}/`);
	}

	// Create a new booking with nested customer creation
	async createBooking(bookingData: {
		service_id: number;
		customer_name: string;
		customer_phone: string;
		customer_email?: string;
		appointment_date: string;
		appointment_time: string;
		booking_method?: 'online' | 'walk_in' | 'phone' | 'qr_scan';
		notes?: string;
		auto_confirm?: boolean;
	}): Promise<ApiResponse<Booking>> {
		// Validate Saudi phone number format
		if (!bookingData.customer_phone.match(/^\+966[0-9]{9}$/)) {
			return {
				success: false,
				error: 'رقم الهاتف يجب أن يكون بالصيغة السعودية: +966xxxxxxxxx'
			};
		}

		// Validate date is not in the past
		const appointmentDateTime = new Date(`${bookingData.appointment_date}T${bookingData.appointment_time}`);
		const now = new Date();
		
		if (appointmentDateTime <= now) {
			return {
				success: false,
				error: 'تاريخ الموعد يجب أن يكون في المستقبل'
			};
		}

		const payload = {
			service: bookingData.service_id,
			customer_phone: bookingData.customer_phone,
			customer_name: bookingData.customer_name,
			customer_email: bookingData.customer_email || '',
			appointment_date: bookingData.appointment_date,
			appointment_time: bookingData.appointment_time,
			booking_method: bookingData.booking_method || 'online',
			notes: bookingData.notes || '',
			auto_confirm: bookingData.auto_confirm || false,
		};

		return this.makeRequest<Booking>('/base/bookings/', {
			method: 'POST',
			body: JSON.stringify(payload),
		});
	}

	// Update booking status
	async updateBookingStatus(
		id: number, 
		status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'in_progress' | 'no_show'
	): Promise<ApiResponse<Booking>> {
		return this.makeRequest<Booking>(`/base/bookings/${id}/status/`, {
			method: 'PATCH',
			body: JSON.stringify({ status }),
		});
	}

	// Update booking details (reschedule, etc.)
	async updateBooking(
		id: number, 
		updates: {
			appointment_date?: string;
			appointment_time?: string;
			notes?: string;
			service?: number;
		}
	): Promise<ApiResponse<Booking>> {
		return this.makeRequest<Booking>(`/base/bookings/${id}/`, {
			method: 'PATCH',
			body: JSON.stringify(updates),
		});
	}

	// Delete booking
	async deleteBooking(id: number): Promise<ApiResponse<void>> {
		return this.makeRequest<void>(`/base/bookings/${id}/`, {
			method: 'DELETE',
		});
	}

	// Get available time slots for a specific date and service
	async getAvailableSlots(
		serviceId: number, 
		date: string
	): Promise<ApiResponse<string[]>> {
		return this.makeRequest<string[]>(
			`/base/services/${serviceId}/available-slots/?date=${date}`
		);
	}

	// Check for booking conflicts
	async checkConflicts(
		serviceId: number,
		date: string,
		time: string,
		excludeBookingId?: number
	): Promise<ApiResponse<{ hasConflict: boolean; conflictingBookings: Booking[] }>> {
		const params = new URLSearchParams({
			service: serviceId.toString(),
			date,
			time,
		});

		if (excludeBookingId) {
			params.append('exclude', excludeBookingId.toString());
		}

		return this.makeRequest<{ hasConflict: boolean; conflictingBookings: Booking[] }>(
			`/base/bookings/check-conflicts/?${params.toString()}`
		);
	}

	// Bulk update bookings
	async bulkUpdateBookings(
		bookingIds: number[],
		updates: {
			status?: string;
			notes?: string;
		}
	): Promise<ApiResponse<{ updated: number; failed: number }>> {
		return this.makeRequest<{ updated: number; failed: number }>('/base/bookings/bulk-update/', {
			method: 'POST',
			body: JSON.stringify({
				booking_ids: bookingIds,
				updates,
			}),
		});
	}

	// Get booking statistics
	async getBookingStats(params?: {
		date_from?: string;
		date_to?: string;
		service?: string;
	}): Promise<ApiResponse<{
		total_bookings: number;
		pending_bookings: number;
		confirmed_bookings: number;
		completed_bookings: number;
		cancelled_bookings: number;
		total_revenue: number;
		average_rating: number;
	}>> {
		const searchParams = new URLSearchParams();
		
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined && value !== null && value !== '') {
					searchParams.append(key, value.toString());
				}
			});
		}

		const queryString = searchParams.toString();
		const endpoint = `/base/bookings/stats/${queryString ? `?${queryString}` : ''}`;
		
		return this.makeRequest(endpoint);
	}

	// Public booking (anonymous) - for customers without accounts
	async createPublicBooking(bookingData: {
		business_id: number;
		service_id: number;
		customer_name: string;
		customer_phone: string;
		customer_email?: string;
		appointment_date: string;
		appointment_time: string;
		notes?: string;
	}): Promise<ApiResponse<{
		booking: Booking;
		booking_id: string; // For customer reference
	}>> {
		// Validate Saudi phone number format
		if (!bookingData.customer_phone.match(/^\+966[0-9]{9}$/)) {
			return {
				success: false,
				error: 'رقم الهاتف يجب أن يكون بالصيغة السعودية: +966xxxxxxxxx'
			};
		}

		const payload = {
			business: bookingData.business_id,
			service: bookingData.service_id,
			customer_phone: bookingData.customer_phone,
			customer_name: bookingData.customer_name,
			customer_email: bookingData.customer_email || '',
			appointment_date: bookingData.appointment_date,
			appointment_time: bookingData.appointment_time,
			booking_method: 'online',
			notes: bookingData.notes || '',
		};

		return this.makeRequest<{
			booking: Booking;
			booking_id: string;
		}>('/base/public/bookings/', {
			method: 'POST',
			body: JSON.stringify(payload),
		});
	}

	// Get public booking (for customers to check their booking)
	async getPublicBooking(
		bookingId: string,
		phoneNumber: string
	): Promise<ApiResponse<Booking>> {
		return this.makeRequest<Booking>(
			`/base/public/bookings/${bookingId}/?phone=${encodeURIComponent(phoneNumber)}`
		);
	}

	// Cancel public booking
	async cancelPublicBooking(
		bookingId: string,
		phoneNumber: string
	): Promise<ApiResponse<Booking>> {
		return this.makeRequest<Booking>(
			`/base/public/bookings/${bookingId}/cancel/`,
			{
				method: 'POST',
				body: JSON.stringify({ phone_number: phoneNumber }),
			}
		);
	}
}

export const bookingApiService = new BookingApiService();