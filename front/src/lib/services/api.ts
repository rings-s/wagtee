// =============================================================================
// REFACTORED API SERVICE - Enterprise Architecture
// =============================================================================
// Clean patterns: Generic services, type safety, error handling, dependency injection

import type { 
	ApiResponse, 
	PaginatedResponse,
	User,
	LoginForm,
	RegisterForm,
	Service,
	Booking,
	Customer,
	BusinessProfile,
	ServiceForm,
	BookingForm,
	QueryParams
} from '$lib/types/refactored.js';

// =============================================================================
// CORE HTTP CLIENT
// =============================================================================

interface HttpConfig {
	readonly baseURL: string;
	readonly timeout: number;
	readonly retryAttempts: number;
}

class HttpClient {
	private readonly config: HttpConfig;
	private tokenStorage: TokenStorage;

	constructor(config: HttpConfig, tokenStorage: TokenStorage) {
		this.config = config;
		this.tokenStorage = tokenStorage;
	}

	async request<T>(
		endpoint: string,
		options: RequestInit & { skipAuth?: boolean } = {}
	): Promise<ApiResponse<T>> {
		const { skipAuth, ...fetchOptions } = options;
		const url = `${this.config.baseURL}${endpoint}`;
		
		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			...fetchOptions.headers
		};

		if (!skipAuth) {
			const token = this.tokenStorage.getAccessToken();
			if (token) {
				headers.Authorization = `Bearer ${token}`;
			}
		}

		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

		try {
			const response = await this.retryRequest(url, {
				...fetchOptions,
				headers,
				signal: controller.signal
			});

			clearTimeout(timeoutId);
			const data = await response.json();

			if (!response.ok) {
				return this.handleError(response, data);
			}

			return { success: true, data };

		} catch (error) {
			clearTimeout(timeoutId);
			return this.handleRequestError(error);
		}
	}

	private async retryRequest(url: string, options: RequestInit): Promise<Response> {
		let lastError: Error;

		for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
			try {
				const response = await fetch(url, options);
				if (response.ok || response.status < 500) {
					return response;
				}
				lastError = new Error(`HTTP ${response.status}`);
			} catch (error) {
				lastError = error instanceof Error ? error : new Error('Request failed');
			}

			if (attempt < this.config.retryAttempts) {
				await this.delay(1000 * Math.pow(2, attempt));
			}
		}

		throw lastError;
	}

	private handleError(response: Response, data: any): ApiResponse<never> {
		if (response.status === 402) {
			return {
				success: false,
				error: data.message || 'Subscription required',
				code: 'SUBSCRIPTION_REQUIRED',
				data
			};
		}

		if (response.status === 401) {
			this.tokenStorage.clearTokens();
			return {
				success: false,
				error: 'Authentication required',
				code: 'AUTHENTICATION_REQUIRED'
			};
		}

		return {
			success: false,
			error: data.message || data.detail || 'Request failed',
			code: this.mapStatusToCode(response.status)
		};
	}

	private handleRequestError(error: any): ApiResponse<never> {
		if (error.name === 'AbortError') {
			return { success: false, error: 'Request timeout', code: 'TIMEOUT' };
		}

		return {
			success: false,
			error: error instanceof Error ? error.message : 'Network error',
			code: 'NETWORK_ERROR'
		};
	}

	private mapStatusToCode(status: number): string {
		const codes: Record<number, string> = {
			400: 'VALIDATION_ERROR',
			401: 'AUTHENTICATION_REQUIRED',
			402: 'SUBSCRIPTION_REQUIRED',
			403: 'PERMISSION_DENIED',
			404: 'NOT_FOUND',
			429: 'RATE_LIMITED',
			500: 'INTERNAL_ERROR'
		};
		return codes[status] || 'UNKNOWN_ERROR';
	}

	private delay(ms: number): Promise<void> {
		return new Promise(resolve => setTimeout(resolve, ms));
	}
}

// =============================================================================
// TOKEN STORAGE
// =============================================================================

interface TokenStorage {
	getAccessToken(): string | null;
	getRefreshToken(): string | null;
	setTokens(access: string, refresh: string): void;
	clearTokens(): void;
}

class BrowserTokenStorage implements TokenStorage {
	getAccessToken(): string | null {
		return typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
	}

	getRefreshToken(): string | null {
		return typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
	}

