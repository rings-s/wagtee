/**
 * Secure JWT Authentication Service for Wagtee Frontend
 * Integrates with Django secure JWT backend endpoints
 */

export interface User {
  id: number;
  email: string;
  role: 'business_owner' | 'admin' | 'super_admin';
  is_verified: boolean;
  subscription_active: boolean;
  last_login: string | null;
  first_name?: string;
  last_name?: string;
  business_name?: string;
}

export interface LoginResponse {
  refresh: string;
  access: string;
  user: User;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthError {
  detail?: string;
  email?: string[];
  password?: string[];
  non_field_errors?: string[];
}

class AuthService {
  private static instance: AuthService;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private user: User | null = null;
  private baseURL = 'http://localhost:8000/api/accounts';
  private refreshPromise: Promise<void> | null = null;

  private constructor() {
    this.loadTokensFromStorage();
  }

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * Load tokens from localStorage on initialization
   */
  private loadTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          this.user = JSON.parse(userStr);
        } catch (e) {
          console.error('Error parsing stored user data:', e);
          this.clearStorage();
        }
      }
    }
  }

  /**
   * Store tokens securely in localStorage
   */
  private storeTokens(tokens: AuthTokens, user?: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
        this.user = user;
      }
    }
    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
  }

  /**
   * Clear all stored authentication data
   */
  private clearStorage(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
    this.accessToken = null;
    this.refreshToken = null;
    this.user = null;
  }

  /**
   * Login with email and password using secure JWT endpoint
   */
  async login(email: string, password: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData: AuthError = await response.json();
        throw new Error(this.formatErrorMessage(errorData));
      }

      const data: LoginResponse = await response.json();
      
      // Store tokens and user data
      this.storeTokens({
        access: data.access,
        refresh: data.refresh
      }, data.user);

      return data.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Refresh access token using secure JWT endpoint
   */
  async refreshAccessToken(): Promise<void> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    this.refreshPromise = this._performRefresh();
    try {
      await this.refreshPromise;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async _performRefresh(): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (!response.ok) {
        // If refresh fails, clear tokens and require re-login
        this.clearStorage();
        throw new Error('Token refresh failed - please login again');
      }

      const data = await response.json();
      
      // Update stored tokens (refresh token may be rotated)
      this.storeTokens({
        access: data.access,
        refresh: data.refresh || this.refreshToken, // Use new refresh token if provided
      });

    } catch (error) {
      this.clearStorage();
      throw error;
    }
  }

  /**
   * Logout using secure JWT endpoint with token blacklisting
   */
  async logout(): Promise<void> {
    try {
      if (this.refreshToken) {
        await fetch(`${this.baseURL}/auth/logout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...this.getAuthHeaders(),
          },
          body: JSON.stringify({ refresh: this.refreshToken }),
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with local cleanup even if server logout fails
    } finally {
      this.clearStorage();
    }
  }

  /**
   * Get authorization headers for API requests
   */
  getAuthHeaders(): Record<string, string> {
    return this.accessToken ? {
      'Authorization': `Bearer ${this.accessToken}`
    } : {};
  }

  /**
   * Make authenticated API request with automatic token refresh
   */
  async authenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    // First attempt with current token
    let response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        ...this.getAuthHeaders(),
      },
    });

    // If unauthorized and we have a refresh token, try refreshing
    if (response.status === 401 && this.refreshToken) {
      try {
        await this.refreshAccessToken();
        
        // Retry request with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            ...this.getAuthHeaders(),
          },
        });
      } catch (refreshError) {
        // Refresh failed, redirect to login
        this.clearStorage();
        throw new Error('Authentication expired - please login again');
      }
    }

    return response;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.accessToken && !!this.user;
  }

  /**
   * Get current user data
   */
  getCurrentUser(): User | null {
    return this.user;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: string): boolean {
    return this.user?.role === role;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles: string[]): boolean {
    return !!this.user?.role && roles.includes(this.user.role);
  }

  /**
   * Check if user is admin or super_admin
   */
  isAdmin(): boolean {
    return this.hasAnyRole(['admin', 'super_admin']);
  }

  /**
   * Check if user is super_admin
   */
  isSuperAdmin(): boolean {
    return this.hasRole('super_admin');
  }

  /**
   * Check if user has active subscription
   */
  hasActiveSubscription(): boolean {
    return !!this.user?.subscription_active;
  }

  /**
   * Format error messages from backend
   */
  private formatErrorMessage(error: AuthError): string {
    if (error.detail) return error.detail;
    if (error.non_field_errors?.length) return error.non_field_errors[0];
    if (error.email?.length) return `Email: ${error.email[0]}`;
    if (error.password?.length) return `Password: ${error.password[0]}`;
    return 'Authentication failed';
  }

  /**
   * Subscribe to authentication state changes
   */
  onAuthStateChanged(callback: (user: User | null) => void): () => void {
    // Simple implementation - in a real app, you might use a more sophisticated observer pattern
    const checkAuth = () => {
      callback(this.getCurrentUser());
    };

    // Check immediately
    checkAuth();

    // Set up periodic check (every 30 seconds)
    const interval = setInterval(checkAuth, 30000);

    // Return cleanup function
    return () => clearInterval(interval);
  }
}

// Export singleton instance
export const authService = AuthService.getInstance();
export default authService;