<!--
  Revenue Chart Component - Saudi Market Analytics
  Interactive revenue trend visualization with growth indicators
-->
<script lang="ts">
import AnalyticsChart from './AnalyticsChart.svelte';
import type { AnalyticsData } from '$lib/services/analytics-api.js';
import { TrendingUp, TrendingDown, DollarSign } from '@lucide/svelte';
import { Badge } from '$lib/components/ui/badge';

// Props using Svelte 5 $props rune
interface Props {
	analyticsData: AnalyticsData;
	period?: 'today' | 'week' | 'month' | 'quarter' | 'year';
	height?: number;
	showGrowth?: boolean;
	showProjections?: boolean;
	autoRefresh?: boolean;
	containerClass?: string;
}

const {
	analyticsData,
	period = 'month',
	height = 450,
	showGrowth = true,
	showProjections = false,
	autoRefresh = false,
	containerClass = ''
}: Props = $props();

// Derived reactive computations
const revenueData = $derived(() => analyticsData?.revenue_trend || []);
const totalRevenue = $derived(() => analyticsData?.revenue_growth?.current_period || 0);
const previousRevenue = $derived(() => analyticsData?.revenue_growth?.previous_period || 0);
const growthRate = $derived(() => analyticsData?.revenue_growth?.growth_rate || 0);
const growthAmount = $derived(() => analyticsData?.revenue_growth?.growth_amount || 0);

// Chart configuration
const chartOptions = $derived(() => ({
	showGrowth,
	period,
	showProjections,
	annotations: showProjections ? getProjectionAnnotations() : undefined
}));

const periodLabels: Record<string, string> = {
	today: 'اليوم',
	week: 'هذا الأسبوع', 
	month: 'هذا الشهر',
	quarter: 'هذا الربع',
	year: 'هذا العام'
};

// Helper functions
function formatCurrency(amount: number): string {
	return new Intl.NumberFormat('ar-SA', {
		style: 'currency',
		currency: 'SAR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 2
	}).format(amount);
}

function formatPercentage(percent: number): string {
	const sign = percent >= 0 ? '+' : '';
	return `${sign}${percent.toFixed(1)}%`;
}

function getGrowthColor(): string {
	if (growthRate > 0) return 'text-emerald-600 dark:text-emerald-400';
	if (growthRate < 0) return 'text-red-600 dark:text-red-400';
	return 'text-slate-600 dark:text-slate-400';
}

function getGrowthIcon() {
	return growthRate >= 0 ? TrendingUp : TrendingDown;
}

function getProjectionAnnotations() {
	if (!showProjections || !revenueData.length) return [];
	
	const lastDataPoint = revenueData[revenueData.length - 1];
	const projectedValue = lastDataPoint.value * (1 + (growthRate / 100));
	
	return [
		{
			x: revenueData.length,
			y: projectedValue,
			text: 'توقع',
			showarrow: true,
			arrowhead: 2,
			arrowsize: 1,
			arrowcolor: '#f59e0b',
			bgcolor: 'rgba(245, 158, 11, 0.1)',
			bordercolor: '#f59e0b',
			font: { color: '#92400e' }
		}
	];
}
</script>

