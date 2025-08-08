// =============================================================================
// PLOTLY CHART SERVICE - Saudi Market Premium Visualizations
// =============================================================================
// Factory service for creating interactive charts with Arabic localization

import type { PlotData, Layout, Config } from 'plotly.js-dist-min';
import type { AnalyticsData } from './analytics-api.js';

// Plotly.js dynamic import for better performance
let Plotly: any = null;

async function loadPlotly() {
	if (!Plotly) {
		const plotlyModule = await import('plotly.js-dist-min');
		Plotly = plotlyModule.default;
	}
	return Plotly;
}

// Saudi Market Color Schemes
export const SaudiColorSchemes = {
	primary: ['#2563eb', '#0ea5e9', '#06b6d4', '#10b981', '#84cc16'],
	success: ['#10b981', '#059669', '#047857', '#065f46', '#064e3b'],
	revenue: ['#059669', '#10b981', '#34d399', '#6ee7b7', '#9df9d0'],
	services: ['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe'],
	customers: ['#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7'],
	heatmap: ['#f3f4f6', '#d1fae5', '#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#047857']
};

// Base chart configuration for Saudi market
const baseSaudiConfig: Partial<Config> = {
	displayModeBar: true,
	displaylogo: false,
	modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
	locale: 'ar',
	responsive: true,
	toImageButtonOptions: {
		format: 'png',
		filename: 'wagtee_chart',
		height: 600,
		width: 1000,
		scale: 2
	}
};

// Base layout for Saudi market with RTL support
const baseSaudiLayout: Partial<Layout> = {
	font: {
		family: 'Inter, system-ui, sans-serif',
		size: 12,
		color: '#374151'
	},
	paper_bgcolor: 'rgba(255,255,255,0.8)',
	plot_bgcolor: 'rgba(255,255,255,0.5)',
	margin: { l: 60, r: 40, t: 80, b: 60 },
	showlegend: true,
	legend: {
		orientation: 'h',
		yanchor: 'bottom',
		y: -0.3,
		xanchor: 'center',
		x: 0.5,
		font: { size: 10 }
	},
	hovermode: 'closest',
	hoverlabel: {
		bgcolor: 'rgba(255,255,255,0.9)',
		bordercolor: '#e5e7eb',
		font: { color: '#374151' }
	}
};

// Saudi currency formatter
export function formatSAR(amount: number): string {
	return new Intl.NumberFormat('ar-SA', {
		style: 'currency',
		currency: 'SAR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 2
	}).format(amount);
}

// Arabic number formatter
export function formatArabicNumber(num: number): string {
	return new Intl.NumberFormat('ar-SA', {
		maximumFractionDigits: 1
	}).format(num);
}

// Date formatter for Arabic
export function formatArabicDate(dateString: string): string {
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('ar-SA', {
		weekday: 'short',
		month: 'short',
		day: 'numeric',
		timeZone: 'Asia/Riyadh'
	}).format(date);
}

export class PlotlyChartService {
	private plotly: any = null;

	async init() {
		if (!this.plotly) {
			this.plotly = await loadPlotly();
		}
		return this.plotly;
	}

	/**
	 * Create revenue trend chart with Saudi formatting
	 */
	async createRevenueChart(
		container: HTMLElement,
		data: AnalyticsData,
		options: {
			showGrowth?: boolean;
			period?: string;
			height?: number;
		} = {}
	): Promise<void> {
		await this.init();
		
		const { showGrowth = true, period = 'month', height = 400 } = options;
		
		const revenueTrace: Partial<PlotData> = {
			x: data.revenue_trend.map(item => formatArabicDate(item.date)),
			y: data.revenue_trend.map(item => item.value),
			type: 'scatter',
			mode: 'lines+markers',
			name: 'الإيرادات',
			line: {
				color: '#10b981',
				width: 3,
				shape: 'spline'
			},
			marker: {
				color: '#059669',
				size: 8,
				line: { color: 'white', width: 2 }
			},
			fill: 'tonexty',
			fillcolor: 'rgba(16, 185, 129, 0.1)',
			hovertemplate: '<b>%{x}</b><br>الإيرادات: %{y:,.0f} ر.س<extra></extra>',
			customdata: data.revenue_trend.map(item => formatSAR(item.value))
		};

		const traces: Partial<PlotData>[] = [revenueTrace];

		// Add growth rate trace if requested
		if (showGrowth && data.revenue_trend.some(item => item.growth_rate !== undefined)) {
			const growthTrace: Partial<PlotData> = {
				x: data.revenue_trend.map(item => formatArabicDate(item.date)),
				y: data.revenue_trend.map(item => item.growth_rate || 0),
				type: 'scatter',
				mode: 'lines',
				name: 'معدل النمو %',
				yaxis: 'y2',
				line: {
					color: '#f59e0b',
					width: 2,
					dash: 'dash'
				},
				hovertemplate: '<b>%{x}</b><br>النمو: %{y:.1f}%<extra></extra>'
			};
			traces.push(growthTrace);
		}

		const layout: Partial<Layout> = {
			...baseSaudiLayout,
			title: {
				text: `اتجاه الإيرادات - ${this.getPeriodLabel(period)}`,
				font: { size: 18, color: '#1f2937' },
				x: 0.5,
				xanchor: 'center'
			},
			xaxis: {
				title: 'الفترة الزمنية',
				showgrid: true,
				gridcolor: 'rgba(0,0,0,0.05)',
				zeroline: false
			},
			yaxis: {
				title: 'الإيرادات (ر.س)',
				tickformat: ',.0f',
				showgrid: true,
				gridcolor: 'rgba(0,0,0,0.05)',
				zeroline: false
			},
			height: height
		};

		// Add secondary y-axis for growth rate
		if (showGrowth) {
			layout.yaxis2 = {
				title: 'معدل النمو (%)',
				overlaying: 'y',
				side: 'right',
				tickformat: '.1f',
				showgrid: false
			};
		}

		await this.plotly.newPlot(container, traces, layout, baseSaudiConfig);
	}

