// =============================================================================
// ADVANCED SVELTE 5 STORE ARCHITECTURE
// =============================================================================
// Enterprise patterns: Generic base stores, reactive derivations,
// error handling, and dependency injection

import type { ApiResult } from '$lib/types/optimized.js';

// =============================================================================
// BASE STORE INTERFACES
// =============================================================================

/** Common async operation state */
interface AsyncState<T> {
	data: T | null;
	isLoading: boolean;
	error: string | null;
	lastUpdated: number | null;
}

/** Store configuration options */
interface StoreConfig {
	cacheTTL?: number; // Cache time-to-live in milliseconds
	retryAttempts?: number;
	debounceMs?: number;
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/** Creates a debounced function */
function debounce<T extends (...args: any[]) => any>(
	func: T,
	delay: number
): (...args: Parameters<T>) => void {
	let timeoutId: NodeJS.Timeout;
	return (...args: Parameters<T>) => {
		clearTimeout(timeoutId);
		timeoutId = setTimeout(() => func(...args), delay);
	};
}

/** Check if data is stale based on TTL */
function isStale(lastUpdated: number | null, ttl: number): boolean {
	if (!lastUpdated) return true;
	return Date.now() - lastUpdated > ttl;
}

// =============================================================================
// GENERIC BASE STORE CLASS
// =============================================================================

/** Generic base store for async operations with caching and error handling */
abstract class BaseAsyncStore<T> {
	protected state = $state<AsyncState<T>>({
		data: null,
		isLoading: false,
		error: null,
		lastUpdated: null
	});

	protected config: Required<StoreConfig>;

	constructor(config: StoreConfig = {}) {
		this.config = {
			cacheTTL: config.cacheTTL ?? 5 * 60 * 1000, // 5 minutes default
			retryAttempts: config.retryAttempts ?? 3,
			debounceMs: config.debounceMs ?? 300
		};
	}

	// Reactive getters
	get data() { return this.state.data; }
	get isLoading() { return this.state.isLoading; }
	get error() { return this.state.error; }
	get lastUpdated() { return this.state.lastUpdated; }
	
	get isStale() {
		return isStale(this.state.lastUpdated, this.config.cacheTTL);
	}

	get hasData() {
		return this.state.data !== null;
	}

	get isEmpty() {
		return !this.state.isLoading && !this.state.data && !this.state.error;
	}

	/** Execute async operation with error handling and caching */
	protected async executeOperation<R>(
		operation: () => Promise<ApiResult<R>>,
		skipCache: boolean = false
	): Promise<R | null> {
		// Return cached data if valid
		if (!skipCache && this.state.data && !this.isStale) {
			return this.state.data as unknown as R;
		}

		this.state.isLoading = true;
		this.state.error = null;

		let lastError: string | null = null;

		for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
			try {
				const result = await operation();

				if (result.success && result.data !== undefined) {
					this.state.data = result.data as unknown as T;
					this.state.lastUpdated = Date.now();
					this.state.error = null;
					this.state.isLoading = false;
					return result.data;
				} else {
					lastError = result.error || 'Operation failed';
				}
			} catch (error) {
				lastError = error instanceof Error ? error.message : 'Network error';
			}

			// Wait before retry (exponential backoff)
			if (attempt < this.config.retryAttempts) {
				await new Promise(resolve => 
					setTimeout(resolve, 1000 * Math.pow(2, attempt))
				);
			}
		}

		this.state.error = lastError;
		this.state.isLoading = false;
		return null;
	}

	/** Clear error state */
	clearError(): void {
		this.state.error = null;
	}

	/** Reset store to initial state */
	reset(): void {
		this.state.data = null;
		this.state.isLoading = false;
		this.state.error = null;
		this.state.lastUpdated = null;
	}

	/** Force refresh data (skip cache) */
	abstract refresh(): Promise<void>;

	/** Update local data optimistically */
	updateOptimistically(updater: (current: T | null) => T | null): void {
		this.state.data = updater(this.state.data);
		this.state.lastUpdated = Date.now();
	}
}

// =============================================================================
// SPECIALIZED STORE CLASSES
// =============================================================================

/** Store for managing collections with pagination */
abstract class CollectionStore<T extends { id: number }> extends BaseAsyncStore<T[]> {
	protected paginationState = $state({
		currentPage: 1,
		totalPages: 1,
		totalCount: 0,
		hasNextPage: false,
		hasPreviousPage: false
	});

	// Collection-specific getters
	get items() { return this.state.data || []; }
	get itemCount() { return this.items.length; }
	get currentPage() { return this.paginationState.currentPage; }
	get totalPages() { return this.paginationState.totalPages; }
	get totalCount() { return this.paginationState.totalCount; }
	get hasNextPage() { return this.paginationState.hasNextPage; }
	get hasPreviousPage() { return this.paginationState.hasPreviousPage; }

	/** Find item by ID */
	findById(id: number): T | undefined {
		return this.items.find(item => item.id === id);
	}

	/** Add item to collection */
	addItem(item: T): void {
		if (!this.state.data) {
			this.state.data = [item];
		} else {
			// Avoid duplicates
			const existingIndex = this.state.data.findIndex(existing => existing.id === item.id);
			if (existingIndex >= 0) {
				this.state.data[existingIndex] = item;
			} else {
				this.state.data = [...this.state.data, item];
			}
		}
		this.state.lastUpdated = Date.now();
	}

