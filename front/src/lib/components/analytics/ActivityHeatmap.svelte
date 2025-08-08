<!--
  Activity Heatmap Component - GitHub-Style Booking Activity
  Interactive heatmap showing booking patterns with Saudi calendar integration
-->
<script lang="ts">
import AnalyticsChart from './AnalyticsChart.svelte';
import { Calendar, TrendingUp, Users, Clock } from '@lucide/svelte';
import { Badge } from '$lib/components/ui/badge';
import { Button } from '$lib/components/ui/button';

// Props using Svelte 5 $props rune
interface Props {
	activityData: Array<{
		date: string;
		bookings: number;
		revenue: number;
		intensity: number; // 0-4 scale
	}>;
	year?: number;
	height?: number;
	showStats?: boolean;
	autoRefresh?: boolean;
	containerClass?: string;
}

const {
	activityData,
	year = new Date().getFullYear(),
	height = 250,
	showStats = true,
	autoRefresh = false,
	containerClass = ''
}: Props = $props();

// Derived reactive computations
const totalBookings = $derived(() => 
	activityData.reduce((sum, day) => sum + day.bookings, 0)
);

const totalRevenue = $derived(() => 
	activityData.reduce((sum, day) => sum + day.revenue, 0)
);

const avgDailyBookings = $derived(() => 
	activityData.length > 0 ? totalBookings / activityData.length : 0
);

const peakDay = $derived(() => 
	activityData.reduce((max, current) => 
		current.bookings > max.bookings ? current : max,
		{ date: '', bookings: 0, revenue: 0, intensity: 0 }
	)
);

const currentStreak = $derived(() => calculateCurrentStreak());
const longestStreak = $derived(() => calculateLongestStreak());
const activeDays = $derived(() => activityData.filter(day => day.bookings > 0).length);
const activityLevels = $derived(() => calculateActivityLevels());

// Saudi calendar months in Arabic
const arabicMonths = [
	'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
	'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
];

