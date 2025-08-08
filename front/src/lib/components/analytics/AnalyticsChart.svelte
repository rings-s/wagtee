<!-- 
  Base Analytics Chart Component - Svelte 5 Runes
  Reusable Plotly wrapper with caching and error handling
-->
<script lang="ts">
import { onMount, onDestroy } from 'svelte';
import { browser } from '$app/environment';
import { plotlyService } from '$lib/services/plotly-service.js';
import { chartCache } from '$lib/services/chart-cache.js';
import { Loader2, RefreshCw, Download, Maximize2, AlertTriangle } from '@lucide/svelte';
import { Button } from '$lib/components/ui/button';
import * as Card from '$lib/components/ui/card';

// Props using Svelte 5 $props rune
interface Props {
	chartType: 'revenue' | 'heatmap' | 'services' | 'segments' | 'timeline';
	data: any;
	title?: string;
	subtitle?: string;
	height?: number;
	options?: Record<string, any>;
	cacheKey?: string;
	autoRefresh?: boolean;
	refreshInterval?: number;
	showControls?: boolean;
	showFullscreen?: boolean;
	containerClass?: string;
}

const {
	chartType,
	data,
	title,
	subtitle,
	height = 400,
	options = {},
	cacheKey,
	autoRefresh = false,
	refreshInterval = 30000,
	showControls = true,
	showFullscreen = true,
	containerClass = '',
	...props
}: Props = $props();

// Svelte 5 runes for reactive state
let chartContainer = $state<HTMLElement>();
let isLoading = $state<boolean>(true);
let error = $state<string | null>(null);
let isInitialized = $state<boolean>(false);
let isFullscreen = $state<boolean>(false);
let lastRefresh = $state<Date>(new Date());
let refreshTimer: NodeJS.Timeout | null = null;

// Derived reactive values
const chartId = $derived(() => `chart-${chartType}-${Math.random().toString(36).substr(2, 9)}`);
const hasData = $derived(() => data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0));
const cacheEnabled = $derived(() => !!cacheKey);

// Chart rendering function
async function renderChart() {
	if (!chartContainer || !hasData) return;
	
	try {
		isLoading = true;
		error = null;
		
		// Check cache first
		if (cacheEnabled) {
			const cachedConfig = chartCache.getChartConfig(chartType, { data, options });
			if (cachedConfig && isInitialized) {
				await plotlyService.updateChart(chartContainer, cachedConfig);
				isLoading = false;
				return;
			}
		}
		
		// Render appropriate chart type
		switch (chartType) {
			case 'revenue':
				await plotlyService.createRevenueChart(chartContainer, data, {
					height,
					...options
				});
				break;
			
			case 'heatmap':
				await plotlyService.createActivityHeatmap(chartContainer, data, {
					height,
					...options
				});
				break;
			
			case 'services':
				await plotlyService.createServicePerformanceChart(chartContainer, data, {
					height,
					...options
				});
				break;
			
			case 'segments':
				await plotlyService.createCustomerSegmentChart(chartContainer, data, {
					height,
					...options
				});
				break;
			
			case 'timeline':
				await plotlyService.createBookingTimelineChart(chartContainer, data, {
					height,
					...options
				});
				break;
			
			default:
				throw new Error(`Unknown chart type: ${chartType}`);
		}
		
		// Cache the configuration for future use
		if (cacheEnabled) {
			chartCache.cacheChartConfig(chartType, { data, options }, data);
		}
		
		isInitialized = true;
		lastRefresh = new Date();
		
	} catch (err) {
		console.error('Chart rendering error:', err);
		error = err instanceof Error ? err.message : 'حدث خطأ في عرض المخطط';
	} finally {
		isLoading = false;
	}
}

// Refresh chart data
async function refreshChart() {
	if (!isInitialized) return;
	await renderChart();
}

