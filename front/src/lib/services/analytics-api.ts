// =============================================================================
// ENHANCED ANALYTICS API SERVICE - Premium Business Intelligence
// =============================================================================
// Connects to Django's comprehensive analytics system with Plotly visualizations

import type { ApiResponse } from '$lib/types/index.js';
import { api } from './api-client.js';

// Enhanced Analytics Types
export interface AnalyticsData {
	// Time period
	period: string;
	date_range: {
		start: string;
		end: string;
	};
	
	// Revenue analysis
	revenue_trend: Array<{
		period: string;
		value: number;
		date: string;
		growth_rate?: number;
	}>;
	revenue_by_service: Array<{
		service_name: string;
		service_name_ar: string;
		revenue: number;
		bookings: number;
		growth_rate: number;
	}>;
	revenue_growth: {
		current_period: number;
		previous_period: number;
		growth_rate: number;
		growth_amount: number;
	};
	
	// Booking analysis
	booking_trends: Array<{
		period: string;
		bookings: number;
		date: string;
		completion_rate: number;
	}>;
	booking_patterns: {
		by_hour: Array<{ hour: number; bookings: number; revenue: number }>;
		by_day: Array<{ day: string; bookings: number; revenue: number }>;
		by_method: Array<{ method: string; count: number; percentage: number }>;
	};
	peak_hours: Array<{
		hour: string;
		bookings: number;
		revenue: number;
		utilization_rate: number;
	}>;
	
	// Customer insights
	customer_segments: {
		new: { count: number; revenue: number; percentage: number };
		regular: { count: number; revenue: number; percentage: number };
		vip: { count: number; revenue: number; percentage: number };
		inactive: { count: number; revenue: number; percentage: number };
	};
	customer_lifetime_value: number;
	customer_acquisition_cost: number;
	customer_retention_rate: number;
	
	// Service performance
	service_performance: Array<{
		id: number;
		name: string;
		name_ar: string;
		bookings: number;
		revenue: number;
		rating: number;
		profit_margin: number;
		growth_rate: number;
	}>;
	service_ratings: {
		[key: string]: {
			average: number;
			count: number;
			distribution: Array<{ rating: number; count: number }>;
		};
	};
	
	// Operational metrics
	cancellation_rate: number;
	no_show_rate: number;
	completion_rate: number;
	average_booking_value: number;
	staff_utilization_rate: number;
	
	// Premium visualizations (HTML strings)
	revenue_chart?: string;
	booking_heatmap?: string;
	customer_segment_chart?: string;
	service_performance_chart?: string;
}

export interface RealtimeMetrics {
	current_revenue: number;
	current_bookings: number;
	active_customers: number;
	pending_bookings: number;
	completion_rate: number;
	average_rating: number;
	notifications: Array<{
		id: number;
		title: string;
		message: string;
		type: string;
		created_at: string;
	}>;
	last_updated: string;
}

export interface BusinessHealthMetrics {
	health_score: number;
	factors: Array<{
		name: string;
		score: number;
		weight: number;
		status: 'excellent' | 'good' | 'needs_improvement';
	}>;
	recommendations: Array<{
		title: string;
		description: string;
		priority: 'high' | 'medium' | 'low';
		impact: number;
		category: 'revenue' | 'customers' | 'operations' | 'quality';
	}>;
}

export interface PredictiveAnalytics {
	predicted_revenue: number;
	predicted_bookings: number;
	revenue_growth_prediction: number;
	booking_growth_prediction: number;
	customer_churn_prediction: number;
	seasonal_trends: Array<{
		period: string;
		predicted_bookings: number;
		predicted_revenue: number;
		confidence: number;
	}>;
	recommendations: Array<{
		title: string;
		description: string;
		impact: number;
		confidence: number;
	}>;
}

export interface CustomerSegmentData {
	name: string;
	name_ar: string;
	count: number;
	percentage: number;
	avg_spend: number;
	loyalty_score: number;
	retention_rate: number;
	growth_rate: number;
}

// Enhanced Analytics Service Class
export class AnalyticsService {
	constructor(private baseUrl: string = '/base') {}