	/** Update item in collection */
	updateItem(id: number, updates: Partial<T>): void {
		if (!this.state.data) return;

		const index = this.state.data.findIndex(item => item.id === id);
		if (index >= 0) {
			this.state.data[index] = { ...this.state.data[index], ...updates };
			this.state.lastUpdated = Date.now();
		}
	}

	/** Remove item from collection */
	removeItem(id: number): void {
		if (!this.state.data) return;

		this.state.data = this.state.data.filter(item => item.id !== id);
		this.state.lastUpdated = Date.now();
	}

	/** Update pagination state */
	protected updatePagination(pagination: {
		count: number;
		next?: string;
		previous?: string;
	}, page: number, pageSize: number = 20): void {
		this.paginationState.currentPage = page;
		this.paginationState.totalCount = pagination.count;
		this.paginationState.totalPages = Math.ceil(pagination.count / pageSize);
		this.paginationState.hasNextPage = !!pagination.next;
		this.paginationState.hasPreviousPage = !!pagination.previous;
	}

	/** Go to next page */
	async nextPage(): Promise<void> {
		if (this.hasNextPage) {
			await this.loadPage(this.currentPage + 1);
		}
	}

	/** Go to previous page */
	async previousPage(): Promise<void> {
		if (this.hasPreviousPage) {
			await this.loadPage(this.currentPage - 1);
		}
	}

	/** Load specific page */
	abstract loadPage(page: number): Promise<void>;
}

/** Store for managing single entities with CRUD operations */
abstract class EntityStore<T extends { id: number }, TCreate, TUpdate = Partial<TCreate>> extends BaseAsyncStore<T> {
	protected entityId = $state<number | null>(null);

	get id() { return this.entityId; }

	/** Load entity by ID */
	async load(id: number): Promise<void> {
		this.entityId = id;
		await this.refresh();
	}

	/** Create new entity */
	abstract create(data: TCreate): Promise<T | null>;

	/** Update current entity */
	abstract update(data: TUpdate): Promise<T | null>;

	/** Delete current entity */
	abstract delete(): Promise<boolean>;

	/** Check if entity is loaded */
	get isLoaded(): boolean {
		return this.entityId !== null && this.hasData;
	}
}

// =============================================================================
// FORM STATE MANAGEMENT
// =============================================================================

/** Generic form state with validation */
class FormStore<T extends Record<string, any>> {
	private initialData: T;
	private state = $state<{
		data: T;
		errors: Partial<Record<keyof T, string>>;
		isSubmitting: boolean;
		isDirty: boolean;
		isValid: boolean;
	}>({
		data: {} as T,
		errors: {},
		isSubmitting: false,
		isDirty: false,
		isValid: false
	});

	constructor(initialData: T) {
		this.initialData = { ...initialData };
		this.state.data = { ...initialData };
	}

	// Reactive getters
	get data() { return this.state.data; }
	get errors() { return this.state.errors; }
	get isSubmitting() { return this.state.isSubmitting; }
	get isDirty() { return this.state.isDirty; }
	get isValid() { return this.state.isValid; }

	/** Update field value */
	setField<K extends keyof T>(field: K, value: T[K]): void {
		this.state.data[field] = value;
		this.state.isDirty = this.checkDirty();
		
		// Clear field error
		if (this.state.errors[field]) {
			delete this.state.errors[field];
			this.state.errors = { ...this.state.errors };
		}
		
		this.validateField(field);
	}

	/** Set field error */
	setFieldError<K extends keyof T>(field: K, error: string): void {
		this.state.errors[field] = error;
		this.updateValidation();
	}

	/** Clear field error */
	clearFieldError<K extends keyof T>(field: K): void {
		delete this.state.errors[field];
		this.state.errors = { ...this.state.errors };
		this.updateValidation();
	}

	/** Set multiple errors */
	setErrors(errors: Partial<Record<keyof T, string>>): void {
		this.state.errors = errors;
		this.updateValidation();
	}

	/** Clear all errors */
	clearErrors(): void {
		this.state.errors = {};
		this.updateValidation();
	}

	/** Reset form to initial state */
	reset(): void {
		this.state.data = { ...this.initialData };
		this.state.errors = {};
		this.state.isSubmitting = false;
		this.state.isDirty = false;
		this.state.isValid = false;
	}

	/** Set submitting state */
	setSubmitting(submitting: boolean): void {
		this.state.isSubmitting = submitting;
	}

	/** Check if form data is different from initial */
	private checkDirty(): boolean {
		return JSON.stringify(this.state.data) !== JSON.stringify(this.initialData);
	}

	/** Update overall validation state */
	private updateValidation(): void {
		this.state.isValid = Object.keys(this.state.errors).length === 0;
	}

	/** Validate individual field (override in subclasses) */
	protected validateField<K extends keyof T>(field: K): void {
		// Override in subclasses for custom validation
	}

	/** Validate entire form (override in subclasses) */
	validate(): boolean {
		// Override in subclasses for custom validation
		return this.isValid;
	}
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
	BaseAsyncStore,
	CollectionStore,
	EntityStore,
	FormStore,
	type AsyncState,
	type StoreConfig,
	debounce,
	isStale
};