	setTokens(access: string, refresh: string): void {
		if (typeof window !== 'undefined') {
			localStorage.setItem('auth_token', access);
			localStorage.setItem('refresh_token', refresh);
		}
	}

	clearTokens(): void {
		if (typeof window !== 'undefined') {
			localStorage.removeItem('auth_token');
			localStorage.removeItem('refresh_token');
		}
	}
}

// =============================================================================
// QUERY BUILDER
// =============================================================================

class QueryBuilder {
	private params = new URLSearchParams();

	add(key: string, value: any): this {
		if (value !== undefined && value !== null && value !== '') {
			this.params.append(key, String(value));
		}
		return this;
	}

	build(): string {
		const query = this.params.toString();
		return query ? `?${query}` : '';
	}

	static from(params: Record<string, any>): string {
		const builder = new QueryBuilder();
		Object.entries(params).forEach(([key, value]) => builder.add(key, value));
		return builder.build();
	}
}

// =============================================================================
// BASE SERVICE CLASS
// =============================================================================

abstract class BaseService<T extends { id: number }, TCreate, TUpdate = Partial<TCreate>> {
	constructor(
		protected http: HttpClient,
		protected path: string
	) {}

	async getAll(params?: QueryParams): Promise<ApiResponse<PaginatedResponse<T>>> {
		const query = params ? QueryBuilder.from(params) : '';
		return this.http.request<PaginatedResponse<T>>(`${this.path}/${query}`);
	}

	async getById(id: number): Promise<ApiResponse<T>> {
		return this.http.request<T>(`${this.path}/${id}/`);
	}