// Chart configuration
const chartOptions = $derived(() => ({
	year,
	showLegend: true,
	clickable: true,
	tooltipFormat: 'arabic'
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

function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('ar-SA', {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		timeZone: 'Asia/Riyadh'
	}).format(date);
}

function calculateCurrentStreak(): number {
	if (activityData.length === 0) return 0;
	
	let streak = 0;
	const today = new Date();
	const sortedData = [...activityData].sort((a, b) => 
		new Date(b.date).getTime() - new Date(a.date).getTime()
	);
	
	for (const day of sortedData) {
		const dayDate = new Date(day.date);
		const daysDiff = Math.floor((today.getTime() - dayDate.getTime()) / (1000 * 60 * 60 * 24));
		
		if (daysDiff > streak && day.bookings > 0) {
			streak++;
		} else if (day.bookings === 0) {
			break;
		}
	}
	
	return streak;
}

function calculateLongestStreak(): number {
	if (activityData.length === 0) return 0;
	
	let longestStreak = 0;
	let currentStreakCount = 0;
	
	const sortedData = [...activityData].sort((a, b) => 
		new Date(a.date).getTime() - new Date(b.date).getTime()
	);
	
	for (const day of sortedData) {
		if (day.bookings > 0) {
			currentStreakCount++;
			longestStreak = Math.max(longestStreak, currentStreakCount);
		} else {
			currentStreakCount = 0;
		}
	}
	
	return longestStreak;
}

function calculateActivityLevels(): {
	none: number;
	low: number;
	medium: number;
	high: number;
	veryHigh: number;
} {
	const levels = { none: 0, low: 0, medium: 0, high: 0, veryHigh: 0 };
	
	for (const day of activityData) {
		switch (day.intensity) {
			case 0: levels.none++; break;
			case 1: levels.low++; break;
			case 2: levels.medium++; break;
			case 3: levels.high++; break;
			case 4: levels.veryHigh++; break;
		}
	}
	
	return levels;
}

function getIntensityLabel(intensity: number): string {
	const labels = ['لا يوجد', 'قليل', 'متوسط', 'عالي', 'عالي جداً'];
	return labels[intensity] || 'غير معروف';
}

function getIntensityColor(intensity: number): string {
	const colors = [
		'bg-slate-100 dark:bg-slate-800',
		'bg-emerald-100 dark:bg-emerald-900/30',
		'bg-emerald-200 dark:bg-emerald-800/50',
		'bg-emerald-400 dark:bg-emerald-600/70',
		'bg-emerald-600 dark:bg-emerald-500'
	];
	return colors[intensity] || colors[0];
}
</script>

<!-- Activity Heatmap Component -->
<div class="activity-heatmap-wrapper {containerClass}">
	{#if showStats}
		<!-- Summary Statistics -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
			<!-- Total Bookings -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							إجمالي الحجوزات
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{totalBookings.toLocaleString('ar-SA')}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-950 dark:to-blue-900">
						<Calendar class="h-5 w-5 text-blue-600 dark:text-blue-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					في عام {year}
				</p>
			</div>

			<!-- Average Daily -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							المتوسط اليومي
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{avgDailyBookings.toFixed(1)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-green-100 to-green-200 dark:from-green-950 dark:to-green-900">
						<TrendingUp class="h-5 w-5 text-green-600 dark:text-green-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					حجز في اليوم
				</p>
			</div>

			<!-- Current Streak -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							السلسلة الحالية
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{currentStreak}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-950 dark:to-orange-900">
						<Users class="h-5 w-5 text-orange-600 dark:text-orange-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					يوم متتالي
				</p>
			</div>

			<!-- Peak Day -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							أعلى نشاط
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{peakDay.bookings}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900">
						<Clock class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					{peakDay.date ? new Date(peakDay.date).toLocaleDateString('ar-SA') : 'غير متاح'}
				</p>
			</div>
		</div>
	{/if}

	<!-- Main Heatmap Chart -->
	<AnalyticsChart
		chartType="heatmap"
		data={activityData}
		title="نشاط الحجوزات - {year}"
		subtitle="مخطط حراري يعرض أنماط النشاط اليومي على مدار العام مع تكامل التقويم السعودي"
		{height}
		options={chartOptions}
		cacheKey="heatmap-{year}"
		{autoRefresh}
		refreshInterval={60000}
		showControls={true}
		showFullscreen={true}
		{containerClass}
	/>

	<!-- Activity Legend & Insights -->
	<div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Activity Legend -->
		<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
			<h4 class="font-bold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-2">
				<div class="h-3 w-3 rounded-sm bg-emerald-500"></div>
				مقياس النشاط
			</h4>
			
			<div class="space-y-3">
				<!-- Legend Scale -->
				<div class="flex items-center gap-2 text-sm">
					<span class="text-slate-600 dark:text-slate-400">أقل</span>
					<div class="flex gap-1">
						{#each [0, 1, 2, 3, 4] as intensity}
							<div 
								class="h-3 w-3 rounded-sm {getIntensityColor(intensity)}"
								title={getIntensityLabel(intensity)}
							></div>
						{/each}
					</div>
					<span class="text-slate-600 dark:text-slate-400">أكثر</span>
				</div>
				
				<!-- Activity Breakdown -->
				<div class="space-y-2">
					{#each Object.entries(activityLevels) as [level, count]}
						{@const levelMap = {
							none: { label: 'لا يوجد نشاط', color: 'text-slate-500' },
							low: { label: 'نشاط قليل', color: 'text-emerald-400' },
							medium: { label: 'نشاط متوسط', color: 'text-emerald-500' },
							high: { label: 'نشاط عالي', color: 'text-emerald-600' },
							veryHigh: { label: 'نشاط عالي جداً', color: 'text-emerald-700' }
						}}
						<div class="flex items-center justify-between text-sm">
							<span class="text-slate-600 dark:text-slate-400">
								{levelMap[level as keyof typeof levelMap].label}
							</span>
							<Badge variant="outline" class="border-slate-300 text-slate-700 dark:border-slate-600 dark:text-slate-300">
								{count} يوم
							</Badge>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Activity Insights -->
		<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
			<h4 class="font-bold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-2">
				<svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
				</svg>
				تحليلات النشاط
			</h4>
			
			<div class="space-y-4">
				<!-- Streak Information -->
				<div class="p-3 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200/50 dark:border-blue-800/50">
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-sm font-semibold text-blue-800 dark:text-blue-200">
								أطول سلسلة نشاط
							</span>
							<Badge variant="outline" class="border-blue-300 text-blue-700 dark:border-blue-700 dark:text-blue-300">
								{longestStreak} يوم
							</Badge>
						</div>
						<div class="text-xs text-blue-600 dark:text-blue-400">
							السلسلة الحالية: {currentStreak} يوم
						</div>
					</div>
				</div>

				<!-- Activity Distribution -->
				<div class="p-3 rounded-lg bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-950/30 dark:to-green-950/30 border border-emerald-200/50 dark:border-emerald-800/50">
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-sm font-semibold text-emerald-800 dark:text-emerald-200">
								الأيام النشطة
							</span>
							<Badge variant="outline" class="border-emerald-300 text-emerald-700 dark:border-emerald-700 dark:text-emerald-300">
								{activeDays} من {activityData.length}
							</Badge>
						</div>
						<div class="text-xs text-emerald-600 dark:text-emerald-400">
							معدل النشاط: {((activeDays / activityData.length) * 100).toFixed(1)}%
						</div>
					</div>
				</div>

				<!-- Revenue Correlation -->
				{#if totalRevenue > 0}
					<div class="p-3 rounded-lg bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-950/30 dark:to-violet-950/30 border border-purple-200/50 dark:border-purple-800/50">
						<div class="space-y-2">
							<div class="flex items-center justify-between">
								<span class="text-sm font-semibold text-purple-800 dark:text-purple-200">
									إجمالي الإيرادات
								</span>
								<Badge variant="outline" class="border-purple-300 text-purple-700 dark:border-purple-700 dark:text-purple-300">
									{formatCurrency(totalRevenue)}
								</Badge>
							</div>
							<div class="text-xs text-purple-600 dark:text-purple-400">
								متوسط الإيرادات لليوم النشط: {formatCurrency(totalRevenue / activeDays)}
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.activity-heatmap-wrapper {
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