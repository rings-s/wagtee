import { redirect } from '@sveltejs/kit';
import type { User } from '$lib/types/index.js';

export interface AuthContext {
	user: User | null;
	isAuthenticated: boolean;
	subscription_active: boolean;
	subscription_tier: string | null;
}

export type RouteProtectionLevel = 
	| 'public' 
	| 'authenticated' 
	| 'active_subscription' 
	| 'premium_features' 
	| 'admin' 
	| 'super_admin';

// Route protection configuration
export const routeProtection: Record<string, RouteProtectionLevel> = {
	// Public routes
	'/': 'public',
	'/about': 'public',
	'/help': 'public',
	'/auth/login': 'public',
	'/auth/register': 'public',
	'/book/[businessId]': 'public',
	'/book/lookup': 'public',
	'/qr/[businessId]': 'public',

	// Authenticated routes
	'/dashboard': 'authenticated',
	'/business/setup': 'authenticated',
	'/settings': 'authenticated',

	// Active subscription required
	'/business/profile': 'active_subscription',
	'/services': 'active_subscription',
	'/bookings': 'active_subscription',
	'/customers': 'active_subscription',

	// Premium features
	'/dashboard/advanced': 'premium_features',
	'/dashboard/reports': 'premium_features',
	'/business/qr': 'premium_features',

	// Admin routes
	'/admin': 'admin',
	'/admin/users': 'admin',
	'/admin/businesses': 'admin',

	// Super admin routes
	'/admin/system': 'super_admin',
	'/admin/subscriptions': 'super_admin',
};

export function checkRouteAccess(pathname: string, context: AuthContext): {
	allowed: boolean;
	redirectTo?: string;
	reason?: string;
} {
	const protection = getRouteProtection(pathname);
	
	switch (protection) {
		case 'public':
			return { allowed: true };

		case 'authenticated':
			if (!context.isAuthenticated) {
				return { 
					allowed: false, 
					redirectTo: `/auth/login?redirect=${encodeURIComponent(pathname)}`,
					reason: 'Authentication required'
				};
			}
			return { allowed: true };

		case 'active_subscription':
			if (!context.isAuthenticated) {
				return { 
					allowed: false, 
					redirectTo: `/auth/login?redirect=${encodeURIComponent(pathname)}`,
					reason: 'Authentication required'
				};
			}
			if (!context.subscription_active) {
				return { 
					allowed: false, 
					redirectTo: '/subscription?expired=true',
					reason: 'Active subscription required'
				};
			}
			return { allowed: true };

		case 'premium_features':
			if (!context.isAuthenticated) {
				return { 
					allowed: false, 
					redirectTo: `/auth/login?redirect=${encodeURIComponent(pathname)}`,
					reason: 'Authentication required'
				};
			}
			if (!context.subscription_active) {
				return { 
					allowed: false, 
					redirectTo: '/subscription?expired=true',
					reason: 'Active subscription required'
				};
			}
			if (!['standard', 'premium'].includes(context.subscription_tier || '')) {
				return { 
					allowed: false, 
					redirectTo: '/subscription?upgrade=standard',
					reason: 'Premium subscription required'
				};
			}
			return { allowed: true };

		case 'admin':
			if (!context.isAuthenticated) {
				return { 
					allowed: false, 
					redirectTo: `/auth/login?redirect=${encodeURIComponent(pathname)}`,
					reason: 'Authentication required'
				};
			}
			if (!['admin', 'super_admin'].includes(context.user?.role || '')) {
				return { 
					allowed: false, 
					redirectTo: '/dashboard',
					reason: 'Admin access required'
				};
			}
			return { allowed: true };

		case 'super_admin':
			if (!context.isAuthenticated) {
				return { 
					allowed: false, 
					redirectTo: `/auth/login?redirect=${encodeURIComponent(pathname)}`,
					reason: 'Authentication required'
				};
			}
			if (context.user?.role !== 'super_admin') {
				return { 
					allowed: false, 
					redirectTo: '/dashboard',
					reason: 'Super admin access required'
				};
			}
			return { allowed: true };

		default:
			return { allowed: true };
	}
}

function getRouteProtection(pathname: string): RouteProtectionLevel {
	// Direct lookup first
	if (routeProtection[pathname]) {
		return routeProtection[pathname];
	}

	// Pattern matching for dynamic routes
	for (const [pattern, protection] of Object.entries(routeProtection)) {
		if (matchesPattern(pathname, pattern)) {
			return protection;
		}
	}

	// Default to authenticated for unknown routes
	return 'authenticated';
}

function matchesPattern(pathname: string, pattern: string): boolean {
	// Convert SvelteKit route pattern to regex
	const regexPattern = pattern
		.replace(/\[([^\]]+)\]/g, '[^/]+') // Replace [param] with regex
		.replace(/\//g, '\\/'); // Escape forward slashes

	const regex = new RegExp(`^${regexPattern}$`);
	return regex.test(pathname);
}

// Server-side route guard for use in +layout.server.ts or +page.server.ts
export function serverAuthGuard(pathname: string, context: AuthContext) {
	const access = checkRouteAccess(pathname, context);
	
	if (!access.allowed && access.redirectTo) {
		throw redirect(302, access.redirectTo);
	}

	return access;
}

// Client-side route guard for use in stores or components
export function clientAuthGuard(pathname: string, context: AuthContext) {
	const access = checkRouteAccess(pathname, context);
	
	if (!access.allowed && access.redirectTo) {
		// Use browser navigation or SvelteKit's goto
		if (typeof window !== 'undefined') {
			window.location.href = access.redirectTo;
		}
	}

	return access;
}