	/**
	 * Create GitHub-style activity heatmap for booking patterns
	 */
	async createActivityHeatmap(
		container: HTMLElement,
		data: Array<{ date: string; bookings: number; intensity: number }>,
		options: {
			year?: number;
			height?: number;
		} = {}
	): Promise<void> {
		await this.init();
		
		const { year = new Date().getFullYear(), height = 200 } = options;
		
		// Organize data into weekly grid (Saudi week starts on Saturday)
		const weeks = this.organizeHeatmapData(data, year);
		
		const trace: Partial<PlotData> = {
			z: weeks.map(week => week.map(day => day?.intensity || 0)),
			x: ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
			y: weeks.map((_, index) => `الأسبوع ${index + 1}`),
			type: 'heatmap',
			colorscale: [
				[0, '#f3f4f6'],
				[0.2, '#d1fae5'],
				[0.4, '#a7f3d0'],
			[0.6, '#6ee7b7'],
				[0.8, '#34d399'],
				[1, '#10b981']
			],
			showscale: true,
			colorbar: {
				title: 'عدد الحجوزات',
				titleside: 'right'
			},
			hovertemplate: '<b>%{customdata}</b><br>الحجوزات: %{z}<extra></extra>',
			customdata: weeks.map(week => 
				week.map(day => day?.date ? formatArabicDate(day.date) : '')
			)
		};

		const layout: Partial<Layout> = {
			...baseSaudiLayout,
			title: {
				text: `نشاط الحجوزات - ${year}`,
				font: { size: 16, color: '#1f2937' },
				x: 0.5,
				xanchor: 'center'
			},
			xaxis: {
				title: '',
				side: 'top',
				showgrid: false,
				zeroline: false,
				fixedrange: true
			},
			yaxis: {
				title: '',
				showgrid: false,
				zeroline: false,
				autorange: 'reversed',
				fixedrange: true
			},
			height: height,
			margin: { l: 80, r: 80, t: 60, b: 40 }
		};

		await this.plotly.newPlot(container, [trace], layout, {
			...baseSaudiConfig,
			displayModeBar: false
		});
	}

	/**
	 * Create service performance horizontal bar chart
	 */
	async createServicePerformanceChart(
		container: HTMLElement,
		services: Array<{
			name: string;
			name_ar: string;
			revenue: number;
			bookings: number;
			rating: number;
		}>,
		options: {
			maxServices?: number;
			height?: number;
		} = {}
	): Promise<void> {
		await this.init();
		
		const { maxServices = 8, height = 500 } = options;
		const topServices = services.slice(0, maxServices);
		
		const revenueTrace: Partial<PlotData> = {
			y: topServices.map(s => s.name_ar || s.name),
			x: topServices.map(s => s.revenue),
			type: 'bar',
			orientation: 'h',
			name: 'الإيرادات',
			marker: {
				color: SaudiColorSchemes.revenue,
				line: { color: 'white', width: 1 }
			},
			hovertemplate: '<b>%{y}</b><br>الإيرادات: %{customdata}<br>الحجوزات: %{x2}<extra></extra>',
			customdata: topServices.map(s => formatSAR(s.revenue)),
			x2: topServices.map(s => s.bookings)
		};

		const layout: Partial<Layout> = {
			...baseSaudiLayout,
			title: {
				text: 'أداء الخدمات',
				font: { size: 18, color: '#1f2937' },
				x: 0.5,
				xanchor: 'center'
			},
			xaxis: {
				title: 'الإيرادات (ر.س)',
				tickformat: ',.0f',
				showgrid: true,
				gridcolor: 'rgba(0,0,0,0.05)'
			},
			yaxis: {
				title: '',
				automargin: true,
				categoryorder: 'total ascending'
			},
			height: height,
			margin: { l: 150, r: 50, t: 80, b: 60 }
		};

		await this.plotly.newPlot(container, [revenueTrace], layout, baseSaudiConfig);
	}

