// =============================================================================
// SVELTE 5 AUTH STORE - Advanced Patterns with Email-First Auth
// =============================================================================

import type { User, LoginForm, RegisterForm } from '$lib/types/index.js';
import { api } from '$lib/services/api-client.js';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

// =============================================================================
// ADVANCED AUTH STORE WITH REACTIVE DERIVATIONS
// =============================================================================

function createAuthStore() {
	// Core state
	let user = $state<User | null>(null);
	let isLoading = $state(false);
	let error = $state<string | null>(null);
	
	// Email verification state
	let emailVerificationSent = $state(false);
	let pendingEmail = $state<string | null>(null);
	
	// Token management
	let tokenExpiresAt = $state<number | null>(null);
	let refreshTimer: NodeJS.Timeout | null = null;

	// Reactive derivations
	const isAuthenticated = $derived(user !== null);
	const isEmailVerified = $derived(user?.is_verified ?? false);
	const userRole = $derived(user?.role ?? null);
	const subscriptionTier = $derived(user?.subscription.tier ?? 'basic');
	const isSubscriptionActive = $derived(user?.subscription.is_active ?? false);
	
	const isTokenExpiringSoon = $derived(() => {
		if (!tokenExpiresAt) return false;
		return Date.now() + (5 * 60 * 1000) > tokenExpiresAt; // 5 minutes before expiry
	});

	const canAccessFeature = $derived((feature: string): boolean => {
		if (!user?.subscription.features) return false;
		return user.subscription.features[feature] || false;
	});

	const hasPermission = $derived((resource: string, action: string): boolean => {
		if (!user) return false;
		// Role-based permission check
		const rolePermissions: Record<string, string[]> = {
			'super_admin': ['*'],
			'admin': ['users:read', 'users:update', 'business:*'],
			'business_owner': ['business:*', 'services:*', 'bookings:*', 'customers:*']
		};
		
		const permissions = rolePermissions[user.role] || [];
		return permissions.includes('*') || 
			   permissions.includes(`${resource}:*`) || 
			   permissions.includes(`${resource}:${action}`);
	});

	const store = {
		// State getters
		get user() { return user; },
		get isLoading() { return isLoading; },
		get error() { return error; },
		get emailVerificationSent() { return emailVerificationSent; },
		get pendingEmail() { return pendingEmail; },
		
		// Reactive getters
		get isAuthenticated() { return isAuthenticated; },
		get isEmailVerified() { return isEmailVerified; },
		get userRole() { return userRole; },
		get subscriptionTier() { return subscriptionTier; },
		get isSubscriptionActive() { return isSubscriptionActive; },
		get isTokenExpiringSoon() { return isTokenExpiringSoon; },
		get canAccessFeature() { return canAccessFeature; },
		get hasPermission() { return hasPermission; },

		// Persistent state management
		initializeFromStorage() {
			if (!browser) return;
			
			const storedTokenExpiration = store.getTokenExpirationFromStorage();
			if (storedTokenExpiration && storedTokenExpiration > Date.now()) {
				tokenExpiresAt = storedTokenExpiration;
				// Check auth if we have valid tokens
				if (api.getAccessToken()) {
					store.checkAuth();
				}
			} else if (storedTokenExpiration) {
				// Token expired, clear everything
				store.clearAuthData();
			}
		},

		// Actions
		async login(email: string, password: string, rememberMe: boolean = true) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.login({ email, password, remember_me: rememberMe });
				
				if (response.success && response.data) {
					user = response.data.user;
					api.setTokens(response.data.access, response.data.refresh);
					
					// Set token expiration (JWT tokens typically expire in 1 hour)
					tokenExpiresAt = Date.now() + (60 * 60 * 1000); // 1 hour from now
					store.setTokenExpirationInStorage(tokenExpiresAt);
					
					store.startAutoRefresh();
					return { success: true };
				} else {
					error = response.error || 'Login failed';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async register(data: RegisterForm) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.register(data);
				
				if (response.success && response.data) {
					user = response.data.user;
					api.setTokens(response.data.access, response.data.refresh);
					
					// Set token expiration (JWT tokens typically expire in 1 hour)
					tokenExpiresAt = Date.now() + (60 * 60 * 1000); // 1 hour from now
					store.setTokenExpirationInStorage(tokenExpiresAt);
					
					store.startAutoRefresh();
					return { success: true };
				} else {
					error = response.error || 'Registration failed';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async sendEmailVerification(email: string) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.sendEmailVerification(email);
				
				if (response.success) {
					emailVerificationSent = true;
					pendingEmail = email;
					return { success: true };
				} else {
					error = response.error || 'Failed to send verification email';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async verifyEmail(email: string, code: string) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.verifyEmail(email, code);
				
				if (response.success) {
					// Update user verification status
					if (user) {
						user = { ...user, is_verified: true };
					}
					emailVerificationSent = false;
					pendingEmail = null;
					return { success: true };
				} else {
					error = response.error || 'Email verification failed';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async requestPasswordReset(email: string) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.requestPasswordReset(email);
				
				if (response.success) {
					return { success: true };
				} else {
					error = response.error || 'Failed to send password reset email';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async confirmPasswordReset(email: string, token: string, newPassword: string, confirmPassword: string) {
			isLoading = true;
			error = null;

			try {
				const response = await api.auth.confirmPasswordReset(email, token, newPassword, confirmPassword);
				
				if (response.success) {
					return { success: true };
				} else {
					error = response.error || 'Password reset failed';
					return { success: false, error };
				}
			} catch (err) {
				error = 'Network error occurred';
				return { success: false, error };
			} finally {
				isLoading = false;
			}
		},

		async logout() {
			isLoading = true;
			
			try {
				// Notify backend about logout to invalidate tokens
				await api.auth.logout();
			} catch (err) {
				console.error('Logout error:', err);
				// Continue with local cleanup even if server logout fails
			}
			
			// Clear all authentication data
			store.clearAuthData();
			isLoading = false;
			
			if (browser) {
				// Redirect to login page
				goto('/auth/login');
			}
		},

		async checkAuth() {
			if (!browser) return;
			
			const token = api.getAccessToken();
			if (!token) {
				store.clearAuthData();
				return;
			}

			// Initialize token expiration if not set but token exists
			if (!tokenExpiresAt) {
				// Assume token is relatively fresh, set expiration
				const tokenExpiration = store.getTokenExpirationFromStorage();
				if (tokenExpiration) {
					tokenExpiresAt = tokenExpiration;
				} else {
					// Default to 50 minutes from now (safe assumption for 1hr tokens)
					tokenExpiresAt = Date.now() + (50 * 60 * 1000);
				}
			}

			// Check if token is expired based on our stored expiration
			if (tokenExpiresAt && tokenExpiresAt <= Date.now()) {
				console.log('Token expired, attempting refresh...');
				await store.refreshTokenIfNeeded();
				return;
			}

			isLoading = true;
			
			try {
				const response = await api.auth.getCurrentUser();
				
				if (response.success && response.data) {
					user = response.data;
					store.startAutoRefresh();
				} else {
					// If getCurrentUser fails, token might be invalid
					console.log('getCurrentUser failed, attempting token refresh...');
					await store.refreshTokenIfNeeded();
				}
			} catch (err) {
				console.error('Auth check error:', err);
				// Clear auth data on unexpected errors
				store.clearAuthData();
			} finally {
				isLoading = false;
			}
		},

		async refreshTokenIfNeeded() {
			if (!browser) return;
			
			const refreshToken = api.getRefreshToken();
			if (!refreshToken) {
				console.log('No refresh token available, clearing auth data');
				store.clearAuthData();
				return;
			}

			console.log('Attempting token refresh...');
			try {
				const refreshSuccess = await api.forceRefreshToken();
				
				if (refreshSuccess) {
					console.log('Token refresh successful');
					// Set new token expiration
					tokenExpiresAt = Date.now() + (60 * 60 * 1000); // 1 hour from now
					store.setTokenExpirationInStorage(tokenExpiresAt);
					
					// Retry getting current user
					const userResponse = await api.auth.getCurrentUser();
					if (userResponse.success && userResponse.data) {
						user = userResponse.data;
						store.startAutoRefresh();
						console.log('User data retrieved after refresh');
					} else {
						console.log('Failed to get user data after refresh, clearing auth');
						store.clearAuthData();
					}
				} else {
					console.log('Token refresh failed, clearing auth data');
					store.clearAuthData();
				}
			} catch (err) {
				console.error('Token refresh error:', err);
				store.clearAuthData();
			}
		},

		clearError() {
			error = null;
		},

		resetEmailVerification() {
			emailVerificationSent = false;
			pendingEmail = null;
			error = null;
		},

		getTokenExpirationFromStorage(): number | null {
			if (!browser) return null;
			const stored = localStorage.getItem('token_expires_at');
			return stored ? parseInt(stored, 10) : null;
		},

		setTokenExpirationInStorage(expiresAt: number) {
			if (!browser) return;
			localStorage.setItem('token_expires_at', expiresAt.toString());
		},

		clearTokenExpirationFromStorage() {
			if (!browser) return;
			localStorage.removeItem('token_expires_at');
		},

		startAutoRefresh() {
			if (!browser || !tokenExpiresAt) return;
			
			// Store expiration time
			store.setTokenExpirationInStorage(tokenExpiresAt);
			
			if (refreshTimer) {
				clearTimeout(refreshTimer);
			}
			
			// Refresh 5 minutes before expiry
			const refreshTime = tokenExpiresAt - Date.now() - (5 * 60 * 1000);
			
			if (refreshTime > 0) {
				refreshTimer = setTimeout(async () => {
					await store.refreshTokenIfNeeded();
				}, refreshTime);
			}
		},

		clearAuthData() {
			console.log('Clearing all auth data...');
			api.clearTokens();
			store.clearTokenExpirationFromStorage();
			user = null;
			tokenExpiresAt = null;
			emailVerificationSent = false;
			pendingEmail = null;
			error = null;
			
			if (refreshTimer) {
				clearTimeout(refreshTimer);
				refreshTimer = null;
			}
		},

		// Manual cleanup method for development/debugging
		forceLogout() {
			console.log('Force logout - clearing all auth data');
			store.clearAuthData();
			if (browser) {
				goto('/auth/login');
			}
		},

		// Debug helper to check auth status
		debugAuthStatus() {
			console.log('=== AUTH DEBUG STATUS ===');
			console.log('User:', user);
			console.log('IsAuthenticated:', isAuthenticated);
			console.log('IsLoading:', isLoading);
			console.log('Error:', error);
			console.log('TokenExpiresAt:', tokenExpiresAt);
			console.log('Access Token:', api.getAccessToken()?.substring(0, 20) + '...' || 'None');
			console.log('Refresh Token:', api.getRefreshToken()?.substring(0, 20) + '...' || 'None');
			console.log('Stored Token Expiration:', store.getTokenExpirationFromStorage());
			console.log('========================');
		},

		handleSubscriptionError(errorResponse: any) {
			if (errorResponse?.code === 'SUBSCRIPTION_REQUIRED') {
				if (browser) {
					goto('/subscription?expired=true');
				}
				return true;
			}
			return false;
		}
	};

	// Initialize from localStorage on browser after store creation
	if (browser) {
		// Use setTimeout to defer initialization until after store is fully created
		setTimeout(() => {
			const storedTokenExpiration = store.getTokenExpirationFromStorage();
			const accessToken = api.getAccessToken();
			
			console.log('🔐 Auth store initialization:');
			console.log('- Access token exists:', !!accessToken);
			console.log('- Access token preview:', accessToken?.substring(0, 30) + '...' || 'None');
			console.log('- Stored expiration:', storedTokenExpiration);
			console.log('- Current time:', Date.now());
			console.log('- Is expired:', storedTokenExpiration ? storedTokenExpiration <= Date.now() : 'No expiration');
			
			if (accessToken) {
				if (storedTokenExpiration && storedTokenExpiration > Date.now()) {
					console.log('✅ Valid tokens found, checking auth...');
					tokenExpiresAt = storedTokenExpiration;
					store.checkAuth();
				} else {
					console.log('⚠️ Token exists but may be expired, attempting to check auth anyway...');
					// Try to check auth even without expiration data
					store.checkAuth();
				}
			} else {
				console.log('❌ No access token found, clearing auth data...');
				store.clearAuthData();
			}
		}, 0);
	}

	return store;
}

// Export the store factory instead of a singleton to avoid $effect orphan errors
export const authStore = createAuthStore();
export const auth = authStore; // Backward compatibility alias
export { createAuthStore };

// Add to window for debugging in browser console
if (browser && typeof window !== 'undefined') {
	(window as any).debugAuth = authStore.debugAuthStatus;
	(window as any).clearAuth = authStore.forceLogout;
	(window as any).checkAuth = authStore.checkAuth;
	(window as any).refreshAuth = authStore.refreshTokenIfNeeded;
}