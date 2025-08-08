// =============================================================================
// REFACTORED TYPE SYSTEM - Clean TypeScript Architecture
// =============================================================================
// Advanced patterns: discriminated unions, utility types, composition-based design

// =============================================================================
// BASE & UTILITY TYPES
// =============================================================================

/** Base entity with audit fields */
interface BaseEntity {
	readonly id: number;
	readonly created_at: string;
	readonly updated_at: string;
}

/** Localized content for Arabic/English support */
interface LocalizedContent {
	name: string;
	name_ar?: string;
	description?: string;
	description_ar?: string;
}

/** Consistent API response wrapper */
interface ApiResponse<T> {
	readonly success: boolean;
	readonly data?: T;
	readonly error?: string;
	readonly code?: ApiErrorCode;
}

/** Discriminated union for error handling */
type ApiErrorCode = 
	| 'AUTHENTICATION_REQUIRED'
	| 'SUBSCRIPTION_REQUIRED' 
	| 'VALIDATION_ERROR'
	| 'RATE_LIMITED'
	| 'INTERNAL_ERROR';

/** Paginated response structure */
interface PaginatedResponse<T> {
	readonly results: readonly T[];
	readonly count: number;
	readonly next?: string;
	readonly previous?: string;
}

// =============================================================================
// USER & AUTHENTICATION (EMAIL-FIRST)
// =============================================================================

type UserRole = 'business_owner' | 'admin' | 'super_admin';
type SubscriptionTier = 'basic' | 'standard' | 'premium';

/** Enhanced user with subscription integration */
interface User extends BaseEntity {
	readonly username: string;
	readonly email: string; // Primary authentication
	readonly phone_number?: string; // For WhatsApp notifications only
	readonly role: UserRole;
	readonly is_verified: boolean;
	readonly is_active: boolean;
	
	// Business information
	readonly business_name?: string;
	readonly cr_number?: string;
	readonly vat_number?: string;
	readonly city?: string;
	readonly district?: string;
	
	// Subscription integration
	readonly subscription: SubscriptionStatus;
}

/** Subscription with feature gates */
interface SubscriptionStatus {
	readonly tier: SubscriptionTier;
	readonly is_active: boolean;
	readonly expires_at?: string;
	readonly features: Record<string, boolean>;
	readonly limits: SubscriptionLimits;
}

interface SubscriptionLimits {
	readonly max_services: number;
	readonly max_bookings_per_month: number;
	readonly max_customers: number;
	readonly can_use_analytics: boolean;
}

// =============================================================================
// AUTHENTICATION FORMS (CLEANED UP)
// =============================================================================

/** Login with email */
interface LoginForm {
	readonly email: string;
	readonly password: string;
}

/** Registration with enhanced validation */
interface RegisterForm extends LocalizedContent {
	readonly username: string;
	readonly email: string;
	readonly phone_number: string;
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
}

/** Email verification */
interface EmailVerificationForm {
	readonly email: string;
	readonly verification_code: string;
}

/** Password reset flow */
interface PasswordResetRequestForm {
	readonly email: string;
}

interface PasswordResetConfirmForm {
	readonly email: string;
	readonly token: string;
	readonly new_password: string;
	readonly confirm_password: string;
}

// =============================================================================
// BUSINESS ENTITIES
// =============================================================================

type ServiceType = 
	| 'barber' | 'salon' | 'beauty_center' 
	| 'car_wash' | 'cleaning' | 'gym' 
	| 'photographer' | 'makeup_artist' 
	| 'bazar' | 'events';

type DayOfWeek = 
	| 'saturday' | 'sunday' | 'monday' | 'tuesday' 
	| 'wednesday' | 'thursday' | 'friday';

/** Working hours by day */
interface WorkingHours {
	[key: string]: {
		open_time: string;
		close_time: string;
		is_closed: boolean;
	};
}

/** Business profile */
interface BusinessProfile extends BaseEntity, LocalizedContent {
	readonly user: number;
	readonly service_type: ServiceType;
	readonly address: string;
	readonly address_ar?: string;
	readonly latitude?: number;
	readonly longitude?: number;
	readonly working_hours: WorkingHours;
	readonly images: readonly string[];
	readonly rating: number;
	readonly is_active: boolean;
	readonly qr_code?: string;
}

