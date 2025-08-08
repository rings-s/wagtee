// =============================================================================
// ENTERPRISE API SERVICE LAYER - Advanced Patterns
// =============================================================================
// Demonstrates: Dependency injection, generic service classes, 
// type-safe response handling, and advanced error management

import type { 
	ApiResult, 
	PaginatedResult,
	QueryParams,
	User,
	LoginCredentials,
	RegistrationData,
	Service,
	Booking,
	Customer,
	BusinessProfile,
	ServiceFormData,
	PublicBookingForm,
	BookingFilters,
	ServiceFilters
} from '$lib/types/optimized.js';

// =============================================================================
// CORE INFRASTRUCTURE
// =============================================================================

/** HTTP client configuration */
interface HttpClientConfig {
	readonly baseURL: string;
	readonly timeout: number;
	readonly retryAttempts: number;
	readonly retryDelay: number;
}

/** Request options with extended configuration */
interface RequestOptions extends RequestInit {
	readonly skipAuth?: boolean;
	readonly skipErrorHandling?: boolean;
	readonly timeout?: number;
}

/** Advanced HTTP client with retry logic and error handling */
class HttpClient {
	private readonly config: HttpClientConfig;
	private tokenStorage: TokenStorage;

	constructor(
		config: HttpClientConfig,
		tokenStorage: TokenStorage
	) {
		this.config = config;
		this.tokenStorage = tokenStorage;
	}

	async request<T>(
		endpoint: string,
		options: RequestOptions = {}
	): Promise<ApiResult<T>> {
		const {
			skipAuth = false,
			skipErrorHandling = false,
			timeout = this.config.timeout,
			...fetchOptions
		} = options;

		const url = `${this.config.baseURL}${endpoint}`;
		const headers = this.buildHeaders(fetchOptions.headers, skipAuth);

		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);

		try {
			const response = await this.executeWithRetry(url, {
				...fetchOptions,
				headers,
				signal: controller.signal
			});

			clearTimeout(timeoutId);
			return await this.processResponse<T>(response, skipErrorHandling);

		} catch (error) {
			clearTimeout(timeoutId);
			return this.handleRequestError(error);
		}
	}

	private buildHeaders(
		customHeaders?: HeadersInit,
		skipAuth: boolean = false
	): HeadersInit {
		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
			...customHeaders
		};

		if (!skipAuth) {
			const token = this.tokenStorage.getAccessToken();
			if (token) {
				headers.Authorization = `Bearer ${token}`;
			}
		}

		return headers;
	}

	private async executeWithRetry(
		url: string,
		options: RequestInit
	): Promise<Response> {
		let lastError: Error | null = null;

		for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
			try {
				const response = await fetch(url, options);
				
				// Don't retry on client errors (4xx), only server errors (5xx)
				if (response.ok || response.status < 500) {
					return response;
				}

				lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
			} catch (error) {
				lastError = error instanceof Error ? error : new Error('Request failed');
			}

			// Wait before retry (exponential backoff)
			if (attempt < this.config.retryAttempts) {
				await this.delay(this.config.retryDelay * Math.pow(2, attempt));
			}
		}

		throw lastError;
	}

	private async processResponse<T>(
		response: Response,
		skipErrorHandling: boolean
	): Promise<ApiResult<T>> {
		const data = await response.json();

		if (!response.ok) {
			return this.handleHttpError(response, data, skipErrorHandling);
		}

		return {
			success: true,
			data
		};
	}

	private handleHttpError(
		response: Response,
		data: any,
		skipErrorHandling: boolean
	): ApiResult<never> {
		// Handle subscription payment required (402)
		if (response.status === 402) {
			return {
				success: false,
				error: data.message || 'Subscription required',
				code: 'SUBSCRIPTION_REQUIRED',
				data
			};
		}

		// Handle unauthorized (401)
		if (response.status === 401) {
			this.tokenStorage.clearTokens();
			return {
				success: false,
				error: 'Authentication required',
				code: 'AUTHENTICATION_REQUIRED'
			};
		}

		// Handle validation errors (422)
		if (response.status === 422) {
			return {
				success: false,
				error: this.formatValidationError(data),
				code: 'VALIDATION_ERROR',
				data
			};
		}

		return {
			success: false,
			error: data.message || data.detail || 'An error occurred',
			code: this.mapStatusToErrorCode(response.status)
		};
	}

	private formatValidationError(data: any): string {
		if (data.errors && typeof data.errors === 'object') {
			const errors = Object.entries(data.errors)
				.map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
				.join('; ');
			return `Validation failed: ${errors}`;
		}
		return data.message || 'Validation failed';
	}

	private mapStatusToErrorCode(status: number): string {
		const codeMap: Record<number, string> = {
			400: 'VALIDATION_ERROR',
			401: 'AUTHENTICATION_REQUIRED',
			402: 'SUBSCRIPTION_REQUIRED',
			403: 'PERMISSION_DENIED',
			404: 'NOT_FOUND',
			429: 'RATE_LIMITED',
			500: 'INTERNAL_ERROR',
			502: 'BAD_GATEWAY',
			503: 'SERVICE_UNAVAILABLE'
		};

		return codeMap[status] || 'UNKNOWN_ERROR';
	}

	private handleRequestError(error: any): ApiResult<never> {
		if (error.name === 'AbortError') {
			return {
				success: false,
				error: 'Request timeout',
				code: 'TIMEOUT'
			};
		}

		return {
			success: false,
			error: error instanceof Error ? error.message : 'Network error',
			code: 'NETWORK_ERROR'
		};
	}

	private delay(ms: number): Promise<void> {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	setTokenStorage(tokenStorage: TokenStorage): void {
		this.tokenStorage = tokenStorage;
	}
}

