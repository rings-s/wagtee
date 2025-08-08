<!--
  Service Performance Chart Component - Business Intelligence for Services
  Horizontal bar chart showing service revenue, bookings, and performance metrics
-->
<script lang="ts">
import AnalyticsChart from './AnalyticsChart.svelte';
import { Crown, TrendingUp, TrendingDown, Star, Users, DollarSign } from '@lucide/svelte';
import { Badge } from '$lib/components/ui/badge';
import { Button } from '$lib/components/ui/button';
import * as Card from '$lib/components/ui/card';

// Props using Svelte 5 $props rune
interface Props {
	servicesData: Array<{
		id: number;
		name: string;
		name_ar: string;
		bookings: number;
		revenue: number;
		rating: number;
		profit_margin: number;
		efficiency_score?: number;
		trend: 'up' | 'down' | 'stable';
		growth_rate?: number;
	}>;
	period?: 'today' | 'week' | 'month' | 'quarter' | 'year';
	maxServices?: number;
	height?: number;
	showDetails?: boolean;
	sortBy?: 'revenue' | 'bookings' | 'rating' | 'profit_margin';
	autoRefresh?: boolean;
	containerClass?: string;
}

const {
	servicesData,
	period = 'month',
	maxServices = 8,
	height = 500,
	showDetails = true,
	sortBy = 'revenue',
	autoRefresh = false,
	containerClass = ''
}: Props = $props();

// Derived reactive computations
const sortedServices = $derived(() => {
	const sorted = [...servicesData].sort((a, b) => {
		switch (sortBy) {
			case 'revenue': return b.revenue - a.revenue;
			case 'bookings': return b.bookings - a.bookings;
			case 'rating': return b.rating - a.rating;
			case 'profit_margin': return b.profit_margin - a.profit_margin;
			default: return b.revenue - a.revenue;
		}
	});
	return sorted.slice(0, maxServices);
});

const topPerformer = $derived(() => sortedServices[0] || null);
const totalRevenue = $derived(() => servicesData.reduce((sum, s) => sum + s.revenue, 0));
const totalBookings = $derived(() => servicesData.reduce((sum, s) => sum + s.bookings, 0));
const averageRating = $derived(() => {
	const validRatings = servicesData.filter(s => s.rating > 0);
	return validRatings.length > 0 
		? validRatings.reduce((sum, s) => sum + s.rating, 0) / validRatings.length 
		: 0;
});

const periodLabels: Record<string, string> = {
	today: 'اليوم',
	week: 'هذا الأسبوع',
	month: 'هذا الشهر', 
	quarter: 'هذا الربع',
	year: 'هذا العام'
};

const sortLabels: Record<string, string> = {
	revenue: 'الإيرادات',
	bookings: 'الحجوزات',
	rating: 'التقييم',
	profit_margin: 'هامش الربح'
};

// Chart configuration
const chartOptions = $derived(() => ({
	maxServices,
	sortBy,
	showTrends: true,
	showRatings: true
}));

// Helper functions
function formatCurrency(amount: number): string {
	return new Intl.NumberFormat('ar-SA', {
		style: 'currency',
		currency: 'SAR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 2
	}).format(amount);
}

function formatNumber(num: number): string {
	return new Intl.NumberFormat('ar-SA').format(num);
}

function formatPercentage(percent: number): string {
	return `${percent.toFixed(1)}%`;
}

function getTrendIcon(trend: 'up' | 'down' | 'stable') {
	switch (trend) {
		case 'up': return TrendingUp;
		case 'down': return TrendingDown;
		default: return null;
	}
}

function getTrendColor(trend: 'up' | 'down' | 'stable'): string {
	switch (trend) {
		case 'up': return 'text-emerald-600 dark:text-emerald-400';
		case 'down': return 'text-red-600 dark:text-red-400';
		default: return 'text-slate-600 dark:text-slate-400';
	}
}

function getPerformanceLevel(score: number): {
	label: string;
	color: string;
	bgColor: string;
} {
	if (score >= 80) {
		return {
			label: 'ممتاز',
			color: 'text-emerald-700 dark:text-emerald-300',
			bgColor: 'bg-emerald-100 dark:bg-emerald-900/30'
		};
	} else if (score >= 60) {
		return {
			label: 'جيد',
			color: 'text-blue-700 dark:text-blue-300',
			bgColor: 'bg-blue-100 dark:bg-blue-900/30'
		};
	} else if (score >= 40) {
		return {
			label: 'متوسط',
			color: 'text-yellow-700 dark:text-yellow-300',
			bgColor: 'bg-yellow-100 dark:bg-yellow-900/30'
		};
	} else {
		return {
			label: 'ضعيف',
			color: 'text-red-700 dark:text-red-300',
			bgColor: 'bg-red-100 dark:bg-red-900/30'
		};
	}
}
</script>

