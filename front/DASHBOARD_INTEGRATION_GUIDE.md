# 🎯 Dashboard Integration Guide - Secure JWT Authentication

Complete guide for the refactored Wagtee dashboard with secure JWT authentication, role-based access control, and Arabic localization.

## 📋 Overview

The dashboard has been successfully refactored to integrate with our secure JWT authentication system:
- **Backend**: Django with secure JWT endpoints
- **Frontend**: SvelteKit dashboard with role-based content
- **Authentication**: Email-based login with automatic token refresh
- **Permissions**: Role-based access control (business_owner, admin, super_admin)
- **Localization**: Arabic UI with RTL support

## 🔧 Key Changes Made

### 1. Authentication Integration

**Before:**
```typescript
import { authStore } from '$lib/stores/auth.svelte.js';
const user = $derived(authStore.user);
const isAuthenticated = $derived(authStore.isAuthenticated);
```

**After:**
```typescript
import { auth } from '$lib/stores/auth.ts';

let authState = $state($auth);
$effect(() => {
  const unsubscribe = auth.subscribe(state => {
    authState = state;
  });
  return unsubscribe;
});

const user = $derived(authState.user);
const isAuthenticated = $derived(authState.isAuthenticated);
```

### 2. API Requests Migration

**Before:**
```typescript
const response = await businessService.getDashboardStats();
const bookingsResponse = await bookingsService.getAll({ page: 1 });
```

**After:**
```typescript
const response = await auth.authenticatedRequest('/api/base/dashboard-stats/', { 
  method: 'GET' 
});
const bookingsResponse = await auth.authenticatedRequest(
  '/api/base/bookings/?page=1&page_size=5', 
  { method: 'GET' }
);
```

### 3. Role-Based Access Control

**User Role Detection:**
```typescript
// Check specific roles
{#if auth.hasRole('business_owner')}
  <!-- Business owner content -->
{:else if auth.isAdmin()}  
  <!-- Admin content -->
{:else if auth.isSuperAdmin()}
  <!-- Super admin content -->
{/if}

// Permission checking
auth.hasActiveSubscription()  // Subscription status
auth.hasAnyRole(['admin', 'super_admin'])  // Multiple roles
```

**Role-Based Navigation:**
```typescript
// Business Owner Actions
<Button onclick={() => goto('/dashboard/services')}>
  <Sparkles class="h-5 w-5" />
  إدارة الخدمات
</Button>

// Admin Actions  
<Button onclick={() => goto('/dashboard/businesses')}>
  <Building class="h-5 w-5" />
  إدارة الأعمال
</Button>

// Super Admin Actions
<Button onclick={() => goto('/dashboard/admin')}>
  <Shield class="h-5 w-5" />
  إدارة النظام
</Button>
```

## 🎨 UI/UX Enhancements

### 1. Authentication Status Display

```typescript
<!-- Subscription Status Alert -->
{#if user && !auth.hasActiveSubscription()}
  <Alert class="mb-6" variant="destructive">
    <Crown class="h-4 w-4" />
    <AlertDescription>
      اشتراكك غير نشط. 
      <Button variant="link" onclick={() => goto('/subscription')}>
        قم بتفعيل الاشتراك الآن
      </Button>
    </AlertDescription>
  </Alert>
{/if}
```

### 2. Role-Based User Information

```typescript
<!-- User Role Badge -->
{#if auth.isSuperAdmin()}
  <div class="flex items-center gap-2 text-muted-foreground">
    <Shield class="h-5 w-5 text-primary" />
    <span class="font-semibold">مدير عام</span>
  </div>
{:else if auth.isAdmin()}
  <div class="flex items-center gap-2 text-muted-foreground">
    <Crown class="h-5 w-5 text-primary" />
    <span class="font-semibold">مدير</span>
  </div>
{:else if auth.hasRole('business_owner')}
  <div class="flex items-center gap-2 text-muted-foreground">
    <Building class="h-5 w-5 text-primary" />
    <span class="font-semibold">صاحب عمل</span>
  </div>
{/if}
```

### 3. Subscription Status Indicators

```typescript
<!-- Active Subscription -->
{#if auth.hasActiveSubscription()}
  <Badge variant="success" class="flex items-center gap-1">
    <Crown class="h-3 w-3" />
    اشتراك نشط
  </Badge>
{:else}
  <Badge variant="destructive" class="flex items-center gap-1">
    <AlertCircle class="h-3 w-3" />
    اشتراك منتهي
  </Badge>
{/if}
```

## 🔒 Security Features

### 1. Automatic Token Refresh
- Tokens automatically refresh when making API requests
- Automatic retry on 401 Unauthorized responses
- Fallback to logout if refresh fails

### 2. Route Protection
- Automatic redirect to `/login` if not authenticated
- Role-based content rendering
- Subscription-based feature access

### 3. Secure API Communication
```typescript
// All API calls use authenticated requests
const handleDeleteBooking = async (booking: any) => {
  const response = await auth.authenticatedRequest(`/api/base/bookings/${booking.id}/`, {
    method: 'DELETE'
  });
  if (response.ok) {
    await loadBookingsData();
  }
};
```

## 📊 Role-Based Dashboard Content

### Business Owner Dashboard
- **Features**: Service management, customer management, booking calendar
- **Stats**: Today's bookings, revenue, customers, ratings
- **Quick Actions**: Create booking, manage services, view customers
- **Subscription**: Alert if inactive, upgrade prompts

### Admin Dashboard  
- **Features**: Business management, user management, system operations
- **Stats**: Total users, pending operations, system health
- **Quick Actions**: Manage businesses, manage users, system reports
- **Access**: Multiple business oversight, user administration