// =============================================================================
// TOKEN MANAGEMENT
// =============================================================================

/** Token storage abstraction for testing and flexibility */
interface TokenStorage {
	getAccessToken(): string | null;
	getRefreshToken(): string | null;
	setTokens(access: string, refresh: string): void;
	clearTokens(): void;
}

/** Browser-based token storage implementation */
class BrowserTokenStorage implements TokenStorage {
	private readonly ACCESS_TOKEN_KEY = 'auth_token';
	private readonly REFRESH_TOKEN_KEY = 'refresh_token';

	getAccessToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem(this.ACCESS_TOKEN_KEY);
	}

	getRefreshToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem(this.REFRESH_TOKEN_KEY);
	}

	setTokens(access: string, refresh: string): void {
		if (typeof window === 'undefined') return;
		localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
		localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
	}

	clearTokens(): void {
		if (typeof window === 'undefined') return;
		localStorage.removeItem(this.ACCESS_TOKEN_KEY);
		localStorage.removeItem(this.REFRESH_TOKEN_KEY);
	}
}

// =============================================================================
// QUERY PARAMETER BUILDER
// =============================================================================

/** Type-safe query parameter builder */
class QueryBuilder {
	private params = new URLSearchParams();

	add<T>(key: string, value: T | undefined | null): this {
		if (value !== undefined && value !== null && value !== '') {
			this.params.append(key, String(value));
		}
		return this;
	}

	addObject(obj: Record<string, any>): this {
		Object.entries(obj).forEach(([key, value]) => {
			this.add(key, value);
		});
		return this;
	}

	toString(): string {
		const query = this.params.toString();
		return query ? `?${query}` : '';
	}

	static fromObject(obj: Record<string, any>): string {
		return new QueryBuilder().addObject(obj).toString();
	}
}

// =============================================================================
// GENERIC SERVICE BASE CLASS
// =============================================================================

/** Generic CRUD service base class */
abstract class BaseService<T extends { id: number }, TCreate, TUpdate = Partial<TCreate>> {
	constructor(
		protected httpClient: HttpClient,
		protected basePath: string
	) {}

	async getAll(filters?: QueryParams): Promise<ApiResult<PaginatedResult<T>>> {
		const query = filters ? QueryBuilder.fromObject(filters) : '';
		return this.httpClient.request<PaginatedResult<T>>(`${this.basePath}/${query}`);
	}

	async getById(id: number): Promise<ApiResult<T>> {
		return this.httpClient.request<T>(`${this.basePath}/${id}/`);
	}

