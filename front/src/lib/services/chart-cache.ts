// =============================================================================
// CHART CACHE SERVICE - Performance Optimization for Analytics
// =============================================================================
// Intelligent caching system for chart data and configurations

interface CacheEntry<T> {
	data: T;
	timestamp: number;
	hits: number;
	size: number;
}

interface CacheOptions {
	maxAge?: number; // milliseconds
	maxSize?: number; // number of entries
	maxMemory?: number; // bytes
}

export class ChartCacheService {
	private cache = new Map<string, CacheEntry<any>>();
	private readonly defaultMaxAge = 5 * 60 * 1000; // 5 minutes
	private readonly defaultMaxSize = 100; // entries
	private readonly defaultMaxMemory = 50 * 1024 * 1024; // 50MB

	private options: Required<CacheOptions>;

	constructor(options: CacheOptions = {}) {
		this.options = {
			maxAge: options.maxAge || this.defaultMaxAge,
			maxSize: options.maxSize || this.defaultMaxSize,
			maxMemory: options.maxMemory || this.defaultMaxMemory
		};

		// Set up periodic cleanup
		this.startCleanupTimer();
	}

	/**
	 * Generate cache key from parameters
	 */
	private generateKey(prefix: string, params: Record<string, any>): string {
		const sortedParams = Object.keys(params)
			.sort()
			.map(key => `${key}=${JSON.stringify(params[key])}`)
			.join('&');
		return `${prefix}:${sortedParams}`;
	}

	/**
	 * Calculate approximate size of data in bytes
	 */
	private calculateSize(data: any): number {
		return new Blob([JSON.stringify(data)]).size;
	}

	/**
	 * Check if cache entry is still valid
	 */
	private isValid(entry: CacheEntry<any>): boolean {
		return Date.now() - entry.timestamp < this.options.maxAge;
	}

	/**
	 * Get total memory usage of cache
	 */
	private getTotalMemoryUsage(): number {
		return Array.from(this.cache.values()).reduce((total, entry) => total + entry.size, 0);
	}

	/**
	 * Clean up expired entries and enforce memory limits
	 */
	private cleanup(): void {
		// Remove expired entries
		for (const [key, entry] of this.cache) {
			if (!this.isValid(entry)) {
				this.cache.delete(key);
			}
		}

		// Enforce size limit
		if (this.cache.size > this.options.maxSize) {
			const entries = Array.from(this.cache.entries())
				.sort((a, b) => {
					// Sort by hit count (ascending) then by age (oldest first)
					const hitDiff = a[1].hits - b[1].hits;
					if (hitDiff !== 0) return hitDiff;
					return a[1].timestamp - b[1].timestamp;
				});

			// Remove least used and oldest entries
			const toRemove = entries.slice(0, this.cache.size - this.options.maxSize);
			toRemove.forEach(([key]) => this.cache.delete(key));
		}

		// Enforce memory limit
		while (this.getTotalMemoryUsage() > this.options.maxMemory && this.cache.size > 0) {
			const entries = Array.from(this.cache.entries())
				.sort((a, b) => {
					// Sort by size (largest first) then by hit count (ascending)
					const sizeDiff = b[1].size - a[1].size;
					if (sizeDiff !== 0) return sizeDiff;
					return a[1].hits - b[1].hits;
				});

			// Remove largest and least used entries
			const [keyToRemove] = entries[0];
			this.cache.delete(keyToRemove);
		}
	}

	/**
	 * Start periodic cleanup timer
	 */
	private startCleanupTimer(): void {
		setInterval(() => {
			this.cleanup();
		}, this.options.maxAge / 2); // Clean up twice per maxAge period
	}

	/**
	 * Store data in cache
	 */
	set<T>(key: string, data: T): void {
		const size = this.calculateSize(data);
		const entry: CacheEntry<T> = {
			data,
			timestamp: Date.now(),
			hits: 0,
			size
		};

		this.cache.set(key, entry);
		
		// Immediate cleanup if we exceed limits
		if (this.cache.size > this.options.maxSize || 
			this.getTotalMemoryUsage() > this.options.maxMemory) {
			this.cleanup();
		}
	}