// Export chart as image
async function exportChart(format: 'png' | 'pdf' = 'png') {
	if (!chartContainer) return;
	
	try {
		// Create download link using Plotly's toImage
		const plotly = await plotlyService.init();
		const imgData = await plotly.toImage(chartContainer, {
			format,
			width: 1200,
			height: 800,
			scale: 2
		});
		
		const link = document.createElement('a');
		link.download = `wagtee-${chartType}-${new Date().toISOString().split('T')[0]}.${format}`;
		link.href = imgData;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		
	} catch (err) {
		console.error('Export failed:', err);
	}
}

// Toggle fullscreen mode
function toggleFullscreen() {
	isFullscreen = !isFullscreen;
	
	// Use requestAnimationFrame to ensure DOM update before resize
	requestAnimationFrame(async () => {
		if (chartContainer) {
			await plotlyService.resizeChart(chartContainer);
		}
	});
}

// Handle resize events
function handleResize() {
	if (chartContainer && isInitialized) {
		plotlyService.resizeChart(chartContainer);
	}
}

// Setup auto-refresh
function setupAutoRefresh() {
	if (autoRefresh && refreshInterval > 0) {
		refreshTimer = setInterval(refreshChart, refreshInterval);
	}
}

function clearAutoRefresh() {
	if (refreshTimer) {
		clearInterval(refreshTimer);
		refreshTimer = null;
	}
}

// Lifecycle management
onMount(async () => {
	if (browser && hasData) {
		await renderChart();
		setupAutoRefresh();
		
		// Setup resize listener
		window.addEventListener('resize', handleResize);
	}
});

onDestroy(() => {
	clearAutoRefresh();
	if (browser) {
		window.removeEventListener('resize', handleResize);
	}
});

// Reactively re-render when data changes
$effect(() => {
	if (browser && hasData && chartContainer) {
		renderChart();
	}
});

// Reactive auto-refresh setup
$effect(() => {
	clearAutoRefresh();
	setupAutoRefresh();
});
</script>

<!-- Chart Component Template -->
<div 
	class="analytics-chart-container {containerClass}"
	class:fullscreen={isFullscreen}