	/**
	 * Create customer segmentation donut chart
	 */
	async createCustomerSegmentChart(
		container: HTMLElement,
		segments: Array<{
			name: string;
			name_ar: string;
			count: number;
			percentage: number;
		}>,
		options: {
			height?: number;
		} = {}
	): Promise<void> {
		await this.init();
		
		const { height = 400 } = options;
		
		const trace: Partial<PlotData> = {
			values: segments.map(s => s.count),
			labels: segments.map(s => s.name_ar || s.name),
			type: 'pie',
			hole: 0.4,
			marker: {
				colors: SaudiColorSchemes.customers,
				line: { color: 'white', width: 2 }
			},
			textinfo: 'label+percent',
			textposition: 'outside',
			hovertemplate: '<b>%{label}</b><br>العدد: %{value}<br>النسبة: %{percent}<extra></extra>',
			sort: false
		};

		const layout: Partial<Layout> = {
			...baseSaudiLayout,
			title: {
				text: 'شرائح العملاء',
				font: { size: 18, color: '#1f2937' },
				x: 0.5,
				xanchor: 'center'
			},
			height: height,
			showlegend: true,
			legend: {
				orientation: 'v',
				yanchor: 'middle',
				y: 0.5,
				xanchor: 'left',
				x: 1.02
			}
		};

		await this.plotly.newPlot(container, [trace], layout, baseSaudiConfig);
	}

	/**
	 * Create booking pattern timeline chart
	 */
	async createBookingTimelineChart(
		container: HTMLElement,
		hourlyData: Array<{ hour: number; bookings: number; revenue: number }>,
		options: {
			height?: number;
		} = {}
	): Promise<void> {
		await this.init();
		
		const { height = 350 } = options;
		
		const trace: Partial<PlotData> = {
			x: hourlyData.map(h => `${h.hour}:00`),
			y: hourlyData.map(h => h.bookings),
			type: 'scatter',
			mode: 'lines+markers',
			fill: 'tozeroy',
			name: 'الحجوزات',
			line: {
				color: '#3b82f6',
				width: 3,
				shape: 'spline'
			},
			marker: {
				color: '#1e40af',
				size: 6
			},
			fillcolor: 'rgba(59, 130, 246, 0.1)',
			hovertemplate: '<b>الساعة %{x}</b><br>الحجوزات: %{y}<br>الإيرادات: %{customdata}<extra></extra>',
			customdata: hourlyData.map(h => formatSAR(h.revenue))
		};

		const layout: Partial<Layout> = {
			...baseSaudiLayout,
			title: {
				text: 'نمط الحجوزات اليومي',
				font: { size: 18, color: '#1f2937' },
				x: 0.5,
				xanchor: 'center'
			},
			xaxis: {
				title: 'الساعة',
				showgrid: true,
				gridcolor: 'rgba(0,0,0,0.05)',
				dtick: 2
			},
			yaxis: {
				title: 'عدد الحجوزات',
				showgrid: true,
				gridcolor: 'rgba(0,0,0,0.05)',
				zeroline: false
			},
			height: height
		};

		await this.plotly.newPlot(container, [trace], layout, baseSaudiConfig);
	}

	/**
	 * Update chart with new data
	 */
	async updateChart(container: HTMLElement, update: any): Promise<void> {
		await this.init();
		await this.plotly.redraw(container, update);
	}

	/**
	 * Resize chart to fit container
	 */
	async resizeChart(container: HTMLElement): Promise<void> {
		await this.init();
		await this.plotly.Plots.resize(container);
	}

	/**
	 * Helper method to get Arabic period label
	 */
	private getPeriodLabel(period: string): string {
		const labels: Record<string, string> = {
			today: 'اليوم',
			week: 'هذا الأسبوع',
			month: 'هذا الشهر',
			quarter: 'هذا الربع',
			year: 'هذا العام'
		};
		return labels[period] || period;
	}

	/**
	 * Organize heatmap data into weekly grid format
	 */
	private organizeHeatmapData(
		data: Array<{ date: string; bookings: number; intensity: number }>,
		year: number
	): Array<Array<{ date: string; bookings: number; intensity: number } | null>> {
		const weeks: Array<Array<{ date: string; bookings: number; intensity: number } | null>> = [];
		const startDate = new Date(year, 0, 1);
		
		// Find first Saturday of the year (Saudi week starts on Saturday)
		const firstSaturday = new Date(startDate);
		const dayOffset = (startDate.getDay() + 1) % 7; // Saturday = 0
		firstSaturday.setDate(startDate.getDate() + (6 - dayOffset));
		
		let currentWeek: Array<{ date: string; bookings: number; intensity: number } | null> = [];
		let currentDate = new Date(firstSaturday);
		
		while (currentDate.getFullYear() <= year) {
			const dateStr = currentDate.toISOString().split('T')[0];
			const dayData = data.find(d => d.date === dateStr);
			
			currentWeek.push(dayData || null);
			
			if (currentWeek.length === 7) {
				weeks.push([...currentWeek]);
				currentWeek = [];
			}
			
			currentDate.setDate(currentDate.getDate() + 1);
			
			// Stop if we've moved to next year
			if (currentDate.getFullYear() > year) break;
		}
		
		return weeks;
	}
}

// Export singleton instance
export const plotlyService = new PlotlyChartService();