	/**
	 * Retrieve data from cache
	 */
	get<T>(key: string): T | null {
		const entry = this.cache.get(key);
		
		if (!entry || !this.isValid(entry)) {
			if (entry) {
				this.cache.delete(key);
			}
			return null;
		}

		// Update hit count
		entry.hits++;
		
		return entry.data as T;
	}

	/**
	 * Check if key exists and is valid
	 */
	has(key: string): boolean {
		const entry = this.cache.get(key);
		return entry ? this.isValid(entry) : false;
	}

	/**
	 * Remove specific entry
	 */
	delete(key: string): boolean {
		return this.cache.delete(key);
	}

	/**
	 * Clear all cache entries
	 */
	clear(): void {
		this.cache.clear();
	}

	/**
	 * Get cache statistics
	 */
	getStats(): {
		size: number;
		memoryUsage: number;
		hitRate: number;
		entries: Array<{
			key: string;
			age: number;
			hits: number;
			size: number;
		}>;
	} {
		const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
			key,
			age: Date.now() - entry.timestamp,
			hits: entry.hits,
			size: entry.size
		}));

		const totalHits = entries.reduce((sum, entry) => sum + entry.hits, 0);
		const hitRate = totalHits > 0 ? totalHits / (totalHits + entries.length) : 0;

		return {
			size: this.cache.size,
			memoryUsage: this.getTotalMemoryUsage(),
			hitRate,
			entries
		};
	}

	/**
	 * Cache analytics data with specialized key generation
	 */
	cacheAnalytics<T>(
		type: 'revenue' | 'bookings' | 'customers' | 'services' | 'heatmap',
		period: string,
		filters: Record<string, any>,
		data: T
	): void {
		const key = this.generateKey(`analytics:${type}`, { period, ...filters });
		this.set(key, data);
	}

	/**
	 * Retrieve cached analytics data
	 */
	getAnalytics<T>(
		type: 'revenue' | 'bookings' | 'customers' | 'services' | 'heatmap',
		period: string,
		filters: Record<string, any>
	): T | null {
		const key = this.generateKey(`analytics:${type}`, { period, ...filters });
		return this.get<T>(key);
	}

	/**
	 * Cache chart configuration
	 */
	cacheChartConfig(
		chartType: string,
		params: Record<string, any>,
		config: any
	): void {
		const key = this.generateKey(`config:${chartType}`, params);
		this.set(key, config);
	}

	/**
	 * Retrieve cached chart configuration
	 */
	getChartConfig(
		chartType: string,
		params: Record<string, any>
	): any | null {
		const key = this.generateKey(`config:${chartType}`, params);
		return this.get(key);
	}

	/**
	 * Invalidate cache entries by pattern
	 */
	invalidatePattern(pattern: RegExp): number {
		let deletedCount = 0;
		for (const key of this.cache.keys()) {
			if (pattern.test(key)) {
				this.cache.delete(key);
				deletedCount++;
			}
		}
		return deletedCount;
	}

	/**
	 * Invalidate all analytics cache
	 */
	invalidateAnalytics(): number {
		return this.invalidatePattern(/^analytics:/);
	}

	/**
	 * Invalidate cache for specific period
	 */
	invalidatePeriod(period: string): number {
		return this.invalidatePattern(new RegExp(`period.*${period}`));
	}

	/**
	 * Pre-warm cache with commonly requested data
	 */
	async preWarmCache(
		dataLoader: (type: string, period: string) => Promise<any>
	): Promise<void> {
		const commonQueries = [
			{ type: 'revenue', period: 'month' },
			{ type: 'bookings', period: 'month' },
			{ type: 'customers', period: 'month' },
			{ type: 'revenue', period: 'week' },
			{ type: 'bookings', period: 'week' }
		];

		const promises = commonQueries.map(async ({ type, period }) => {
			try {
				const data = await dataLoader(type, period);
				this.cacheAnalytics(type as any, period, {}, data);
			} catch (error) {
				console.warn(`Failed to pre-warm cache for ${type}:${period}`, error);
			}
		});

		await Promise.allSettled(promises);
	}
}

// Export singleton instance
export const chartCache = new ChartCacheService({
	maxAge: 5 * 60 * 1000, // 5 minutes
	maxSize: 150, // entries
	maxMemory: 75 * 1024 * 1024 // 75MB
});