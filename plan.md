# Wagtee SaaS Booking Platform - Backend-to-Frontend Page Architecture Plan

## Project Overview
**Wagtee** is a comprehensive Saudi-focused SaaS booking platform built with Django (backend) and SvelteKit with Svelte 5 runes (frontend). The core models are User, BusinessProfile, Service, Customer, Booking, Review, Subscription, and Notification.

## Core Backend Models Analysis

### 1. User Model (`accounts.User`)
- **Fields**: Email-based auth, role hierarchy (super_admin � admin � business_owner), subscription management
- **Key Features**: Saudi phone validation (+966), CR/VAT numbers, subscription tiers
- **API Endpoints**: `/api/accounts/login/`, `/api/accounts/register/`, `/api/accounts/profile/`

### 2. BusinessProfile Model (`accounts.BusinessProfile`)  
- **Fields**: Service types (barber, salon, beauty_center, etc.), Arabic localization, geolocation, QR codes
- **Key Features**: Multi-language support, working hours JSON, rating system
- **API Endpoints**: `/api/accounts/business-profile/`, `/api/base/qr/business/`

### 3. Service Model (`base.Service`)
- **Fields**: Pricing, duration, Arabic descriptions, active status
- **Relationships**: Belongs to BusinessProfile
- **API Endpoints**: `/api/base/services/`, `/api/base/services/{id}/`

### 4. Customer Model (`base.Customer`)
- **Fields**: Anonymous booking (phone + name only), email optional
- **Key Features**: No account required for booking
- **API Endpoints**: `/api/base/customers/`, `/api/base/customers/{id}/`

### 5. Booking Model (`base.Booking`)
- **Fields**: UUID booking_id, status workflow, payment tracking, QR codes
- **Key Features**: Arabic status translations, multiple booking methods
- **API Endpoints**: `/api/base/bookings/`, `/api/base/public/booking/`

### 6. Other Supporting Models
- **Review**: One-to-one with Booking, 1-5 rating system
- **BusinessHours**: Weekly schedule management  
- **Notification**: WhatsApp integration, multi-channel notifications
- **Subscription**: Tier-based pricing (Basic 30 SAR, Standard 45 SAR, Premium 60 SAR)

## Required Frontend Pages Architecture

### A. Authentication System Pages

#### 1. `/auth/login` - Multi-Modal Login Page
- **Model Connection**: User model with email-based authentication
- **API Endpoints**: `POST /api/accounts/login/`, `POST /api/accounts/refresh/`
- **Features**: 
  - Email/password login with JWT tokens
  - OTP phone verification backup
  - Forgot password integration
  - Role-based redirect after login
- **UI/UX**: Premium glass morphism design, bilingual (AR/EN)
- **Components**: `LoginForm.svelte`, `ProtectedRoute.svelte`
- **Svelte 5 Runes**: `$state` for form data, `$effect` for validation

#### 2. `/auth/register` - Business Registration
- **Model Connection**: User + BusinessProfile creation in single flow
- **API Endpoints**: `POST /api/accounts/register/`, `POST /api/accounts/business-profile/`
- **Features**:
  - Multi-step wizard (User � Business � Verification)
  - CR/VAT number validation
  - Saudi phone format validation
  - Service type selection
- **UI/UX**: Progressive disclosure, validation feedback
- **Components**: `RegistrationWizard.svelte`, `BusinessSetupForm.svelte`
- **Svelte 5 Runes**: `$state` for wizard steps, `$derived` for validation

#### 3. `/auth/verify-email` - Email Verification
- **Model Connection**: User.is_verified field update
- **API Endpoints**: `POST /api/accounts/verify-email/`
- **Features**: Email verification token handling, resend functionality
- **Svelte 5 Runes**: `$state` for verification status

### B. Dashboard & Analytics Pages

#### 4. `/dashboard` - Main Business Dashboard
- **Model Connection**: Aggregated data from Booking, Review, Customer models
- **API Endpoints**: `GET /api/base/dashboard/`, `GET /api/base/subscription-status/`
- **Features**:
  - Real-time booking statistics
  - Revenue tracking with charts
  - Upcoming appointments preview
  - Quick action buttons
- **UI/UX**: Premium cards with glass effects, responsive grid
- **Components**: `PremiumDashboard.svelte`, `StatsCard.svelte`
- **Svelte 5 Runes**: `$state` for dashboard data, `$derived` for computed metrics