	async create(data: TCreate): Promise<ApiResult<T>> {
		return this.httpClient.request<T>(`${this.basePath}/`, {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	async update(id: number, data: TUpdate): Promise<ApiResult<T>> {
		return this.httpClient.request<T>(`${this.basePath}/${id}/`, {
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}

	async delete(id: number): Promise<ApiResult<void>> {
		return this.httpClient.request<void>(`${this.basePath}/${id}/`, {
			method: 'DELETE'
		});
	}

	async bulkDelete(ids: number[]): Promise<ApiResult<{ deleted_count: number }>> {
		return this.httpClient.request<{ deleted_count: number }>(`${this.basePath}/bulk-delete/`, {
			method: 'DELETE',
			body: JSON.stringify({ ids })
		});
	}

	async bulkUpdate(ids: number[], data: TUpdate): Promise<ApiResult<{ updated_count: number }>> {
		return this.httpClient.request<{ updated_count: number }>(`${this.basePath}/bulk-update/`, {
			method: 'POST',
			body: JSON.stringify({ ids, data })
		});
	}
}

// =============================================================================
// SPECIALIZED SERVICE IMPLEMENTATIONS
// =============================================================================

/** Authentication service with email-based flow */
class AuthService {
	constructor(private httpClient: HttpClient) {}

	async login(credentials: LoginCredentials): Promise<ApiResult<{
		user: User;
		access: string;
		refresh: string;
	}>> {
		return this.httpClient.request('/accounts/login/', {
			method: 'POST',
			body: JSON.stringify(credentials),
			skipAuth: true
		});
	}

	async register(data: RegistrationData): Promise<ApiResult<{
		user: User;
		access: string;
		refresh: string;
	}>> {
		return this.httpClient.request('/accounts/register/', {
			method: 'POST',
			body: JSON.stringify(data),
			skipAuth: true
		});
	}

	async sendEmailVerification(email: string): Promise<ApiResult<{ message: string }>> {
		return this.httpClient.request('/accounts/send-email-verification/', {
			method: 'POST',
			body: JSON.stringify({ email }),
			skipAuth: true
		});
	}

	async verifyEmail(email: string, code: string): Promise<ApiResult<{ message: string }>> {
		return this.httpClient.request('/accounts/verify-email/', {
			method: 'POST',
			body: JSON.stringify({ email, verification_code: code }),
			skipAuth: true
		});
	}

	async requestPasswordReset(email: string): Promise<ApiResult<{ message: string }>> {
		return this.httpClient.request('/accounts/password-reset/', {
			method: 'POST',
			body: JSON.stringify({ email }),
			skipAuth: true
		});
	}

	async confirmPasswordReset(
		email: string,
		token: string,
		new_password: string,
		confirm_password: string
	): Promise<ApiResult<{ message: string }>> {
		return this.httpClient.request('/accounts/password-reset-confirm/', {
			method: 'POST',
			body: JSON.stringify({ email, token, new_password, confirm_password }),
			skipAuth: true
		});
	}

	async refreshToken(refresh: string): Promise<ApiResult<{ access: string }>> {
		return this.httpClient.request('/accounts/token/refresh/', {
			method: 'POST',
			body: JSON.stringify({ refresh }),
			skipAuth: true
		});
	}

	async getCurrentUser(): Promise<ApiResult<User>> {
		return this.httpClient.request<User>('/accounts/profile/');
	}

	async logout(): Promise<ApiResult<void>> {
		return this.httpClient.request<void>('/accounts/logout/', {
			method: 'POST'
		});
	}
}

/** Service management with advanced filtering */
class ServiceService extends BaseService<Service, ServiceFormData> {
	constructor(httpClient: HttpClient) {
		super(httpClient, '/base/services');
	}

	async getAll(filters?: ServiceFilters): Promise<ApiResult<PaginatedResult<Service>>> {
		return super.getAll(filters);
	}

	async getByCategory(category: string): Promise<ApiResult<Service[]>> {
		return this.httpClient.request<Service[]>(`${this.basePath}/by-category/${category}/`);
	}

	async getPopular(limit: number = 5): Promise<ApiResult<Service[]>> {
		return this.httpClient.request<Service[]>(`${this.basePath}/popular/?limit=${limit}`);
	}
}

/** Booking management with status transitions */
class BookingService extends BaseService<Booking, PublicBookingForm> {
	constructor(httpClient: HttpClient) {
		super(httpClient, '/base/bookings');
	}

	async getAll(filters?: BookingFilters): Promise<ApiResult<PaginatedResult<Booking>>> {
		return super.getAll(filters);
	}

	async updateStatus(id: number, status: string, reason?: string): Promise<ApiResult<Booking>> {
		return this.httpClient.request<Booking>(`${this.basePath}/${id}/status/`, {
			method: 'PATCH',
			body: JSON.stringify({ status, reason })
		});
	}

	async getCalendarEvents(startDate: string, endDate: string): Promise<ApiResult<any[]>> {
		const query = QueryBuilder.fromObject({ start_date: startDate, end_date: endDate });
		return this.httpClient.request<any[]>(`${this.basePath}/calendar/${query}`);
	}
}

/** Public booking service for anonymous customers */
class PublicBookingService {
	constructor(private httpClient: HttpClient) {}

	async getBusinessServices(businessId: number): Promise<ApiResult<Service[]>> {
		return this.httpClient.request<Service[]>(
			`/base/public/business/${businessId}/services/`,
			{ skipAuth: true }
		);
	}

	async getAvailableSlots(
		businessId: number,
		serviceId: number,
		date?: string
	): Promise<ApiResult<string[]>> {
		const query = date ? QueryBuilder.fromObject({ date }) : '';
		return this.httpClient.request<string[]>(
			`/base/public/business/${businessId}/service/${serviceId}/slots/${query}`,
			{ skipAuth: true }
		);
	}

	async createBooking(data: PublicBookingForm): Promise<ApiResult<{ booking_id: string }>> {
		return this.httpClient.request<{ booking_id: string }>('/base/public/booking/', {
			method: 'POST',
			body: JSON.stringify(data),
			skipAuth: true
		});
	}

	async getBooking(bookingId: string, phone: string): Promise<ApiResult<Booking>> {
		const query = QueryBuilder.fromObject({ phone });
		return this.httpClient.request<Booking>(
			`/base/public/booking/${bookingId}/${query}`,
			{ skipAuth: true }
		);
	}

	async cancelBooking(bookingId: string, phone: string, reason?: string): Promise<ApiResult<void>> {
		return this.httpClient.request<void>('/base/public/booking/cancel/', {
			method: 'POST',
			body: JSON.stringify({ booking_id: bookingId, phone, reason }),
			skipAuth: true
		});
	}
}

/** Customer management service */
class CustomerService extends BaseService<Customer, Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'booking_count' | 'last_booking_at'>> {
	constructor(httpClient: HttpClient) {
		super(httpClient, '/base/customers');
	}

	async getCustomerStats(id: number): Promise<ApiResult<{
		total_bookings: number;
		total_spent: number;
		average_rating: number;
		last_booking_date?: string;
		favorite_services: Service[];
	}>> {
		return this.httpClient.request(`${this.basePath}/${id}/stats/`);
	}
}

/** Business profile management */
class BusinessService {
	constructor(private httpClient: HttpClient) {}

	async getProfile(): Promise<ApiResult<BusinessProfile>> {
		return this.httpClient.request<BusinessProfile>('/accounts/business-profile/');
	}

	async updateProfile(data: Partial<BusinessProfile>): Promise<ApiResult<BusinessProfile>> {
		return this.httpClient.request<BusinessProfile>('/accounts/business-profile/', {
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}

	async getDashboardStats(period?: string): Promise<ApiResult<any>> {
		const query = period ? QueryBuilder.fromObject({ period }) : '';
		return this.httpClient.request(`/base/dashboard/${query}`);
	}

	async getAnalytics(period?: string): Promise<ApiResult<any>> {
		const query = period ? QueryBuilder.fromObject({ period }) : '';
		return this.httpClient.request(`/base/analytics/${query}`);
	}
}

// =============================================================================
// API CLIENT FACTORY
// =============================================================================

/** Centralized API client with dependency injection */
export class ApiClient {
	private httpClient: HttpClient;
	private tokenStorage: TokenStorage;

	// Service instances
	public readonly auth: AuthService;
	public readonly services: ServiceService;
	public readonly bookings: BookingService;
	public readonly publicBookings: PublicBookingService;
	public readonly customers: CustomerService;
	public readonly business: BusinessService;

	constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api') {
		// Initialize dependencies
		this.tokenStorage = new BrowserTokenStorage();
		this.httpClient = new HttpClient({
			baseURL,
			timeout: 30000,
			retryAttempts: 3,
			retryDelay: 1000
		}, this.tokenStorage);

		// Initialize services
		this.auth = new AuthService(this.httpClient);
		this.services = new ServiceService(this.httpClient);
		this.bookings = new BookingService(this.httpClient);
		this.publicBookings = new PublicBookingService(this.httpClient);
		this.customers = new CustomerService(this.httpClient);
		this.business = new BusinessService(this.httpClient);
	}

	/** Set authentication tokens */
	setTokens(access: string, refresh: string): void {
		this.tokenStorage.setTokens(access, refresh);
	}

	/** Clear authentication tokens */
	clearTokens(): void {
		this.tokenStorage.clearTokens();
	}

	/** Get current access token */
	getAccessToken(): string | null {
		return this.tokenStorage.getAccessToken();
	}

	/** Configure HTTP client for testing */
	setHttpClient(httpClient: HttpClient): void {
		this.httpClient = httpClient;
	}

	/** Configure token storage for testing */
	setTokenStorage(tokenStorage: TokenStorage): void {
		this.tokenStorage = tokenStorage;
		this.httpClient.setTokenStorage(tokenStorage);
	}
}

// =============================================================================
// SINGLETON EXPORT
// =============================================================================

export const apiClient = new ApiClient();

// Export individual services for backwards compatibility
export const authService = apiClient.auth;
export const servicesService = apiClient.services;
export const bookingsService = apiClient.bookings;
export const publicService = apiClient.publicBookings;
export const customersService = apiClient.customers;
export const businessService = apiClient.business;

// Export types for external use
export type {
	HttpClientConfig,
	RequestOptions,
	TokenStorage,
	QueryParams,
	ApiResult,
	PaginatedResult
};