<!-- Revenue Chart Component -->
<div class="revenue-chart-wrapper {containerClass}">
	<!-- Summary Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
		<!-- Total Revenue -->
		<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<div class="space-y-1">
					<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
						إجمالي الإيرادات
					</p>
					<p class="text-2xl font-black text-slate-800 dark:text-slate-200">
						{formatCurrency(totalRevenue)}
					</p>
				</div>
				<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900">
					<DollarSign class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
				</div>
			</div>
			<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
				{periodLabels[period]}
			</p>
		</div>

		<!-- Growth Rate -->
		<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<div class="space-y-1">
					<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
						معدل النمو
					</p>
					<p class="text-2xl font-black {getGrowthColor()}">
						{formatPercentage(growthRate)}
					</p>
				</div>
				<div class="flex h-12 w-12 items-center justify-center rounded-xl {growthRate >= 0 ? 'bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900' : 'bg-gradient-to-br from-red-100 to-red-200 dark:from-red-950 dark:to-red-900'}">
					<svelte:component 
						this={getGrowthIcon()} 
						class="h-6 w-6 {growthRate >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}" 
					/>
				</div>
			</div>
			<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
				مقارنة بالفترة السابقة
			</p>
		</div>

		<!-- Growth Amount -->
		<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
			<div class="flex items-center justify-between">
				<div class="space-y-1">
					<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
						مقدار النمو
					</p>
					<p class="text-2xl font-black {getGrowthColor()}">
						{formatCurrency(Math.abs(growthAmount))}
					</p>
				</div>
				<Badge 
					variant="outline" 
					class="{growthRate >= 0 ? 'border-emerald-300 text-emerald-700 dark:border-emerald-700 dark:text-emerald-300' : 'border-red-300 text-red-700 dark:border-red-700 dark:text-red-300'}"
				>
					{growthRate >= 0 ? 'زيادة' : 'نقص'}
				</Badge>
			</div>
			<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
				{formatCurrency(previousRevenue)} في الفترة السابقة
			</p>
		</div>
	</div>

	<!-- Main Chart -->
	<AnalyticsChart
		chartType="revenue"
		data={analyticsData}
		title="تطور الإيرادات"
		subtitle="تحليل تفصيلي لنمو الإيرادات مع مؤشرات الأداء والتوقعات المستقبلية"
		{height}
		options={chartOptions}
		cacheKey="revenue-{period}-{showGrowth}-{showProjections}"
		{autoRefresh}
		refreshInterval={30000}
		showControls={true}
		showFullscreen={true}
		{containerClass}
	/>

	<!-- Additional Insights -->
	{#if revenueData.length > 0}
		<div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Performance Insights -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<h4 class="font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
					<svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
					</svg>
					تحليل الأداء
				</h4>
				<div class="space-y-3">
					{#if growthRate > 10}
						<div class="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
							<TrendingUp class="h-4 w-4" />
							<span>نمو ممتاز! معدل النمو أعلى من المتوسط</span>
						</div>
					{:else if growthRate > 0}
						<div class="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
							<TrendingUp class="h-4 w-4" />
							<span>نمو إيجابي مستقر</span>
						</div>
					{:else if growthRate < -10}
						<div class="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
							<TrendingDown class="h-4 w-4" />
							<span>انخفاض كبير يحتاج انتباه</span>
						</div>
					{:else}
						<div class="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
							<TrendingDown class="h-4 w-4" />
							<span>انخفاض طفيف</span>
						</div>
					{/if}
					
					<!-- Average Daily Revenue -->
					{#if period === 'month'}
						<div class="text-sm text-slate-600 dark:text-slate-400">
							متوسط الإيرادات اليومية: 
							<span class="font-semibold text-slate-800 dark:text-slate-200">
								{formatCurrency(totalRevenue / 30)}
							</span>
						</div>
					{/if}
				</div>
			</div>

			<!-- Trend Analysis -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<h4 class="font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
					<svg class="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
					</svg>
					توقعات المستقبل
				</h4>
				<div class="space-y-3">
					{#if showProjections}
						{#if growthRate > 0}
							<div class="text-sm text-emerald-600 dark:text-emerald-400">
								متوقع نمو الإيرادات بنسبة {formatPercentage(growthRate)} في الفترة القادمة
							</div>
						{:else}
							<div class="text-sm text-amber-600 dark:text-amber-400">
								يُنصح بمراجعة الاستراتيجية التسويقية لتحسين الأداء
							</div>
						{/if}
					{:else}
						<button 
							onclick={() => showProjections = true}
							class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
						>
							عرض التوقعات المستقبلية
						</button>
					{/if}
					
					<!-- Best performing period -->
					{#if revenueData.length > 1}
						{@const bestPeriod = revenueData.reduce((max, current) => 
							current.value > max.value ? current : max
						)}
						<div class="text-sm text-slate-600 dark:text-slate-400">
							أفضل أداء: 
							<span class="font-semibold text-slate-800 dark:text-slate-200">
								{formatCurrency(bestPeriod.value)} في {bestPeriod.period}
							</span>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.revenue-chart-wrapper {
		@apply space-y-0;
	}
	
	.glass-card {
		background: rgba(255, 255, 255, 0.25);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border: 1px solid rgba(255, 255, 255, 0.18);
		box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
	}

	.dark .glass-card {
		background: rgba(15, 23, 42, 0.25);
		border: 1px solid rgba(255, 255, 255, 0.05);
		box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
	}
</style>