#### 5. `/dashboard/advanced` - Advanced Analytics (Premium Feature)
- **Model Connection**: Complex queries across all models with date filtering
- **API Endpoints**: `GET /api/base/analytics/`
- **Features**:
  - Plotly.js interactive charts (revenue trends, service performance)
  - Customer segmentation analysis
  - Peak hours heatmap with booking density
  - Growth metrics and KPI tracking
- **UI/UX**: Full-screen analytics with premium visualizations
- **Components**: `AnalyticsDashboard.svelte`, `ActivityHeatmap.svelte`
- **Svelte 5 Runes**: `$state` for chart data, `$effect` for chart updates

### C. Business Management Pages

#### 6. `/business/setup` - Business Profile Setup
- **Model Connection**: BusinessProfile CRUD operations
- **API Endpoints**: `POST /api/accounts/business-profile/`, `POST /api/base/qr/business/`
- **Features**:
  - Business information form with Arabic support
  - **Leaflet Map Integration**: Automatic location detection for latitude/longitude
  - **Location Sharing**: Share detected location to WhatsApp automatically
  - Working hours management
  - Service type selection
- **UI/UX**: Step-by-step setup wizard
- **Components**: `BusinessSetupWizard.svelte`, `LocationPicker.svelte`
- **Svelte 5 Runes**: `$state` for form data, `$effect` for location detection

#### 7. `/business/profile` - Business Profile Management
- **Model Connection**: BusinessProfile update operations
- **API Endpoints**: `PUT/PATCH /api/accounts/business-profile/`
- **Features**:
  - Business info editing
  - **Leaflet Maps**: Interactive map for location updates
  - **Location Sharing**: One-click WhatsApp location sharing
  - Image gallery management
  - QR code generation and display
- **Svelte 5 Runes**: `$state` for profile data, `$derived` for validation

### D. Service Management Pages

#### 8. `/services` - Service Management Interface
- **Model Connection**: Service model with business filtering
- **API Endpoints**: `GET /api/base/services/`, `POST /api/base/services/bulk-update/`
- **Features**:
  - Service list with search/filter
  - Bulk operations (enable/disable, pricing updates)
  - Arabic/English dual descriptions
  - Duration and pricing management
- **UI/UX**: Data table with inline editing, shadcn-svelte components
- **Components**: `ServiceManager.svelte`, `ServiceCard.svelte`
- **Svelte 5 Runes**: `$state` for service list, `$derived` for filtered results

#### 9. `/services/new` - Service Creation
- **Model Connection**: Service model creation
- **API Endpoints**: `POST /api/base/services/`
- **Features**:
  - Rich form with validation
  - Duration picker (HH:MM:SS format)
  - Pricing calculator
  - Arabic description support
- **Svelte 5 Runes**: `$state` for form data, `$effect` for validation

### E. Booking Management Pages

#### 10. `/bookings` - Booking Management Dashboard
- **Model Connection**: Booking model with customer/service joins
- **API Endpoints**: `GET /api/base/bookings/`, `POST /api/base/bookings/bulk-update/`
- **Features**:
  - Booking list with advanced filters (status, date range)
  - Status updates with workflow validation
  - Bulk operations for booking management
  - QR code generation for bookings
- **UI/UX**: Data table with status badges, quick actions
- **Components**: `BookingManager.svelte`, `BookingCard.svelte`
- **Svelte 5 Runes**: `$state` for bookings, `$derived` for filtered/sorted data

#### 11. `/bookings/calendar` - Calendar View
- **Model Connection**: Booking model with date/time aggregation
- **API Endpoints**: `GET /api/base/bookings/?date_from&date_to`
- **Features**:
  - Monthly/weekly/daily views
  - Drag-and-drop rescheduling
  - Time slot availability display
  - Conflict detection
- **UI/UX**: Full-calendar integration with premium styling
- **Components**: `BookingCalendar.svelte`
- **Svelte 5 Runes**: `$state` for calendar data, `$effect` for date changes

#### 12. `/bookings/new` - Manual Booking Creation
- **Model Connection**: Booking + Customer model creation
- **API Endpoints**: `POST /api/base/bookings/`, `GET /api/base/public/business/{id}/service/{id}/slots/`
- **Features**:
  - Customer search/creation
  - Service selection with pricing
  - Time slot validation
  - WhatsApp notification trigger
- **Components**: `BookingForm.svelte`
- **Svelte 5 Runes**: `$state` for booking form, `$derived` for availability