### Super Admin Dashboard
- **Features**: System administration, platform analytics, global controls
- **Stats**: Platform metrics, user activity, system performance  
- **Quick Actions**: System admin, comprehensive analytics, global settings
- **Access**: Full platform control, all data access

## 🌐 API Endpoint Integration

### Dashboard Data Endpoints
```typescript
// Dashboard statistics
GET /api/base/dashboard-stats/

// Subscription status  
GET /api/accounts/subscription-status/

// Bookings with pagination
GET /api/base/bookings/?page=1&page_size=5

// User permissions
GET /api/accounts/permissions/
```

### CRUD Operations
```typescript
// Services
GET /api/base/services/?page=1&page_size=50
DELETE /api/base/services/{id}/

// Bookings  
GET /api/base/bookings/?page=1&page_size=50&ordering=-appointment_date,-appointment_time
DELETE /api/base/bookings/{id}/

// Customers
GET /api/base/customers/?page=1&page_size=50
```

## 🚀 Performance Optimizations

### 1. Lazy Loading
- Data loads only when tabs are accessed
- Prevents unnecessary API calls on initial load
- Caches data between tab switches

### 2. Efficient State Management
```typescript
// Load data only when needed
const handleTabChange = async (tab: string) => {
  switch (tab) {
    case 'bookings':
      if (bookingsData.length === 0) await loadBookingsData();
      break;
    case 'services': 
      if (servicesData.length === 0) await loadServicesData();
      break;
  }
};
```

### 3. Authenticated Request Caching
- Authentication headers cached per request
- Automatic token refresh prevents unnecessary login prompts
- Request failures handled gracefully with user feedback

## 📱 Mobile Responsiveness

### 1. Adaptive UI
- Mobile-first responsive design
- Touch-friendly interface elements
- Collapsible navigation for small screens

### 2. Arabic RTL Support
```css
/* RTL support */
:global([dir="rtl"]) .space-x-4 > * + * {
  margin-left: 0;
  margin-right: 1rem;
}
```

## 🎯 User Experience Improvements

### 1. Loading States
```typescript
{#if isLoading}
  <div class="flex items-center justify-center py-20">
    <div class="space-y-4 text-center">
      <div class="h-12 w-12 animate-spin rounded-full border-4 border-primary/20 border-t-primary mx-auto"></div>
      <p class="text-lg font-semibold text-muted-foreground">جاري تحميل البيانات...</p>
    </div>
  </div>
{/if}
```

### 2. Error Handling
```typescript
{#if error}
  <div class="text-center py-20">
    <div class="space-y-6">
      <AlertCircle class="h-20 w-20 text-destructive mx-auto" />
      <h3 class="text-xl font-bold">حدث خطأ</h3>
      <p class="text-muted-foreground">{error}</p>
      <Button onclick={() => window.location.reload()}>
        إعادة التحميل
      </Button>
    </div>
  </div>
{/if}
```

### 3. Empty States
```typescript
{#if bookingsData.length === 0}
  <div class="text-center py-20">
    <Calendar class="h-20 w-20 text-muted-foreground mx-auto mb-6" />
    <h3 class="text-xl font-bold mb-3">لا توجد حجوزات حالياً</h3>
    <p class="text-muted-foreground mb-8">ابدأ بإنشاء أول حجز في نظامك</p>
    <Button onclick={() => goto('/dashboard/bookings/new')}>
      إنشاء حجز جديد
    </Button>
  </div>
{/if}
```

## 🔧 Development Commands

### Frontend Development
```bash
# Start development server
cd front && npm run dev

# Build for production  
npm run build

# Preview production build
npm run preview
```

### Backend Integration
```bash
# Start Django server
cd back && python manage.py runserver

# Test secure JWT endpoints
curl -X POST http://localhost:8000/api/accounts/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@wagtee.sa", "password": "admin123"}'
```

## ✅ Integration Checklist

- [x] **Authentication Integration**: Secure JWT auth service integrated
- [x] **Role-Based Access**: Business owner, admin, super admin roles implemented  
- [x] **API Migration**: All endpoints use authenticated requests
- [x] **Subscription Management**: Active/inactive status with alerts
- [x] **Arabic Localization**: RTL support and Arabic UI text
- [x] **Error Handling**: Comprehensive error states and user feedback
- [x] **Loading States**: Smooth loading transitions and indicators
- [x] **Mobile Responsive**: Mobile-first design with touch support
- [x] **Data Security**: All sensitive data requests authenticated
- [x] **Token Management**: Automatic refresh and secure logout
- [x] **Route Protection**: Automatic redirect for unauthenticated users
- [x] **Permission Checking**: Granular role-based content rendering

## 🚨 Security Considerations

### 1. Token Security
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days with rotation
- Automatic token blacklisting on logout
- No sensitive data in localStorage

### 2. API Security
- All dashboard data requires authentication
- Role-based API endpoint access
- Automatic retry with token refresh on 401
- Secure error handling without data exposure

### 3. Frontend Security
- XSS protection through proper data sanitization
- CSRF protection via JWT tokens
- Secure route protection and redirects
- No hardcoded credentials or tokens

## 📚 Additional Resources

- [SvelteKit Authentication Guide](https://kit.svelte.dev/docs/authentication)
- [JWT Security Best Practices](https://tools.ietf.org/html/rfc8725)  
- [Role-Based Access Control](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Arabic Web Design Guidelines](https://www.w3.org/International/articles/arabic-layout/)

---

**Status**: ✅ Complete - Dashboard fully integrated with secure JWT authentication
**Security**: 🔒 Production-ready with comprehensive role-based access control
**User Experience**: 🎨 Modern Arabic UI with excellent mobile responsiveness