>
	<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl">
		{#if title || showControls}
			<Card.Header class="pb-4">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						{#if title}
							<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200">
								{title}
							</Card.Title>
						{/if}
						{#if subtitle}
							<Card.Description class="text-slate-600 dark:text-slate-400">
								{subtitle}
							</Card.Description>
						{/if}
					</div>
					
					{#if showControls}
						<div class="flex items-center gap-2">
							<!-- Refresh Button -->
							<Button 
								variant="ghost" 
								size="sm" 
								onclick={refreshChart}
								disabled={isLoading}
								class="glass-button"
								title="تحديث المخطط"
							>
								<RefreshCw class="h-4 w-4 {isLoading ? 'animate-spin' : ''}" />
							</Button>
							
							<!-- Export Button -->
							<Button 
								variant="ghost" 
								size="sm" 
								onclick={() => exportChart('png')}
								disabled={isLoading || !isInitialized}
								class="glass-button"
								title="تصدير كصورة"
							>
								<Download class="h-4 w-4" />
							</Button>
							
							<!-- Fullscreen Button -->
							{#if showFullscreen}
								<Button 
									variant="ghost" 
									size="sm" 
									onclick={toggleFullscreen}
									disabled={isLoading}
									class="glass-button"
									title="ملء الشاشة"
								>
									<Maximize2 class="h-4 w-4" />
								</Button>
							{/if}
						</div>
					{/if}
				</div>
			</Card.Header>
		{/if}
		
		<Card.Content class="space-y-4">
			<!-- Chart Container -->
			<div class="relative">
				{#if isLoading}
					<!-- Loading State -->
					<div 
						class="flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
						style="height: {height}px"
					>
						<div class="text-center space-y-4">
							<div class="relative">
								<Loader2 class="h-8 w-8 animate-spin text-blue-500 mx-auto" />
								<div class="absolute inset-0 h-8 w-8 rounded-full bg-blue-500/20 blur-xl animate-pulse mx-auto"></div>
							</div>
							<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
								جار تحميل المخطط...
							</p>
						</div>
					</div>
				{:else if error}
					<!-- Error State -->
					<div 
						class="flex items-center justify-center bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950/30 dark:to-red-900/30 border border-red-200 dark:border-red-800 rounded-lg"
						style="height: {height}px"
					>
						<div class="text-center space-y-4">
							<div class="relative">
								<AlertTriangle class="h-8 w-8 text-red-500 mx-auto" />
								<div class="absolute inset-0 h-8 w-8 rounded-full bg-red-500/20 blur-xl mx-auto"></div>
							</div>
							<div class="space-y-2">
								<p class="text-sm font-semibold text-red-800 dark:text-red-200">
									خطأ في تحميل المخطط
								</p>
								<p class="text-xs text-red-600 dark:text-red-400">
									{error}
								</p>
							</div>
							<Button 
								variant="outline" 
								size="sm" 
								onclick={refreshChart}
								class="border-red-300 text-red-700 hover:bg-red-50 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-950/30"
							>
								<RefreshCw class="h-4 w-4 ml-1" />
								إعادة المحاولة
							</Button>
						</div>
					</div>
				{:else if !hasData}
					<!-- No Data State -->
					<div 
						class="flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg"
						style="height: {height}px"
					>
						<div class="text-center space-y-3">
							<div class="h-12 w-12 mx-auto rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
								<svg class="h-6 w-6 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
								</svg>
							</div>
							<div class="space-y-1">
								<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
									لا توجد بيانات متاحة
								</p>
								<p class="text-xs text-slate-500 dark:text-slate-500">
									قم بإنشاء بعض الحجوزات لرؤية التحليلات
								</p>
							</div>
						</div>
					</div>
				{:else}
					<!-- Chart Container -->
					<div 
						bind:this={chartContainer}
						id={chartId}
						class="chart-container rounded-lg overflow-hidden"
					></div>
				{/if}
			</div>
			
			<!-- Chart Footer Info -->
			{#if isInitialized && !error}
				<div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200/50 dark:border-slate-700/50 pt-3">
					<div class="flex items-center gap-2">
						<div class="h-2 w-2 rounded-full bg-emerald-500"></div>
						<span>آخر تحديث: {lastRefresh.toLocaleString('ar-SA')}</span>
					</div>
					
					{#if autoRefresh}
						<div class="flex items-center gap-1">
							<div class="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
							<span>تحديث تلقائي كل {Math.round(refreshInterval / 1000)} ثانية</span>
						</div>
					{/if}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>

<style>
	.analytics-chart-container {
		transition: all 0.3s ease;
	}
	
	.analytics-chart-container.fullscreen {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 50;
		background: rgba(0, 0, 0, 0.9);
		backdrop-filter: blur(8px);
		padding: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.analytics-chart-container.fullscreen :global(.glass-card) {
		width: 100%;
		height: 100%;
		max-width: none;
		max-height: none;
	}
	
	.chart-container {
		min-height: 200px;
	}
	
	/* Custom Plotly styling */
	:global(.js-plotly-plot .plotly) {
		border-radius: 0.5rem;
	}
	
	:global(.modebar) {
		background: rgba(255, 255, 255, 0.9) !important;
		border-radius: 0.5rem !important;
		border: 1px solid rgba(0, 0, 0, 0.1) !important;
	}
	
	:global(.modebar-btn) {
		color: #6b7280 !important;
	}
	
	:global(.modebar-btn:hover) {
		background: rgba(59, 130, 246, 0.1) !important;
		color: #3b82f6 !important;
	}
	
	/* Dark mode adaptations */
	:global(.dark) .analytics-chart-container :global(.modebar) {
		background: rgba(30, 41, 59, 0.9) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
	}
	
	:global(.dark) .analytics-chart-container :global(.modebar-btn) {
		color: #94a3b8 !important;
	}
	
	:global(.dark) .analytics-chart-container :global(.modebar-btn:hover) {
		background: rgba(59, 130, 246, 0.2) !important;
		color: #60a5fa !important;
	}
</style>