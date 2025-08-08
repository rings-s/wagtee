// =============================================================================
// ADVANCED TYPE SYSTEM - Email-First Auth & Discriminated Unions
// =============================================================================

// Base entity with audit fields
interface BaseEntity {
	readonly id: number;
	readonly created_at: string;
	readonly updated_at: string;
}

// Localized content for Arabic/English support
interface LocalizedContent {
	name: string;
	name_ar?: string;
	description?: string;
	description_ar?: string;
}

// User roles with hierarchical permissions
export type UserRole = 'business_owner' | 'admin' | 'super_admin';

// Subscription tiers
export type SubscriptionTier = 'basic' | 'standard' | 'premium';

// Enhanced user with email-first authentication
export interface User extends BaseEntity {
	readonly username: string;
	readonly email: string; // Primary authentication method
	readonly phone_number?: string; // Optional for WhatsApp notifications
	readonly role: UserRole;
	readonly is_verified: boolean;
	readonly is_active: boolean;
	
	// Business information
	readonly business_name?: string;
	readonly cr_number?: string; // Saudi CR number
	readonly vat_number?: string; // Saudi VAT number
	readonly city?: string;
	readonly district?: string;
	
	// Subscription integration
	readonly subscription: SubscriptionStatus;
}

// Subscription with feature gates
export interface SubscriptionStatus {
	readonly tier: SubscriptionTier;
	readonly is_active: boolean;
	readonly expires_at?: string;
	readonly features: Record<string, boolean>;
	readonly limits: SubscriptionLimits;
}

export interface SubscriptionLimits {
	readonly max_services: number;
	readonly max_bookings_per_month: number;
	readonly max_customers: number;
	readonly can_use_analytics: boolean;
}

// Business Profile Types
export interface BusinessProfile {
	id: number;
	user: number | User;
	service_type: ServiceType;
	description?: string;
	description_ar?: string;
	address: string;
	address_ar?: string;
	latitude?: number;
	longitude?: number;
	working_hours: WorkingHours;
	images: string[];
	rating: number;
	is_active: boolean;
	qr_code?: string;
}

export type ServiceType = 
	| 'barber'
	| 'salon'
	| 'beauty_center'
	| 'car_wash'
	| 'cleaning'
	| 'gym'
	| 'photographer'
	| 'makeup_artist'
	| 'bazar'
	| 'events';

export interface WorkingHours {
	[key: string]: {
		open_time: string;
		close_time: string;
		is_closed: boolean;
	};
}

// Subscription Types
export interface Subscription {
	id: number;
	user: number;
	tier: 'basic' | 'standard' | 'premium';
	price: number;
	is_active: boolean;
	start_date: string;
	end_date: string;
	// Payment gateway integration removed for testing mode
	// lemon_squeezy_subscription_id?: string;
}

export interface SubscriptionTierInfo {
	name: string;
	price: number;
	currency: string;
	features: string[];
	limits: {
		max_services: number;
		max_bookings_per_month: number;
		max_customers: number;
	};
}

// Service Types
export interface Service {
	id: number;
	business: number | BusinessProfile;
	name: string;
	name_ar?: string;
	description?: string;
	description_ar?: string;
	price: number;
	duration: string; // ISO 8601 duration format
	is_active: boolean;
	created_at: string;
}

// Customer Types
export interface Customer {
	id: number;
	phone_number: string;
	name: string;
	email?: string | null;
	date_of_birth?: string | null;
	gender?: string | null;
	address?: string | null;
	notes?: string | null;
	customer_segment?: 'new' | 'regular' | 'vip' | 'inactive';
	total_bookings?: number;
	total_spent?: number;
	last_booking_date?: string | null;
	status?: string;
	avatar?: string | null;
	created_at: string;
	updated_at?: string;
}

// Booking Types
export interface Booking {
	id: number;
	booking_id?: string;
	business?: number | BusinessProfile;
	service?: number | Service;
	customer?: Customer; // Always populated customer object
	appointment_date: string;
	appointment_time: string;
	status: BookingStatus;
	booking_method: BookingMethod;
	total_price: number;
	notes?: string;
	reminder_sent?: boolean;
	qr_code?: string;
	created_at: string;
	updated_at: string;
}