	/**
	 * Get comprehensive business analytics with optional chart generation
	 */
	async getAnalytics(
		period: 'today' | 'week' | 'month' | 'quarter' | 'year' = 'month',
		options: {
			includeCharts?: boolean;
			includeHeatmap?: boolean;
			includeSegments?: boolean;
		} = {}
	): Promise<ApiResponse<AnalyticsData>> {
		const query = new URLSearchParams({
			period,
			charts: options.includeCharts ? 'true' : 'false',
			heatmap: options.includeHeatmap ? 'true' : 'false',
			segments: options.includeSegments ? 'true' : 'false'
		});

		return api.business.http.request<AnalyticsData>(`${this.baseUrl}/analytics/?${query}`);
	}

	/**
	 * Get real-time business metrics for live dashboard updates
	 */
	async getRealtimeMetrics(): Promise<ApiResponse<RealtimeMetrics>> {
		return api.business.http.request<RealtimeMetrics>(`${this.baseUrl}/realtime-metrics/`);
	}

	/**
	 * Get business health assessment with actionable recommendations
	 */
	async getBusinessHealth(): Promise<ApiResponse<BusinessHealthMetrics>> {
		return api.business.http.request<BusinessHealthMetrics>(`${this.baseUrl}/business-health/`);
	}

	/**
	 * Get predictive analytics and forecasting
	 */
	async getPredictiveAnalytics(
		horizon: 'week' | 'month' | 'quarter' = 'month'
	): Promise<ApiResponse<PredictiveAnalytics>> {
		const query = new URLSearchParams({ horizon });
		return api.business.http.request<PredictiveAnalytics>(`${this.baseUrl}/predictive-analytics/?${query}`);
	}

	/**
	 * Get detailed customer segmentation analysis
	 */
	async getCustomerSegments(): Promise<ApiResponse<CustomerSegmentData[]>> {
		return api.business.http.request<CustomerSegmentData[]>(`${this.baseUrl}/customer-segments/`);
	}

	/**
	 * Export analytics data in various formats
	 */
	async exportAnalytics(
		format: 'excel' | 'pdf' | 'csv',
		period: string = 'month',
		options: {
			includeCharts?: boolean;
			includeRawData?: boolean;
		} = {}
	): Promise<ApiResponse<Blob>> {
		const query = new URLSearchParams({
			format,
			period,
			charts: options.includeCharts ? 'true' : 'false',
			raw_data: options.includeRawData ? 'true' : 'false'
		});

		const response = await fetch(`${api.business.http.config.baseURL}${this.baseUrl}/export-analytics/?${query}`, {
			headers: {
				'Authorization': `Bearer ${api.getAccessToken()}`
			}
		});

		if (!response.ok) {
			return {
				success: false,
				error: 'Export failed',
				code: 'EXPORT_ERROR'
			};
		}

		const blob = await response.blob();
		return {
			success: true,
			data: blob
		};
	}

	/**
	 * Get activity heatmap data for GitHub-style visualization
	 */
	async getActivityHeatmap(
		year?: number
	): Promise<ApiResponse<{
		year: number;
		data: Array<{
			date: string;
			bookings: number;
			revenue: number;
			intensity: number; // 0-4 scale for color intensity
		}>;
		stats: {
			total_bookings: number;
			total_revenue: number;
			avg_daily_bookings: number;
			peak_day: { date: string; bookings: number };
		};
	}>> {
		const query = year ? `?year=${year}` : '';
		return api.business.http.request(`${this.baseUrl}/activity-heatmap/${query}`);
	}

	/**
	 * Get service performance comparison data
	 */
	async getServicePerformance(
		period: string = 'month'
	): Promise<ApiResponse<{
		services: Array<{
			id: number;
			name: string;
			name_ar: string;
			bookings: number;
			revenue: number;
			rating: number;
			profit_margin: number;
			efficiency_score: number;
			trend: 'up' | 'down' | 'stable';
		}>;
		summary: {
			top_performer: string;
			most_profitable: string;
			highest_rated: string;
			fastest_growing: string;
		};
	}>> {
		const query = new URLSearchParams({ period });
		return api.business.http.request(`${this.baseUrl}/service-performance/?${query}`);
	}
}

// Create and export singleton instance
export const analyticsService = new AnalyticsService();

// Export types for use in components
export type {
	AnalyticsData,
	RealtimeMetrics,
	BusinessHealthMetrics,
	PredictiveAnalytics,
	CustomerSegmentData
};