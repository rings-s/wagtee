// =============================================================================
// ADVANCED TYPE SYSTEM OPTIMIZATION - Wagtee Frontend
// =============================================================================
// Demonstrates enterprise-level TypeScript patterns with discriminated unions,
// utility types, and composition-based architecture

// =============================================================================
// BASE & UTILITY TYPES
// =============================================================================

/** Base entity interface with common audit fields */
interface BaseEntity {
	readonly id: number;
	readonly created_at: string;
	readonly updated_at: string;
}

/** Localized content interface for Arabic/English support */
interface LocalizedContent {
	name: string;
	name_ar?: string;
	description?: string;
	description_ar?: string;
}

/** API response wrapper with consistent error handling */
interface ApiResult<T> {
	readonly success: boolean;
	readonly data?: T;
	readonly error?: string;
	readonly code?: ApiErrorCode;
}

/** Discriminated union for API error codes */
type ApiErrorCode = 
	| 'AUTHENTICATION_REQUIRED'
	| 'SUBSCRIPTION_REQUIRED' 
	| 'VALIDATION_ERROR'
	| 'RATE_LIMITED'
	| 'INTERNAL_ERROR';

/** Pagination metadata interface */
interface PaginationMeta {
	readonly count: number;
	readonly next?: string;
	readonly previous?: string;
}

/** Paginated response with type safety */
interface PaginatedResult<T> extends PaginationMeta {
	readonly results: readonly T[];
}

// =============================================================================
// USER & AUTHENTICATION SYSTEM
// =============================================================================

/** User role with hierarchical permissions */
type UserRole = 'business_owner' | 'admin' | 'super_admin';

/** Subscription tier with feature access */
type SubscriptionTier = 'basic' | 'standard' | 'premium';

/** Enhanced user entity with subscription integration */
interface User extends BaseEntity {
	readonly username: string;
	readonly email: string; // Primary auth method (migrated from phone)
	readonly phone_number?: string; // Optional for notifications
	readonly role: UserRole;
	readonly is_verified: boolean;
	readonly is_active: boolean;
	
	// Business information
	readonly business_name?: string;
	readonly cr_number?: string; // Saudi CR number validation
	readonly vat_number?: string; // Saudi VAT number
	readonly city?: string;
	readonly district?: string;
	
	// Subscription data
	readonly subscription: SubscriptionStatus;
}

/** Subscription status with feature access control */
interface SubscriptionStatus {
	readonly tier: SubscriptionTier;
	readonly is_active: boolean;
	readonly expires_at?: string;
	readonly features: Record<string, boolean>;
	readonly limits: SubscriptionLimits;
}

/** Usage limits by subscription tier */
interface SubscriptionLimits {
	readonly max_services: number;
	readonly max_bookings_per_month: number;
	readonly max_customers: number;
	readonly can_use_analytics: boolean;
	readonly can_export_data: boolean;
}

// =============================================================================
// AUTHENTICATION FORMS WITH EMAIL-FIRST APPROACH
// =============================================================================

/** Login form (email-based) */
interface LoginCredentials {
	readonly email: string;
	readonly password: string;
	readonly remember_me?: boolean;
}

/** Registration form with enhanced validation */
interface RegistrationData extends LocalizedContent {
	readonly username: string;
	readonly email: string;
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
}

/** Email verification form */
interface EmailVerification {
	readonly email: string;
	readonly verification_code: string;
}

/** Password reset flow */
interface PasswordResetRequest {
	readonly email: string;
}

interface PasswordResetConfirm {
	readonly email: string;
	readonly token: string;
	readonly new_password: string;
	readonly confirm_password: string;
}

// =============================================================================
// BUSINESS ENTITIES WITH DISCRIMINATED UNIONS
// =============================================================================

/** Saudi business service types */
type ServiceType = 
	| 'barber' | 'salon' | 'beauty_center' 
	| 'car_wash' | 'cleaning' | 'gym' 
	| 'photographer' | 'makeup_artist' 
	| 'bazar' | 'events';

