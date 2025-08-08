import type { 
	BusinessProfile, 
	Service, 
	Booking, 
	Customer, 
	DashboardStats, 
	SubscriptionTierInfo 
} from '$lib/types/index.js';
import { 
	businessService, 
	servicesService, 
	bookingsService, 
	customersService 
} from '$lib/services/api.js';
import { authStore } from './auth.svelte.js';

// Subscription tier definitions (moved from dummy data)
export const SUBSCRIPTION_TIERS: SubscriptionTierInfo[] = [
	{
		name: 'Basic',
		price: 30,
		currency: 'SAR',
		features: [
			'Up to 5 services',
			'50 bookings per month', 
			'100 customers',
			'Basic support',
			'Mobile app access'
		],
		limits: {
			max_services: 5,
			max_bookings_per_month: 50,
			max_customers: 100
		}
	},
	{
		name: 'Standard',
		price: 45,
		currency: 'SAR',
		features: [
			'Up to 15 services',
			'150 bookings per month',
			'300 customers', 
			'Priority support',
			'WhatsApp notifications',
			'Analytics dashboard'
		],
		limits: {
			max_services: 15,
			max_bookings_per_month: 150,
			max_customers: 300
		}
	},
	{
		name: 'Premium',
		price: 60,
		currency: 'SAR',
		features: [
			'Unlimited services',
			'Unlimited bookings',
			'Unlimited customers',
			'24/7 support',
			'Advanced analytics',
			'Custom branding',
			'API access'
		],
		limits: {
			max_services: -1, // -1 indicates unlimited
			max_bookings_per_month: -1,
			max_customers: -1
		}
	}
];

