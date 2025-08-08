import type { BusinessProfile, Service, Booking, DashboardStats } from '$lib/types/index.js';
import { businessService, servicesService, bookingsService } from '$lib/services/api.js';

// Business store using Svelte 5 runes
function createBusinessStore() {
	let profile = $state<BusinessProfile | null>(null);
	let services = $state<Service[]>([]);
	let bookings = $state<Booking[]>([]);
	let dashboardStats = $state<DashboardStats | null>(null);
	let isLoading = $state(false);
	let error = $state<string | null>(null);

	return {
		// Reactive getters
		get profile() { return profile; },
		get services() { return services; },
		get bookings() { return bookings; },
		get dashboardStats() { return dashboardStats; },
		get isLoading() { return isLoading; },
		get error() { return error; },

		// Business Profile Actions
		async loadProfile() {
			isLoading = true;
			error = null;

			try {
				const response = await businessService.getProfile();
				
				if (response.success && response.data) {
					profile = response.data;
					return { success: true };
				} else {
					error = response.error || 'Failed to load business profile';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			} finally {
				isLoading = false;
			}
		},

		async updateProfile(data: Partial<BusinessProfile>) {
			isLoading = true;
			error = null;

			try {
				const response = await businessService.updateProfile(data);
				
				if (response.success && response.data) {
					profile = response.data;
					return { success: true };
				} else {
					error = response.error || 'Failed to update business profile';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			} finally {
				isLoading = false;
			}
		},

		// Services Actions
		async loadServices() {
			try {
				const response = await servicesService.getAll();
				
				if (response.success && response.data) {
					services = response.data.results;
					return { success: true };
				} else {
					error = response.error || 'Failed to load services';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		async createService(serviceData: any) {
			try {
				const response = await servicesService.create(serviceData);
				
				if (response.success && response.data) {
					services = [...services, response.data];
					return { success: true };
				} else {
					error = response.error || 'Failed to create service';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		async updateService(id: number, serviceData: any) {
			try {
				const response = await servicesService.update(id, serviceData);
				
				if (response.success && response.data) {
					const index = services.findIndex(s => s.id === id);
					if (index !== -1) {
						services[index] = response.data;
					}
					return { success: true };
				} else {
					error = response.error || 'Failed to update service';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		async deleteService(id: number) {
			try {
				const response = await servicesService.delete(id);
				
				if (response.success) {
					services = services.filter(s => s.id !== id);
					return { success: true };
				} else {
					error = response.error || 'Failed to delete service';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		// Bookings Actions
		async loadBookings(params?: { status?: string; date?: string; page?: number }) {
			try {
				const response = await bookingsService.getAll(params);
				
				if (response.success && response.data) {
					bookings = response.data.results;
					return { success: true };
				} else {
					error = response.error || 'Failed to load bookings';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		async updateBookingStatus(id: number, status: string) {
			try {
				const response = await bookingsService.updateStatus(id, status);
				
				if (response.success && response.data) {
					const index = bookings.findIndex(b => b.id === id);
					if (index !== -1) {
						bookings[index] = response.data;
					}
					return { success: true };
				} else {
					error = response.error || 'Failed to update booking status';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		// Dashboard Actions
		async loadDashboardStats() {
			try {
				const response = await businessService.getDashboardStats();
				
				if (response.success && response.data) {
					dashboardStats = response.data;
					return { success: true };
				} else {
					error = response.error || 'Failed to load dashboard stats';
					return { success: false, error: error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error: error };
			}
		},

		// Utility Actions
		clearError() {
			error = null;
		},

		reset() {
			profile = null;
			services = [];
			bookings = [];
			dashboardStats = null;
			error = null;
			isLoading = false;
		}
	};
}

export const businessStore = createBusinessStore();