/** Working hours structure with day-specific settings */
type WorkingHours = Record<DayOfWeek, DaySchedule>;

interface DaySchedule {
	readonly open_time: string;
	readonly close_time: string;
	readonly is_closed: boolean;
}

type DayOfWeek = 
	| 'saturday' | 'sunday' | 'monday' | 'tuesday' 
	| 'wednesday' | 'thursday' | 'friday';

/** Business profile with location and settings */
interface BusinessProfile extends BaseEntity, LocalizedContent {
	readonly user: number;
	readonly service_type: ServiceType;
	readonly address: string;
	readonly address_ar?: string;
	readonly location?: GeoLocation;
	readonly working_hours: WorkingHours;
	readonly images: readonly string[];
	readonly rating: number;
	readonly is_active: boolean;
	readonly qr_code?: string;
	readonly settings: BusinessSettings;
}

/** Geographic location data */
interface GeoLocation {
	readonly latitude: number;
	readonly longitude: number;
}

/** Business configuration settings */
interface BusinessSettings {
	readonly auto_confirm_bookings: boolean;
	readonly allow_online_payments: boolean;
	readonly send_whatsapp_notifications: boolean;
	readonly booking_lead_time_hours: number;
	readonly max_advance_booking_days: number;
}

// =============================================================================
// SERVICE & BOOKING SYSTEM
// =============================================================================

/** Service entity with localization */
interface Service extends BaseEntity, LocalizedContent {
	readonly business: number;
	readonly price: number;
	readonly duration: string; // ISO 8601 duration
	readonly is_active: boolean;
	readonly category?: string;
	readonly requires_approval: boolean;
}

/** Customer data for anonymous booking system */
interface Customer extends BaseEntity {
	readonly phone_number: string;
	readonly name: string;
	readonly email?: string;
	readonly booking_count: number;
	readonly last_booking_at?: string;
}

/** Booking status with state machine pattern */
type BookingStatus = 
	| 'pending' | 'confirmed' | 'in_progress' 
	| 'completed' | 'cancelled' | 'no_show';

/** Booking method tracking */
type BookingMethod = 
	| 'online' | 'walk_in' | 'phone' | 'qr_scan';

/** Booking entity with comprehensive tracking */
interface Booking extends BaseEntity {
	readonly booking_id: string; // Public booking reference
	readonly business: number;
	readonly service: number;
	readonly customer: number;
	readonly appointment_date: string;
	readonly appointment_time: string;
	readonly status: BookingStatus;
	readonly method: BookingMethod;
	readonly total_price: number;
	readonly notes?: string;
	readonly reminder_sent: boolean;
	readonly qr_code?: string;
	readonly cancellation_reason?: string;
}

// =============================================================================
// FORM INTERFACES WITH VALIDATION
// =============================================================================

/** Anonymous booking form for public interface */
interface PublicBookingForm {
	readonly service_id: number;
	readonly customer_name: string;
	readonly customer_phone: string;
	readonly customer_email?: string;
	readonly appointment_date: string;
	readonly appointment_time: string;
	readonly notes?: string;
}

/** Service creation/update form */
interface ServiceFormData extends LocalizedContent {
	readonly price: number;
	readonly duration: string;
	readonly is_active: boolean;
	readonly category?: string;
	readonly requires_approval: boolean;
}

// =============================================================================
// ANALYTICS & DASHBOARD
// =============================================================================

/** Dashboard statistics with time-based metrics */
interface DashboardMetrics {
	readonly period: TimePeriod;
	readonly bookings: BookingMetrics;
	readonly revenue: RevenueMetrics;
	readonly customers: CustomerMetrics;
	readonly performance: PerformanceMetrics;
}

type TimePeriod = 'today' | 'week' | 'month' | 'quarter' | 'year';

interface BookingMetrics {
	readonly total: number;
	readonly confirmed: number;
	readonly completed: number;
	readonly cancelled: number;
	readonly no_shows: number;
	readonly conversion_rate: number;
}

interface RevenueMetrics {
	readonly total: number;
	readonly current_period: number;
	readonly previous_period: number;
	readonly growth_rate: number;
	readonly average_booking_value: number;
}