export type BookingStatus = 
	| 'pending'
	| 'confirmed'
	| 'in_progress'
	| 'completed'
	| 'cancelled'
	| 'no_show';

export type BookingMethod = 
	| 'online'
	| 'walk_in'
	| 'phone'
	| 'qr_scan';

// Review Types
export interface Review {
	id: number;
	booking: number | Booking;
	rating: 1 | 2 | 3 | 4 | 5;
	comment?: string;
	created_at: string;
}

// Business Hours Types
export interface BusinessHours {
	id: number;
	business: number;
	day: DayOfWeek;
	open_time: string;
	close_time: string;
	is_closed: boolean;
}

export type DayOfWeek = 
	| 'saturday'
	| 'sunday'
	| 'monday'
	| 'tuesday'
	| 'wednesday'
	| 'thursday'
	| 'friday';

// Notification Types
export interface Notification {
	id: number;
	user?: number;
	customer?: number;
	notification_type: NotificationType;
	title: string;
	message: string;
	is_read: boolean;
	sent_via_whatsapp: boolean;
	created_at: string;
}

export type NotificationType = 
	| 'booking_confirmation'
	| 'booking_reminder'
	| 'booking_cancellation'
	| 'payment_success'
	| 'subscription_expiry';

export interface NotificationTemplate {
	id: number;
	name: string;
	type: NotificationType;
	title_template: string;
	message_template: string;
	is_active: boolean;
	language: 'ar' | 'en';
	created_at: string;
}

export interface NotificationCampaign {
	id: number;
	name: string;
	template: NotificationTemplate;
	target_audience: 'all' | 'vip' | 'regular' | 'new' | 'inactive';
	scheduled_time?: string;
	status: 'draft' | 'scheduled' | 'sent' | 'failed';
	total_sent: number;
	success_count: number;
	created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
	data?: T;
	message?: string;
	error?: string;
	success: boolean;
	code?: string;
	shouldRetry?: boolean;
}

export interface PaginatedResponse<T> {
	results: T[];
	count: number;
	next?: string;
	previous?: string;
}

// =============================================================================
// AUTHENTICATION FORMS (EMAIL-FIRST ARCHITECTURE)
// =============================================================================

// Clean login form with email primary
export interface LoginForm {
	readonly email: string;
	readonly password: string;
	readonly remember_me?: boolean;
}

// Enhanced registration with localization
export interface RegisterForm {
	readonly username: string;
	readonly email: string;
	readonly first_name: string;
	readonly last_name: string;
	readonly phone_number: string; // Required for WhatsApp notifications
	readonly password: string;
	readonly confirm_password: string;
	readonly role: UserRole;
	readonly business_name: string;
	readonly service_type: ServiceType;
	readonly address: string;
	readonly address_ar?: string;
	readonly city: string;
	readonly district: string;
	readonly cr_number?: string;
	readonly vat_number?: string;
	readonly terms_accepted: boolean;
	// Optional LocalizedContent fields
	readonly name?: string;
	readonly name_ar?: string;
	readonly description?: string;
	readonly description_ar?: string;
}

// Removed OTPForm - deprecated after email migration

export interface EmailVerificationForm {
	email: string;
	verification_code: string;
}

export interface PasswordResetRequestForm {
	email: string;
}

export interface PasswordResetConfirmForm {
	email: string;
	token: string;
	new_password: string;
	confirm_password: string;
}

export interface BookingForm {
	service_id: string;
	customer: {
		name: string;
		phone_number: string;
		email?: string;
	};
	appointment_date: string;
	appointment_time: string;
	notes?: string;
	booking_method: BookingMethod;
	auto_confirm?: boolean;
}

export interface ServiceForm {
	name: string;
	name_ar?: string;
	description?: string;
	description_ar?: string;
	price: number;
	duration: string;
	is_active: boolean;
}

export interface CustomerForm {
	name: string;
	phone_number: string;
	email?: string;
	date_of_birth?: string;
	gender?: string;
	address?: string;
	notes?: string;
}

// Dashboard Types
export interface DashboardStats {
	total_bookings: number;
	pending_bookings: number;
	completed_bookings: number;
	total_revenue: number;
	monthly_revenue: number;
	total_customers: number;
	average_rating: number;
}

export interface BookingCalendarEvent {
	id: number;
	title: string;
	start: string;
	end: string;
	color?: string;
	booking: Booking;
}