// =============================================================================
// SVELTEKIT GLOBAL TYPES - Following 2024 Best Practices
// =============================================================================

import type { SubscriptionTier, UserRole } from '$lib/types/index.js';

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}

		interface Locals {
			user?: {
				id: number;
				email: string;
				username: string;
				role: UserRole;
				is_verified: boolean;
				subscription: {
					tier: SubscriptionTier;
					is_active: boolean;
					expires_at?: string;
				};
			};
			subscription?: {
				tier: SubscriptionTier;
				is_active: boolean;
				features: Record<string, boolean>;
				limits: {
					max_services: number;
					max_bookings_per_month: number;
					max_customers: number;
				};
			};
			session?: string;
		}

		interface PageData {
			user?: App.Locals['user'];
			subscription?: App.Locals['subscription'];
		}

		// interface PageState {}
		// interface Platform {}
	}

	// Global event handler types for consistent typing
	type FormSubmitEvent = SubmitEvent & {
		currentTarget: EventTarget & HTMLFormElement;
	};

	type InputChangeEvent = Event & {
		currentTarget: EventTarget & HTMLInputElement;
	};

	type SelectChangeEvent = Event & {
		currentTarget: EventTarget & HTMLSelectElement;
	};

	// Arabic/English form validation patterns
	type LocalizedValidation = {
		en: string;
		ar: string;
	};

	// Saudi-specific validation patterns
	type SaudiPhoneNumber = `+966${string}`;
	type SaudiCRNumber = `${number}${number}${number}${number}${number}${number}${number}${number}${number}${number}`;
}

export {};
