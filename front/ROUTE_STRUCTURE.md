# Wagtee SvelteKit Route Structure

## Authentication Routes
- `/auth/login` - Phone-based login with OTP option
- `/auth/register` - Multi-step registration with OTP verification
- `/auth/forgot-password` - Password recovery via SMS
- `/auth/verify-otp` - OTP verification page

## Public Customer Routes (No Authentication)
- `/book/[businessId]` - Public booking page for specific business
- `/book/lookup` - Booking lookup by ID and phone
- `/book/success/[bookingId]` - Booking confirmation page
- `/qr/[businessId]` - QR code landing page for quick booking

## Business Dashboard Routes (Authenticated)
- `/dashboard` - Main dashboard with overview stats
- `/dashboard/advanced` - Advanced analytics (Standard+ subscription)
- `/dashboard/calendar` - Calendar view of bookings
- `/dashboard/reports` - Business reports (Premium subscription)

## Business Management Routes
- `/business/setup` - Initial business profile setup
- `/business/profile` - Edit business profile and settings
- `/business/hours` - Manage business hours
- `/business/qr` - Generate and manage QR codes

## Service Management Routes
- `/services` - List and manage services
- `/services/create` - Create new service
- `/services/[id]/edit` - Edit service details
- `/services/[id]` - View service details and bookings

## Booking Management Routes
- `/bookings` - List all bookings with filters
- `/bookings/[id]` - View booking details
- `/bookings/calendar` - Calendar view of bookings
- `/bookings/create` - Create manual booking (walk-in)

## Customer Management Routes
- `/customers` - Customer list and management
- `/customers/[id]` - Customer profile and booking history
- `/customers/import` - Import customer data

## Subscription Management Routes
- `/subscription` - Current subscription details
- `/subscription/upgrade` - Subscription upgrade options
- `/subscription/billing` - Billing history and invoices
- `/subscription/success` - Payment success page
- `/subscription/cancelled` - Payment cancelled page

## Admin Routes (Admin/Super Admin only)
- `/admin` - Admin dashboard
- `/admin/users` - User management
- `/admin/businesses` - Business management
- `/admin/subscriptions` - Subscription management
- `/admin/system` - System settings (Super Admin only)

## Settings Routes
- `/settings` - General settings
- `/settings/profile` - User profile settings
- `/settings/notifications` - Notification preferences
- `/settings/security` - Security settings (password, 2FA)

## Help & Support Routes
- `/help` - Help center
- `/help/guide` - User guide
- `/help/contact` - Contact support
- `/help/faq` - Frequently asked questions

## API Routes (for webhooks and integrations)
- `/api/webhooks/whatsapp` - WhatsApp webhook
- `/api/qr/[businessId]` - QR code redirect handler
- `/api/subscriptions/` - Subscription management API (payment gateway to be configured post-deployment)

## Route Guards and Middleware

### Authentication Middleware
- Redirects unauthenticated users to `/auth/login`
- Handles token refresh automatically
- Stores redirect URL for post-login navigation

### Subscription Middleware
- Checks subscription status for protected features
- Redirects to upgrade page for expired subscriptions
- Enforces subscription tier limits

### Role-Based Access Control
- Restricts admin routes to admin/super_admin roles
- Prevents access to features above subscription tier
- Shows appropriate error messages for restricted access

### Route Protection Levels
1. **Public** - No authentication required
2. **Authenticated** - Valid JWT token required
3. **Active Subscription** - Active subscription required
4. **Premium Features** - Standard/Premium subscription required
5. **Admin** - Admin or Super Admin role required
6. **Super Admin** - Super Admin role only

## Route Components Structure

### Layout Components
- `+layout.svelte` - Main app layout with navigation
- `+layout@auth.svelte` - Authentication layout (clean, centered)
- `+layout@public.svelte` - Public booking layout (minimal header)
- `+layout@admin.svelte` - Admin layout with sidebar navigation

### Page Components
Each route has corresponding page components with:
- Loading states with skeleton screens
- Error boundaries with user-friendly messages
- Mobile-first responsive design
- Arabic/English language support
- Proper SEO meta tags

### Route Data Loading
- Server-side data loading where appropriate
- Client-side hydration for interactive features
- Proper error handling and fallbacks
- Cache management for frequently accessed data

### Navigation Structure
- Main navigation for authenticated users
- Mobile-friendly hamburger menu
- Breadcrumb navigation for complex flows
- Quick actions and shortcuts
- Language toggle (Arabic/English)
- User menu with role-based options