	async create(data: TCreate): Promise<ApiResponse<T>> {
		return this.http.request<T>(`${this.path}/`, {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}

	async update(id: number, data: TUpdate): Promise<ApiResponse<T>> {
		return this.http.request<T>(`${this.path}/${id}/`, {
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}

	async delete(id: number): Promise<ApiResponse<void>> {
		return this.http.request<void>(`${this.path}/${id}/`, {
			method: 'DELETE'
		});
	}

	async bulkDelete(ids: number[]): Promise<ApiResponse<{ deleted_count: number }>> {
		return this.http.request<{ deleted_count: number }>(`${this.path}/bulk-delete/`, {
			method: 'DELETE',
			body: JSON.stringify({ ids })
		});
	}
}

// =============================================================================
// SERVICE IMPLEMENTATIONS
// =============================================================================

class AuthService {
	constructor(private http: HttpClient) {}

	async login(credentials: LoginForm): Promise<ApiResponse<{
		user: User;
		access: string;
		refresh: string;
	}>> {
		return this.http.request('/accounts/login/', {
			method: 'POST',
			body: JSON.stringify(credentials),
			skipAuth: true
		});
	}

	async register(data: RegisterForm): Promise<ApiResponse<{
		user: User;
		access: string;
		refresh: string;
	}>> {
		return this.http.request('/accounts/register/', {
			method: 'POST',
			body: JSON.stringify(data),
			skipAuth: true
		});
	}

	async sendEmailVerification(email: string): Promise<ApiResponse<{ message: string }>> {
		return this.http.request('/accounts/send-email-verification/', {
			method: 'POST',
			body: JSON.stringify({ email }),
			skipAuth: true
		});
	}

	async verifyEmail(email: string, code: string): Promise<ApiResponse<{ message: string }>> {
		return this.http.request('/accounts/verify-email/', {
			method: 'POST',
			body: JSON.stringify({ email, verification_code: code }),
			skipAuth: true
		});
	}

	async requestPasswordReset(email: string): Promise<ApiResponse<{ message: string }>> {
		return this.http.request('/accounts/password-reset/', {
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
	): Promise<ApiResponse<{ message: string }>> {
		return this.http.request('/accounts/password-reset-confirm/', {
			method: 'POST',
			body: JSON.stringify({ email, token, new_password, confirm_password }),
			skipAuth: true
		});
	}

	async refreshToken(refresh: string): Promise<ApiResponse<{ access: string }>> {
		return this.http.request('/accounts/token/refresh/', {
			method: 'POST',
			body: JSON.stringify({ refresh }),
			skipAuth: true
		});
	}

	async getCurrentUser(): Promise<ApiResponse<User>> {
		return this.http.request<User>('/accounts/profile/');
	}

	async logout(): Promise<ApiResponse<void>> {
		return this.http.request<void>('/accounts/logout/', { method: 'POST' });
	}
}

class ServiceService extends BaseService<Service, ServiceForm> {
	constructor(http: HttpClient) {
		super(http, '/base/services');
	}
}

class BookingService extends BaseService<Booking, BookingForm> {
	constructor(http: HttpClient) {
		super(http, '/base/bookings');
	}

	async updateStatus(id: number, status: string): Promise<ApiResponse<Booking>> {
		return this.http.request<Booking>(`${this.path}/${id}/`, {
			method: 'PATCH',
			body: JSON.stringify({ status })
		});
	}
}

class PublicService {
	constructor(private http: HttpClient) {}

	async getBusinessServices(businessId: number): Promise<ApiResponse<Service[]>> {
		return this.http.request<Service[]>(
			`/base/public/business/${businessId}/services/`,
			{ skipAuth: true }
		);
	}

	async getAvailableSlots(
		businessId: number,
		serviceId: number,
		date?: string
	): Promise<ApiResponse<string[]>> {
		const query = date ? QueryBuilder.from({ date }) : '';
		return this.http.request<string[]>(
			`/base/public/business/${businessId}/service/${serviceId}/slots/${query}`,
			{ skipAuth: true }
		);
	}

	async createBooking(data: BookingForm): Promise<ApiResponse<{ booking_id: string }>> {
		return this.http.request<{ booking_id: string }>('/base/public/booking/', {
			method: 'POST',
			body: JSON.stringify(data),
			skipAuth: true
		});
	}

	async getBooking(bookingId: string, phone: string): Promise<ApiResponse<Booking>> {
		const query = QueryBuilder.from({ phone });
		return this.http.request<Booking>(
			`/base/public/booking/${bookingId}/${query}`,
			{ skipAuth: true }
		);
	}

	async cancelBooking(bookingId: string, phone: string): Promise<ApiResponse<void>> {
		return this.http.request<void>('/base/public/booking/cancel/', {
			method: 'POST',
			body: JSON.stringify({ booking_id: bookingId, phone }),
			skipAuth: true
		});
	}
}

class CustomerService extends BaseService<Customer, Omit<Customer, 'id' | 'created_at' | 'updated_at'>> {
	constructor(http: HttpClient) {
		super(http, '/base/customers');
	}
}

class BusinessService {
	constructor(private http: HttpClient) {}

	async getProfile(): Promise<ApiResponse<BusinessProfile>> {
		return this.http.request<BusinessProfile>('/accounts/business-profile/');
	}

	async updateProfile(data: Partial<BusinessProfile>): Promise<ApiResponse<BusinessProfile>> {
		return this.http.request<BusinessProfile>('/accounts/business-profile/', {
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}

	async getDashboardStats(period?: string): Promise<ApiResponse<any>> {
		const query = period ? QueryBuilder.from({ period }) : '';
		return this.http.request(`/base/dashboard/${query}`);
	}
}

// =============================================================================
// API CLIENT
// =============================================================================

export class ApiClient {
	private http: HttpClient;
	private tokenStorage: TokenStorage;

	public readonly auth: AuthService;
	public readonly services: ServiceService;
	public readonly bookings: BookingService;
	public readonly public: PublicService;
	public readonly customers: CustomerService;
	public readonly business: BusinessService;

	constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api') {
		this.tokenStorage = new BrowserTokenStorage();
		this.http = new HttpClient({
			baseURL,
			timeout: 30000,
			retryAttempts: 3
		}, this.tokenStorage);

		this.auth = new AuthService(this.http);
		this.services = new ServiceService(this.http);
		this.bookings = new BookingService(this.http);
		this.public = new PublicService(this.http);
		this.customers = new CustomerService(this.http);
		this.business = new BusinessService(this.http);
	}

	setTokens(access: string, refresh: string): void {
		this.tokenStorage.setTokens(access, refresh);
	}

	clearTokens(): void {
		this.tokenStorage.clearTokens();
	}

	getAccessToken(): string | null {
		return this.tokenStorage.getAccessToken();
	}
}

// =============================================================================
// EXPORTS
// =============================================================================

export const api = new ApiClient();

// Backward compatibility exports
export const authService = api.auth;
export const servicesService = api.services;
export const bookingsService = api.bookings;
export const publicService = api.public;
export const customersService = api.customers;
export const businessService = api.business;

export type { ApiResponse, PaginatedResponse, QueryParams };