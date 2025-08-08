<!--
  Customer Segment Chart Component - Customer Analytics & Segmentation
  Donut chart with detailed customer segment analysis and insights
-->
<script lang="ts">
import AnalyticsChart from './AnalyticsChart.svelte';
import { Users, Heart, UserPlus, Crown, TrendingUp, Percent } from '@lucide/svelte';
import { Badge } from '$lib/components/ui/badge';
import { Button } from '$lib/components/ui/button';
import * as Card from '$lib/components/ui/card';
import { Progress } from '$lib/components/ui/progress';

// Props using Svelte 5 $props rune
interface Props {
	segmentsData: Array<{
		name: string;
		name_ar: string;
		count: number;
		percentage: number;
		avg_spend: number;
		loyalty_score: number;
		retention_rate: number;
		growth_rate: number;
		characteristics?: string[];
	}>;
	totalCustomers?: number;
	period?: string;
	height?: number;
	showInsights?: boolean;
	autoRefresh?: boolean;
	containerClass?: string;
}

const {
	segmentsData,
	totalCustomers = 0,
	period = 'month',
	height = 450,
	showInsights = true,
	autoRefresh = false,
	containerClass = ''
}: Props = $props();

// Derived reactive computations
const totalSegmentCustomers = $derived(() => 
	segmentsData.reduce((sum, segment) => sum + segment.count, 0)
);

const totalRevenue = $derived(() => 
	segmentsData.reduce((sum, segment) => sum + (segment.avg_spend * segment.count), 0)
);

const mostValuableSegment = $derived(() => 
	segmentsData.reduce((max, current) => 
		current.avg_spend > max.avg_spend ? current : max,
		segmentsData[0] || { avg_spend: 0 }
	)
);

const mostLoyalSegment = $derived(() => 
	segmentsData.reduce((max, current) => 
		current.loyalty_score > max.loyalty_score ? current : max,
		segmentsData[0] || { loyalty_score: 0 }
	)
);

const fastestGrowingSegment = $derived(() => 
	segmentsData.reduce((max, current) => 
		current.growth_rate > max.growth_rate ? current : max,
		segmentsData[0] || { growth_rate: 0 }
	)
);

// Chart configuration
const chartOptions = $derived(() => ({
	showPercentages: true,
	showValues: true,
	showLegend: true
}));