/** Service entity */
interface Service extends BaseEntity, LocalizedContent {
	readonly business: number;
	readonly price: number;
	readonly duration: string; // ISO 8601
	readonly is_active: boolean;
}

/** Customer for anonymous booking */
interface Customer extends BaseEntity {
	readonly phone_number: string;
	readonly name: string;
	readonly email?: string;
}

// =============================================================================
// BOOKING SYSTEM
// =============================================================================

type BookingStatus = 
	| 'pending' | 'confirmed' | 'in_progress' 
	| 'completed' | 'cancelled' | 'no_show';

type BookingMethod = 
	| 'online' | 'walk_in' | 'phone' | 'qr_scan';

/** Booking entity */
interface Booking extends BaseEntity {
	readonly booking_id: string;
	readonly business: number;
	readonly service: number;
	readonly customer: number;
	readonly appointment_date: string;
	readonly appointment_time: string;
	readonly status: BookingStatus;
	readonly booking_method: BookingMethod;
	readonly total_price: number;
	readonly notes?: string;
	readonly reminder_sent: boolean;
	readonly qr_code?: string;
}

// =============================================================================
// FORM INTERFACES
// =============================================================================

/** Anonymous booking form */
interface BookingForm {
	readonly service_id: number;
	readonly customer_name: string;
	readonly customer_phone: string;
	readonly customer_email?: string;
	readonly appointment_date: string;
	readonly appointment_time: string;
	readonly notes?: string;
}

/** Service form */
interface ServiceForm extends LocalizedContent {
	readonly price: number;
	readonly duration: string;
	readonly is_active: boolean;
}

// =============================================================================
// DASHBOARD & ANALYTICS
// =============================================================================

interface DashboardStats {
	readonly total_bookings: number;
	readonly pending_bookings: number;
	readonly completed_bookings: number;
	readonly total_revenue: number;
	readonly monthly_revenue: number;
	readonly total_customers: number;
	readonly average_rating: number;
}

interface BookingCalendarEvent {
	readonly id: number;
	readonly title: string;
	readonly start: string;
	readonly end: string;
	readonly color?: string;
	readonly booking: Booking;
}

// =============================================================================
// NOTIFICATIONS
// =============================================================================

type NotificationType = 
	| 'booking_confirmation' | 'booking_reminder' 
	| 'booking_cancellation' | 'payment_success' 
	| 'subscription_expiry';

interface Notification extends BaseEntity {
	readonly user?: number;
	readonly customer?: number;
	readonly notification_type: NotificationType;
	readonly title: string;
	readonly message: string;
	readonly is_read: boolean;
	readonly sent_via_whatsapp: boolean;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/** Extract form data from entity */
type FormData<T> = Omit<T, keyof BaseEntity>;

/** Partial update type */
type UpdateData<T> = Partial<FormData<T>>;

/** Query parameters for filtering */
interface QueryParams {
	readonly page?: number;
	readonly ordering?: string;
	readonly search?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type {
	// Core entities
	User,
	BusinessProfile,
	Service,
	Booking,
	Customer,
	Notification,
	
	// Enums
	UserRole,
	SubscriptionTier,
	ServiceType,
	BookingStatus,
	BookingMethod,
	NotificationType,
	DayOfWeek,
	
	// Forms
	LoginForm,
	RegisterForm,
	EmailVerificationForm,
	PasswordResetRequestForm,
	PasswordResetConfirmForm,
	BookingForm,
	ServiceForm,
	
	// API types
	ApiResponse,
	PaginatedResponse,
	ApiErrorCode,
	
	// Subscription
	SubscriptionStatus,
	SubscriptionLimits,
	
	// Dashboard
	DashboardStats,
	BookingCalendarEvent,
	
	// Utilities
	BaseEntity,
	LocalizedContent,
	WorkingHours,
	FormData,
	UpdateData,
	QueryParams
};