// Global app state store using Svelte 5 runes
function createAppStore() {
	// Business profile state
	let businessProfile = $state<BusinessProfile | null>(null);
	let isBusinessLoading = $state(false);
	let businessError = $state<string | null>(null);

	// Services state
	let services = $state<Service[]>([]);
	let isServicesLoading = $state(false);
	let servicesError = $state<string | null>(null);

	// Bookings state
	let bookings = $state<Booking[]>([]);
	let isBookingsLoading = $state(false);
	let bookingsError = $state<string | null>(null);

	// Customers state
	let customers = $state<Customer[]>([]);
	let isCustomersLoading = $state(false);
	let customersError = $state<string | null>(null);

	// Dashboard state
	let dashboardStats = $state<DashboardStats | null>(null);
	let isDashboardLoading = $state(false);
	let dashboardError = $state<string | null>(null);

	// Derived reactive values
	const hasBusinessProfile = $derived(!!businessProfile);
	const totalServices = $derived(services.length);
	const totalBookings = $derived(bookings.length);
	const totalCustomers = $derived(customers.length);
	const pendingBookings = $derived(bookings.filter(b => b.status === 'pending'));
	const confirmedBookings = $derived(bookings.filter(b => b.status === 'confirmed'));
	const completedBookings = $derived(bookings.filter(b => b.status === 'completed'));

	// Auto-load data when user is authenticated
	$effect(() => {
		if (authStore.isAuthenticated) {
			loadBusinessProfile();
			loadServices();
			loadBookings();
			loadCustomers();
			loadDashboardStats();
		} else {
			// Clear data when user logs out
			businessProfile = null;
			services = [];
			bookings = [];
			customers = [];
			dashboardStats = null;
		}
	});

	return {
		// Getters for state
		get businessProfile() { return businessProfile; },
		get isBusinessLoading() { return isBusinessLoading; },
		get businessError() { return businessError; },

		get services() { return services; },
		get isServicesLoading() { return isServicesLoading; },
		get servicesError() { return servicesError; },

		get bookings() { return bookings; },
		get isBookingsLoading() { return isBookingsLoading; },
		get bookingsError() { return bookingsError; },

		get customers() { return customers; },
		get isCustomersLoading() { return isCustomersLoading; },
		get customersError() { return customersError; },

		get dashboardStats() { return dashboardStats; },
		get isDashboardLoading() { return isDashboardLoading; },
		get dashboardError() { return dashboardError; },

		// Derived values
		get hasBusinessProfile() { return hasBusinessProfile; },
		get totalServices() { return totalServices; },
		get totalBookings() { return totalBookings; },
		get totalCustomers() { return totalCustomers; },
		get pendingBookings() { return pendingBookings; },
		get confirmedBookings() { return confirmedBookings; },
		get completedBookings() { return completedBookings; },

		// Business profile actions
		async loadBusinessProfile() {
			isBusinessLoading = true;
			businessError = null;

			try {
				const response = await businessService.getProfile();
				if (response.success && response.data) {
					businessProfile = response.data;
				} else {
					businessError = response.error || 'Failed to load business profile';
				}
			} catch (err) {
				businessError = 'Network error occurred';
			} finally {
				isBusinessLoading = false;
			}
		},

		async updateBusinessProfile(data: Partial<BusinessProfile>) {
			isBusinessLoading = true;
			businessError = null;

			try {
				const response = await businessService.updateProfile(data);
				if (response.success && response.data) {
					businessProfile = response.data;
					return { success: true };
				} else {
					businessError = response.error || 'Failed to update business profile';
					return { success: false, error: businessError };
				}
			} catch (err) {
				businessError = 'Network error occurred';
				return { success: false, error: businessError };
			} finally {
				isBusinessLoading = false;
			}
		},

		// Services actions
		async loadServices(params?: any) {
			isServicesLoading = true;
			servicesError = null;

			try {
				const response = await servicesService.getAll(params);
				if (response.success && response.data) {
					services = response.data.results || response.data;
				} else {
					servicesError = response.error || 'Failed to load services';
				}
			} catch (err) {
				servicesError = 'Network error occurred';
			} finally {
				isServicesLoading = false;
			}
		},

		async createService(data: any) {
			isServicesLoading = true;
			servicesError = null;

			try {
				const response = await servicesService.create(data);
				if (response.success && response.data) {
					services = [...services, response.data];
					return { success: true, data: response.data };
				} else {
					servicesError = response.error || 'Failed to create service';
					return { success: false, error: servicesError };
				}
			} catch (err) {
				servicesError = 'Network error occurred';
				return { success: false, error: servicesError };
			} finally {
				isServicesLoading = false;
			}
		},

		async updateService(id: number, data: any) {
			const response = await servicesService.update(id, data);
			if (response.success && response.data) {
				const index = services.findIndex(s => s.id === id);
				if (index !== -1) {
					services[index] = response.data;
				}
				return { success: true, data: response.data };
			}
			return { success: false, error: response.error };
		},

		async deleteService(id: number) {
			const response = await servicesService.delete(id);
			if (response.success) {
				services = services.filter(s => s.id !== id);
				return { success: true };
			}
			return { success: false, error: response.error };
		},

		// Bookings actions
		async loadBookings(params?: any) {
			isBookingsLoading = true;
			bookingsError = null;

			try {
				const response = await bookingsService.getAll(params);
				if (response.success && response.data) {
					bookings = response.data.results || response.data;
				} else {
					bookingsError = response.error || 'Failed to load bookings';
				}
			} catch (err) {
				bookingsError = 'Network error occurred';
			} finally {
				isBookingsLoading = false;
			}
		},

		async updateBookingStatus(id: number, status: string) {
			const response = await bookingsService.updateStatus(id, status);
			if (response.success && response.data) {
				const index = bookings.findIndex(b => b.id === id);
				if (index !== -1) {
					bookings[index] = response.data;
				}
				return { success: true, data: response.data };
			}
			return { success: false, error: response.error };
		},

		// Customers actions
		async loadCustomers(params?: any) {
			isCustomersLoading = true;
			customersError = null;

			try {
				const response = await customersService.getAll(params);
				if (response.success && response.data) {
					customers = response.data.results || response.data;
				} else {
					customersError = response.error || 'Failed to load customers';
				}
			} catch (err) {
				customersError = 'Network error occurred';
			} finally {
				isCustomersLoading = false;
			}
		},

		// Dashboard actions
		async loadDashboardStats(period?: string) {
			isDashboardLoading = true;
			dashboardError = null;

			try {
				const response = await businessService.getDashboardStats(period);
				if (response.success && response.data) {
					dashboardStats = response.data;
				} else {
					dashboardError = response.error || 'Failed to load dashboard stats';
				}
			} catch (err) {
				dashboardError = 'Network error occurred';
			} finally {
				isDashboardLoading = false;
			}
		},

		// Utility methods
		getServiceById(id: number) {
			return services.find(service => service.id === id);
		},

		getBookingById(id: number) {
			return bookings.find(booking => booking.id === id);
		},

		getCustomerById(id: number) {
			return customers.find(customer => customer.id === id);
		},

		getBookingsByStatus(status: string) {
			return bookings.filter(booking => booking.status === status);
		},

		clearErrors() {
			businessError = null;
			servicesError = null;
			bookingsError = null;
			customersError = null;
			dashboardError = null;
		}
	};
}

export const appStore = createAppStore();

// Export subscription tiers helper function
export function getSubscriptionTierInfo(tierName: string): SubscriptionTierInfo | undefined {
	return SUBSCRIPTION_TIERS.find(tier => tier.name.toLowerCase() === tierName.toLowerCase());
}