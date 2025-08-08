<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import type { ComponentType } from 'svelte';
	import { TrendingUp, TrendingDown, Minus } from '@lucide/svelte';

	interface Props {
		title: string;
		value: string | number;
		change?: number;
		changeLabel?: string;
		icon?: ComponentType;
		loading?: boolean;
		currency?: boolean;
		trend?: 'up' | 'down' | 'neutral';
	}

	let {
		title,
		value,
		change,
		changeLabel,
		icon: IconComponent,
		loading = false,
		currency = false,
		trend = 'neutral'
	}: Props = $props();

	// Format the display value
	function formatValue(val: string | number): string {
		if (loading) return '---';
		
		if (typeof val === 'number') {
			if (currency) {
				return `${val.toLocaleString()} SAR`;
			}
			return val.toLocaleString();
		}
		return val;
	}

	// Get trend icon and color
	function getTrendDisplay(trend: 'up' | 'down' | 'neutral', change?: number) {
		if (!change && change !== 0) {
			return {
				icon: Minus,
				color: 'text-muted-foreground',
				bgColor: 'bg-muted/20'
			};
		}

		switch (trend) {
			case 'up':
				return {
					icon: TrendingUp,
					color: 'text-green-600',
					bgColor: 'bg-green-50'
				};
			case 'down':
				return {
					icon: TrendingDown,
					color: 'text-red-600',
					bgColor: 'bg-red-50'
				};
			default:
				return {
					icon: Minus,
					color: 'text-muted-foreground',
					bgColor: 'bg-muted/20'
				};
		}
	}

	const trendDisplay = getTrendDisplay(trend, change);
	const TrendIcon = trendDisplay.icon;
</script>

<Card>
	<CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
		<CardTitle class="text-sm font-medium text-muted-foreground">
			{title}
		</CardTitle>
		{#if IconComponent}
			<div class="h-4 w-4 text-muted-foreground">
				<IconComponent class="h-4 w-4" />
			</div>
		{/if}
	</CardHeader>
	
	<CardContent>
		<div class="space-y-2">
			<!-- Main Value -->
			<div class="text-2xl font-bold">
				{#if loading}
					<div class="animate-pulse bg-muted rounded h-8 w-20"></div>
				{:else}
					{formatValue(value)}
				{/if}
			</div>

			<!-- Change Indicator -->
			{#if change !== undefined || changeLabel}
				<div class="flex items-center space-x-2">
					{#if change !== undefined}
						<div class={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${trendDisplay.bgColor}`}>
							<TrendIcon class={`h-3 w-3 ${trendDisplay.color}`} />
							<span class={trendDisplay.color}>
								{change > 0 ? '+' : ''}{change}%
							</span>
						</div>
					{/if}
					
					{#if changeLabel}
						<span class="text-xs text-muted-foreground">
							{changeLabel}
						</span>
					{/if}
				</div>
			{/if}
		</div>
	</CardContent>
</Card>