interface CustomerMetrics {
	readonly total: number;
	readonly new_customers: number;
	readonly returning_customers: number;
	readonly retention_rate: number;
}

interface PerformanceMetrics {
	readonly average_rating: number;
	readonly service_utilization: number;
	readonly peak_hours: readonly string[];
	readonly popular_services: readonly ServicePopularity[];
}

interface ServicePopularity {
	readonly service_id: number;
	readonly service_name: string;
	readonly booking_count: number;
	readonly revenue: number;
}

// =============================================================================
// NOTIFICATION SYSTEM
// =============================================================================

/** Notification types for WhatsApp integration */
type NotificationType = 
	| 'booking_confirmation' | 'booking_reminder' 
	| 'booking_cancellation' | 'payment_success' 
	| 'subscription_expiry' | 'daily_summary';

/** Notification entity with delivery tracking */
interface Notification extends BaseEntity {
	readonly user?: number;
	readonly customer?: number;
	readonly type: NotificationType;
	readonly title: string;
	readonly message: string;
	readonly is_read: boolean;
	readonly delivery_status: NotificationDeliveryStatus;
}

/** Notification delivery tracking */
interface NotificationDeliveryStatus {
	readonly sent_via_whatsapp: boolean;
	readonly sent_via_email: boolean;
	readonly delivery_timestamp?: string;
	readonly failure_reason?: string;
}

// =============================================================================
// ADVANCED UTILITY TYPES
// =============================================================================

/** Extract form data from entity types */
type FormData<T> = Omit<T, keyof BaseEntity | 'id'>;

/** Make specific fields optional for updates */
type PartialUpdate<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/** API endpoint parameter types */
type QueryParams<T = Record<string, unknown>> = T & {
	readonly page?: number;
	readonly ordering?: string;
	readonly search?: string;
};

/** Filter parameters for list endpoints */
interface BookingFilters extends QueryParams {
	readonly status?: BookingStatus;
	readonly date_from?: string;
	readonly date_to?: string;
	readonly service_id?: number;
	readonly customer_id?: number;
}

interface ServiceFilters extends QueryParams {
	readonly is_active?: boolean;
	readonly price_min?: number;
	readonly price_max?: number;
	readonly category?: string;
}

// =============================================================================
// CALENDAR & SCHEDULING
// =============================================================================

/** Calendar event for booking display */
interface CalendarEvent {
	readonly id: string;
	readonly title: string;
	readonly start: string;
	readonly end: string;
	readonly color?: string;
	readonly booking: Booking;
	readonly is_available: boolean;
}

/** Available time slot for scheduling */
interface TimeSlot {
	readonly start_time: string;
	readonly end_time: string;
	readonly is_available: boolean;
	readonly booking_id?: string;
}

// =============================================================================
// EXPORTS FOR BACKWARD COMPATIBILITY
// =============================================================================

// Re-export commonly used types with original names
export type {
	// Core entities
	User,
	BusinessProfile,
	Service,
	Booking,
	Customer,
	
	// Enums
	UserRole,
	SubscriptionTier,
	ServiceType,
	BookingStatus,
	BookingMethod,
	NotificationType,
	
	// Forms
	LoginCredentials as LoginForm,
	RegistrationData as RegisterForm,
	EmailVerification as EmailVerificationForm,
	PasswordResetRequest as PasswordResetRequestForm,
	PasswordResetConfirm as PasswordResetConfirmForm,
	PublicBookingForm as BookingForm,
	ServiceFormData as ServiceForm,
	
	// API types
	ApiResult as ApiResponse,
	PaginatedResult as PaginatedResponse,
	
	// Filters
	BookingFilters,
	ServiceFilters,
	QueryParams,
	
	// Dashboard
	DashboardMetrics as DashboardStats,
	CalendarEvent as BookingCalendarEvent,
	
	// Utilities
	BaseEntity,
	LocalizedContent,
	FormData,
	PartialUpdate,
	WorkingHours,
	DayOfWeek,
	TimePeriod
};