### F. Customer Management Pages

#### 13. `/customers` - Customer Relationship Management
- **Model Connection**: Customer model with booking history aggregation
- **API Endpoints**: `GET /api/base/customers/`
- **Features**:
  - Customer list with search/filter
  - Booking history per customer
  - Customer analytics (total spent, frequency)
  - Export customer data
- **UI/UX**: CRM-style interface with customer cards
- **Components**: `CustomerManager.svelte`, `CustomerCard.svelte`
- **Svelte 5 Runes**: `$state` for customer list, `$derived` for analytics

#### 14. `/customers/[id]` - Customer Profile
- **Model Connection**: Customer detail with related bookings/reviews
- **API Endpoints**: `GET /api/base/customers/{id}/`
- **Features**:
  - Complete booking history
  - Favorite services analysis
  - Customer communication log
  - **WhatsApp Integration**: Direct messaging with location sharing
- **Svelte 5 Runes**: `$state` for customer data, `$derived` for statistics

### G. Public Booking Pages (No Authentication)

#### 15. `/book/[businessId]` - Public Booking Interface
- **Model Connection**: BusinessProfile, Service, Customer, Booking models
- **API Endpoints**: `GET /api/base/public/business/{id}/services/`, `POST /api/base/public/booking/`
- **Features**:
  - Business information display
  - **Leaflet Map**: Business location with automatic detection
  - **Location Sharing**: Share business location to WhatsApp
  - Service selection with pricing
  - Available time slots (real-time)
  - Anonymous customer booking (phone + name)
- **UI/UX**: Mobile-first design, Arabic support, shadcn-svelte components
- **Components**: `PublicBookingForm.svelte`, `ServiceSelector.svelte`
- **Svelte 5 Runes**: `$state` for booking process, `$effect` for location detection

#### 16. `/book/public/success/[bookingId]` - Booking Confirmation
- **Model Connection**: Booking lookup with QR code generation
- **API Endpoints**: `GET /api/base/public/booking/{id}/`
- **Features**:
  - Booking details display
  - QR code for easy check-in
  - WhatsApp confirmation message
  - Cancellation instructions
- **Svelte 5 Runes**: `$state` for booking data

### H. Subscription & Payment Pages

#### 17. `/subscription` - Subscription Management
- **Model Connection**: Subscription model with tier comparison
- **API Endpoints**: `GET /api/base/subscription-status/`, `GET /api/accounts/subscriptions/`
- **Features**:
  - Current subscription status
  - Feature comparison table
  - Upgrade/downgrade options
  - Billing history
- **UI/UX**: Pricing cards with feature highlights, shadcn-svelte components
- **Components**: `SubscriptionCard.svelte`
- **Svelte 5 Runes**: `$state` for subscription data

#### 18. `/subscription/upgrade` - Subscription Upgrade
- **Model Connection**: Subscription model updates
- **API Endpoints**: `POST /api/accounts/subscriptions/`
- **Features**:
  - Tier selection (Basic 30 SAR, Standard 45 SAR, Premium 60 SAR)
  - Payment processing integration
  - Feature unlocking confirmation
- **Svelte 5 Runes**: `$state` for upgrade process

### I. Notification & Communication Pages

#### 19. `/notifications` - Notification Center
- **Model Connection**: Notification model with user filtering
- **API Endpoints**: `GET /api/base/notifications/`, `POST /api/base/notifications/mark-all-read/`
- **Features**:
  - Notification feed with read/unread status
  - WhatsApp delivery status
  - Bulk mark as read functionality
- **Components**: `NotificationCenter.svelte`
- **Svelte 5 Runes**: `$state` for notifications, `$effect` for real-time updates

### J. QR Code & Mobile Integration Pages

#### 20. `/qr/business/[businessId]` - QR Code Landing
- **Model Connection**: BusinessProfile with service listing
- **API Endpoints**: `GET /api/accounts/business-profile/{id}/`
- **Features**:
  - Mobile-optimized business profile
  - **Leaflet Map**: Location display with share to WhatsApp
  - Quick booking interface
  - One-tap phone calling
- **Svelte 5 Runes**: `$state` for business data

#### 21. `/qr/booking/[bookingId]` - Booking QR View
- **Model Connection**: Booking model with customer details
- **API Endpoints**: `GET /api/base/qr/booking/{id}/`
- **Features**:
  - Booking verification interface
  - Status updates (check-in/check-out)
  - Customer information display