// Segment icons and colors
const segmentConfig: Record<string, { 
	icon: any; 
	color: string; 
	bgColor: string;
	description: string;
}> = {
	new: {
		icon: UserPlus,
		color: 'text-blue-600 dark:text-blue-400',
		bgColor: 'bg-blue-100 dark:bg-blue-900/30',
		description: 'عملاء جدد، أول مرة يتعاملون مع المؤسسة'
	},
	regular: {
		icon: Users,
		color: 'text-green-600 dark:text-green-400',
		bgColor: 'bg-green-100 dark:bg-green-900/30',
		description: 'عملاء منتظمون، يتعاملون بشكل دوري'
	},
	vip: {
		icon: Crown,
		color: 'text-purple-600 dark:text-purple-400',
		bgColor: 'bg-purple-100 dark:bg-purple-900/30',
		description: 'عملاء مميزون، أعلى قيمة إنفاق وولاء'
	},
	inactive: {
		icon: Heart,
		color: 'text-gray-600 dark:text-gray-400',
		bgColor: 'bg-gray-100 dark:bg-gray-900/30',
		description: 'عملاء غير نشطين، لم يتعاملوا مؤخراً'
	}
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

function formatNumber(num: number): string {
	return new Intl.NumberFormat('ar-SA').format(num);
}

function formatPercentage(percent: number): string {
	return `${percent.toFixed(1)}%`;
}

function getSegmentKey(name: string): string {
	const key = name.toLowerCase();
	if (key.includes('new') || key.includes('جديد')) return 'new';
	if (key.includes('vip') || key.includes('مميز')) return 'vip';
	if (key.includes('inactive') || key.includes('غير نشط')) return 'inactive';
	return 'regular';
}

function getLoyaltyLabel(score: number): { label: string; color: string } {
	if (score >= 80) return { label: 'عالي جداً', color: 'text-emerald-600 dark:text-emerald-400' };
	if (score >= 60) return { label: 'عالي', color: 'text-green-600 dark:text-green-400' };
	if (score >= 40) return { label: 'متوسط', color: 'text-yellow-600 dark:text-yellow-400' };
	if (score >= 20) return { label: 'منخفض', color: 'text-orange-600 dark:text-orange-400' };
	return { label: 'ضعيف جداً', color: 'text-red-600 dark:text-red-400' };
}
</script>

<!-- Customer Segment Chart Component -->
<div class="customer-segment-wrapper {containerClass}">
	{#if showInsights}
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<!-- Total Customers -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							إجمالي العملاء
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{formatNumber(totalSegmentCustomers)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-950 dark:to-blue-900">
						<Users class="h-5 w-5 text-blue-600 dark:text-blue-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					عميل مسجل
				</p>
			</div>

			<!-- Most Valuable Segment -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							الأعلى قيمة
						</p>
						<p class="text-lg font-black text-slate-800 dark:text-slate-200">
							{mostValuableSegment.name_ar || mostValuableSegment.name}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900">
						<Crown class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					{formatCurrency(mostValuableSegment.avg_spend)} متوسط الإنفاق
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
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900">
						<TrendingUp class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					من جميع الشرائح
				</p>
			</div>

			<!-- Average Loyalty -->
			<div class="glass-card rounded-xl p-4 border border-white/20 backdrop-blur-xl">
				<div class="flex items-center justify-between">
					<div class="space-y-1">
						<p class="text-sm font-medium text-slate-600 dark:text-slate-400">
							متوسط الولاء
						</p>
						<p class="text-xl font-black text-slate-800 dark:text-slate-200">
							{(segmentsData.reduce((sum, s) => sum + s.loyalty_score, 0) / segmentsData.length).toFixed(1)}
						</p>
					</div>
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-red-100 to-red-200 dark:from-red-950 dark:to-red-900">
						<Heart class="h-5 w-5 text-red-600 dark:text-red-400" />
					</div>
				</div>
				<p class="text-xs text-slate-500 dark:text-slate-500 mt-2">
					من 100 درجة
				</p>
			</div>
		</div>
	{/if}

	<!-- Main Segment Chart -->
	<AnalyticsChart
		chartType="segments"
		data={segmentsData}
		title="شرائح العملاء"
		subtitle="تحليل مفصل لقاعدة العملاء مقسمة حسب السلوك وقيمة الإنفاق ومستوى الولاء"
		{height}
		options={chartOptions}
		cacheKey="segments-{period}"
		{autoRefresh}
		refreshInterval={120000}
		showControls={true}
		showFullscreen={true}
		{containerClass}
	/>

	<!-- Detailed Segment Analysis -->
	{#if showInsights && segmentsData.length > 0}
		<div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Segment Details -->
			<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl">
				<Card.Header>
					<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
						<Users class="h-5 w-5" />
						تفاصيل الشرائح
					</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-4">
					{#each segmentsData as segment}
						{@const segmentKey = getSegmentKey(segment.name)}
						{@const config = segmentConfig[segmentKey]}
						{@const loyaltyInfo = getLoyaltyLabel(segment.loyalty_score)}
						
						<div class="p-4 rounded-xl {config.bgColor} border border-current/20">
							<div class="flex items-center justify-between mb-3">
								<div class="flex items-center gap-3">
									<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-white/60 dark:bg-slate-800/60">
										<svelte:component this={config.icon} class="h-5 w-5 {config.color}" />
									</div>
									<div>
										<h4 class="font-bold text-slate-800 dark:text-slate-200">
											{segment.name_ar || segment.name}
										</h4>
										<p class="text-xs text-slate-600 dark:text-slate-400">
											{config.description}
										</p>
									</div>
								</div>
								<Badge variant="outline" class="border-current/30 text-current {config.color}">
									{formatNumber(segment.count)} عميل
								</Badge>
							</div>

							<!-- Segment Metrics -->
							<div class="grid grid-cols-2 gap-4">
								<div class="space-y-2">
									<div class="flex justify-between items-center">
										<span class="text-sm text-slate-600 dark:text-slate-400">النسبة</span>
										<span class="font-bold text-slate-800 dark:text-slate-200">
											{formatPercentage(segment.percentage)}
										</span>
									</div>
									<Progress value={segment.percentage} class="h-2" />
								</div>

								<div class="space-y-2">
									<div class="flex justify-between items-center">
										<span class="text-sm text-slate-600 dark:text-slate-400">الولاء</span>
										<span class="font-bold {loyaltyInfo.color}">
											{loyaltyInfo.label}
										</span>
									</div>
									<Progress value={segment.loyalty_score} class="h-2" />
								</div>

								<div class="text-center p-2 rounded bg-white/40 dark:bg-slate-700/40">
									<div class="text-sm font-bold text-slate-800 dark:text-slate-200">
										{formatCurrency(segment.avg_spend)}
									</div>
									<div class="text-xs text-slate-500 dark:text-slate-500">
										متوسط الإنفاق
									</div>
								</div>

								<div class="text-center p-2 rounded bg-white/40 dark:bg-slate-700/40">
									<div class="text-sm font-bold text-slate-800 dark:text-slate-200">
										{formatPercentage(segment.retention_rate)}
									</div>
									<div class="text-xs text-slate-500 dark:text-slate-500">
										معدل الاحتفاظ
									</div>
								</div>
							</div>

							<!-- Growth Rate -->
							{#if segment.growth_rate !== undefined}
								<div class="mt-3 flex items-center gap-2 text-sm">
									{#if segment.growth_rate > 0}
										<TrendingUp class="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
										<span class="text-emerald-600 dark:text-emerald-400 font-semibold">
											نمو {formatPercentage(segment.growth_rate)}
										</span>
									{:else if segment.growth_rate < 0}
										<svg class="h-4 w-4 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
										</svg>
										<span class="text-red-600 dark:text-red-400 font-semibold">
											انخفاض {formatPercentage(Math.abs(segment.growth_rate))}
										</span>
									{:else}
										<span class="text-slate-600 dark:text-slate-400 font-semibold">
											مستقر
										</span>
									{/if}
								</div>
							{/if}
						</div>
					{/each}
				</Card.Content>
			</Card.Root>

			<!-- Strategic Insights -->
			<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl">
				<Card.Header>
					<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
						<svg class="h-5 w-5 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
						</svg>
						رؤى استراتيجية
					</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-4">
					<!-- Key Insights -->
					<div class="space-y-4">
						<!-- Most Valuable Segment -->
						<div class="p-3 rounded-lg bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-950/30 dark:to-green-950/30 border border-emerald-200/50 dark:border-emerald-800/50">
							<div class="flex items-center gap-2 mb-2">
								<Crown class="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
								<span class="font-semibold text-emerald-800 dark:text-emerald-200">
									الشريحة الأعلى قيمة
								</span>
							</div>
							<p class="text-sm text-emerald-700 dark:text-emerald-300">
								<strong>{mostValuableSegment.name_ar}</strong> يساهم بمتوسط 
								{formatCurrency(mostValuableSegment.avg_spend)} لكل عميل
							</p>
						</div>

						<!-- Most Loyal Segment -->
						<div class="p-3 rounded-lg bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-950/30 dark:to-violet-950/30 border border-purple-200/50 dark:border-purple-800/50">
							<div class="flex items-center gap-2 mb-2">
								<Heart class="h-4 w-4 text-purple-600 dark:text-purple-400" />
								<span class="font-semibold text-purple-800 dark:text-purple-200">
									الأكثر ولاءً
								</span>
							</div>
							<p class="text-sm text-purple-700 dark:text-purple-300">
								<strong>{mostLoyalSegment.name_ar}</strong> لديه أعلى درجة ولاء 
								{mostLoyalSegment.loyalty_score.toFixed(1)}/100
							</p>
						</div>

						<!-- Fastest Growing -->
						{#if fastestGrowingSegment.growth_rate > 0}
							<div class="p-3 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200/50 dark:border-blue-800/50">
								<div class="flex items-center gap-2 mb-2">
									<TrendingUp class="h-4 w-4 text-blue-600 dark:text-blue-400" />
									<span class="font-semibold text-blue-800 dark:text-blue-200">
										الأسرع نمواً
									</span>
								</div>
								<p class="text-sm text-blue-700 dark:text-blue-300">
									<strong>{fastestGrowingSegment.name_ar}</strong> ينمو بمعدل 
									{formatPercentage(fastestGrowingSegment.growth_rate)}
								</p>
							</div>
						{/if}

						<!-- Recommendations -->
						<div class="p-3 rounded-lg bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border border-amber-200/50 dark:border-amber-800/50">
							<div class="flex items-center gap-2 mb-2">
								<svg class="h-4 w-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
								<span class="font-semibold text-amber-800 dark:text-amber-200">
									توصيات
								</span>
							</div>
							<div class="space-y-2 text-sm text-amber-700 dark:text-amber-300">
								<p>• ركز على الاحتفاظ بالعملاء المميزين من خلال برامج الولاء</p>
								<p>• طوّر استراتيجيات لتحويل العملاء الجدد إلى منتظمين</p>
								<p>• أعد تفعيل العملاء غير النشطين بعروض خاصة</p>
							</div>
						</div>
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	{/if}
</div>

<style>
	.customer-segment-wrapper {
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