<!-- Service Performance Chart Component -->
<div class="service-performance-wrapper {containerClass}">
	{#if showDetails}
		<!-- Summary Statistics -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<!-- Total Services -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							إجمالي الخدمات
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{servicesData.length}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900">
						<Crown class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					خدمة متاحة
				</p>
			</div>

			<!-- Total Revenue -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							إجمالي الإيرادات
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{formatCurrency(totalRevenue)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900">
						<DollarSign class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					{periodLabels[period]}
				</p>
			</div>

			<!-- Total Bookings -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							إجمالي الحجوزات
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{formatNumber(totalBookings)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-950 dark:to-blue-900">
						<Users class="h-5 w-5 text-blue-600 dark:text-blue-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					حجز كلي
				</p>
			</div>

			<!-- Average Rating -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							متوسط التقييم
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{averageRating.toFixed(1)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-950 dark:to-amber-900">
						<Star class="h-5 w-5 text-amber-600 dark:text-amber-400 fill-current" />
					</div>
				</div>
				<div class="flex items-center gap-1 mt-2">
					{#each Array(5) as _, i}
						<Star class="h-3 w-3 {i < Math.floor(averageRating) ? 'text-amber-500 fill-current' : 'text-slate-300 dark:text-slate-600'}" />
					{/each}
				</div>
			</div>
		</div>

		<!-- Sort Controls -->
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center gap-2">
				<span class="text-sm font-medium text-slate-600 dark:text-slate-400">ترتيب حسب:</span>
				<div class="flex items-center gap-1 rounded-lg bg-white/60 dark:bg-slate-800/60 p-1 backdrop-blur-sm border border-white/20">
					{#each Object.entries(sortLabels) as [value, label]}
						<button
							onclick={() => sortBy = value as typeof sortBy}
							class="px-3 py-1.5 text-sm font-semibold rounded-md transition-all duration-300 {sortBy === value 
								? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg' 
								: 'text-slate-600 dark:text-slate-400 hover:bg-white/40 dark:hover:bg-slate-700/40'
							}"
						>
							{label}
						</button>
					{/each}
				</div>
			</div>

			{#if topPerformer}
				<Badge variant="outline" class="border-purple-300 text-purple-700 dark:border-purple-700 dark:text-purple-300">
					الأفضل: {topPerformer.name_ar || topPerformer.name}
				</Badge>
			{/if}
		</div>
	{/if}

	<!-- Main Performance Chart -->
	<AnalyticsChart
		chartType="services"
		data={sortedServices}
		title="أداء الخدمات"
		subtitle="تحليل تفصيلي لأداء الخدمات من حيث الإيرادات والحجوزات والتقييمات مع مؤشرات الاتجاه"
		{height}
		options={chartOptions}
		cacheKey="services-{period}-{sortBy}-{maxServices}"
		{autoRefresh}
		refreshInterval={60000}
		showControls={true}
		showFullscreen={true}
		{containerClass}
	/>

	<!-- Detailed Service List -->
	{#if showDetails && sortedServices.length > 0}
		<div class="mt-6">
			<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl">
				<Card.Header>
					<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200">
						تفاصيل الخدمات
					</Card.Title>
					<Card.Description class="text-slate-600 dark:text-slate-400">
						قائمة مفصلة بأداء كل خدمة مع المؤشرات والاتجاهات
					</Card.Description>
				</Card.Header>
				<Card.Content>
					<div class="space-y-4">
						{#each sortedServices as service, index}
							{@const performanceScore = service.efficiency_score || ((service.rating / 5) * 100)}
							{@const performance = getPerformanceLevel(performanceScore)}
							
							<div class="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-white/50 to-white/30 dark:from-slate-800/50 dark:to-slate-800/30 border border-white/30 dark:border-slate-700/30 backdrop-blur-sm hover:shadow-lg transition-all duration-300">
								<!-- Service Info -->
								<div class="flex items-center gap-4">
									<!-- Ranking Badge -->
									<div class="flex h-10 w-10 items-center justify-center rounded-xl {index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white' : index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-white' : index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' : 'bg-gradient-to-br from-slate-200 to-slate-300 text-slate-600'} text-sm font-bold">
										{index + 1}
									</div>
									
									<!-- Service Details -->
									<div class="space-y-1">
										<div class="flex items-center gap-3">
											<h4 class="font-bold text-slate-800 dark:text-slate-200">
												{service.name_ar || service.name}
											</h4>
											{#if service.trend && service.trend !== 'stable'}
												{@const TrendIcon = getTrendIcon(service.trend)}
												{#if TrendIcon}
													<svelte:component 
														this={TrendIcon} 
														class="h-4 w-4 {getTrendColor(service.trend)}" 
													/>
												{/if}
											{/if}
										</div>
										
										<div class="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
											<div class="flex items-center gap-1">
												<DollarSign class="h-3 w-3" />
												<span>{formatCurrency(service.revenue)}</span>
											</div>
											<div class="flex items-center gap-1">
												<Users class="h-3 w-3" />
												<span>{formatNumber(service.bookings)} حجز</span>
											</div>
											{#if service.rating > 0}
												<div class="flex items-center gap-1">
													<Star class="h-3 w-3 text-amber-500 fill-current" />
													<span>{service.rating.toFixed(1)}</span>
												</div>
											{/if}
										</div>
									</div>
								</div>

								<!-- Performance Metrics -->
								<div class="flex items-center gap-4">
									<!-- Profit Margin -->
									<div class="text-center">
										<div class="text-sm font-bold text-slate-800 dark:text-slate-200">
											{formatPercentage(service.profit_margin)}
										</div>
										<div class="text-xs text-slate-500 dark:text-slate-500">
											هامش الربح
										</div>
									</div>

									<!-- Performance Score -->
									<div class="text-center">
										<Badge variant="outline" class="border-current/20 bg-current/5 {performance.color}">
											{performance.label}
										</Badge>
										<div class="text-xs text-slate-500 dark:text-slate-500 mt-1">
											{performanceScore.toFixed(0)}%
										</div>
									</div>

									<!-- Growth Rate -->
									{#if service.growth_rate !== undefined}
										<div class="text-center">
											<div class="text-sm font-bold {getTrendColor(service.trend)}">
												{service.growth_rate >= 0 ? '+' : ''}{service.growth_rate.toFixed(1)}%
											</div>
											<div class="text-xs text-slate-500 dark:text-slate-500">
												النمو
											</div>
										</div>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	{/if}
</div>

<style>
	.service-performance-wrapper {
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