- **Svelte 5 Runes**: `$state` for booking status

## Technical Implementation Requirements

### Frontend Technology Stack
- **Framework**: SvelteKit with Svelte 5 runes ($state, $derived, $effect)
- **UI Components**: shadcn-svelte with bits-ui primitives
- **Styling**: TailwindCSS v4 with RTL Arabic support
- **Maps**: Leaflet.js with automatic location detection
- **Charts**: Plotly.js for premium analytics
- **Responsive**: Mobile-first design approach

### Design System Requirements
- **Premium UI/UX**: Glass morphism effects, premium color schemes
- **Bilingual Support**: Arabic/English with proper RTL handling
- **Saudi Localization**: +966 phone format, Riyadh timezone
- **Accessibility**: WCAG compliance, keyboard navigation
- **Performance**: Loading states, skeleton screens, optimized images

### Integration Features
- **WhatsApp Integration**: Location sharing, booking confirmations
- **Leaflet Maps**: Auto-location detection, business location display
- **QR Codes**: Booking verification, business profile sharing
- **Real-time Updates**: WebSocket for live booking status
- **Offline Support**: PWA capabilities for core functionality

### API Integration Patterns
- **Authentication**: JWT tokens with refresh handling
- **Error Handling**: Centralized error management with user-friendly messages
- **Loading States**: Consistent loading indicators across all pages
- **Form Validation**: Real-time validation with Arabic error messages
- **Subscription Enforcement**: Feature gating based on subscription tier

### Svelte 5 Runes Usage Patterns
- **$state**: Form data, component state, API responses
- **$derived**: Computed values, filtered lists, validation results
- **$effect**: Side effects, API calls, event listeners, location detection

### shadcn-svelte Components Usage
- **Forms**: Input, Label, Button, Select, Textarea
- **Data Display**: Card, Table, Badge, Avatar
- **Navigation**: Tabs, Dialog, Sheet, Popover
- **Feedback**: Alert, Progress, Toast (Sonner)

### TailwindCSS v4 Features
- **RTL Support**: `dir-rtl:` and `dir-ltr:` variants
- **Premium Effects**: Glass morphism, gradients, shadows
- **Responsive Design**: Mobile-first breakpoints
- **Arabic Typography**: Font families and text rendering

## API Documentation Requirements

### Context7 Documentation Lookup
- **Leaflet Maps**: Best practices for location detection and mobile integration
- **Plotly.js**: Advanced chart configurations and interactive features
- **shadcn-svelte**: Component patterns and accessibility guidelines
- **SvelteKit**: SSR patterns, data loading, and form actions
- **TailwindCSS**: RTL support and premium design patterns

### Error Handling Patterns
- **Network Errors**: Retry mechanisms and offline states
- **Validation Errors**: Field-level error display
- **Authentication Errors**: Token refresh and re-authentication
- **Subscription Errors**: Upgrade prompts and feature gating

## Implementation Priority

### Phase 1: Core Authentication & Dashboard (Pages 1-4)
1. Implement `/auth/login` with JWT authentication
2. Create `/auth/register` with multi-step wizard
3. Build `/dashboard` with real-time statistics
4. Add `/dashboard/advanced` with Plotly.js charts

### Phase 2: Business & Service Management (Pages 5-9)
1. Create `/business/setup` with Leaflet integration
2. Build `/services` management interface
3. Implement service creation and editing pages
4. Add subscription management pages

### Phase 3: Booking & Customer Management (Pages 10-14)
1. Create booking management dashboard
2. Build calendar view with drag-and-drop
3. Implement customer management CRM
4. Add customer profile pages

### Phase 4: Public Interface & QR Integration (Pages 15-21)
1. Create public booking interface with Leaflet maps
2. Implement QR code landing pages
3. Add notification center
4. Build mobile-optimized views

### Quality Assurance Requirements
- **Testing**: Unit tests for components, integration tests for forms
- **Performance**: Lighthouse scores >90, Core Web Vitals compliance
- **Accessibility**: WCAG 2.1 AA compliance, keyboard navigation
- **Security**: XSS protection, CSRF tokens, input sanitization
- **Browser Support**: Modern browsers, Progressive Enhancement

This comprehensive plan ensures complete coverage of all Django models while providing a premium, scalable, and localized booking platform specifically designed for the Saudi market with cutting-edge frontend technologies.