<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { SubscriptionTier } from '$lib/types/index.js';
	import { Button } from '$lib/components/ui/button';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Check, Crown, Star, Zap } from '@lucide/svelte';

	interface Props {
		tier: SubscriptionTier;
		tierKey: string;
		isCurrentTier?: boolean;
		isPopular?: boolean;
		isLoading?: boolean;
	}

	let {
		tier,
		tierKey,
		isCurrentTier = false,
		isPopular = false,
		isLoading = false
	}: Props = $props();

	const dispatch = createEventDispatcher<{
		upgrade: string;
	}>();

	function handleUpgrade() {
		if (!isCurrentTier) {
			dispatch('upgrade', tierKey);
		}
	}

	// Get tier icon
	function getTierIcon(tierKey: string) {
		switch (tierKey) {
			case 'basic':
				return Zap;
			case 'standard':
				return Star;
			case 'premium':
				return Crown;
			default:
				return Zap;
		}
	}

	// Get tier color scheme
	function getTierColors(tierKey: string) {
		switch (tierKey) {
			case 'basic':
				return {
					accent: 'text-blue-600',
					bg: 'bg-blue-50',
					border: 'border-blue-200'
				};
			case 'standard':
				return {
					accent: 'text-purple-600',
					bg: 'bg-purple-50',
					border: 'border-purple-200'
				};
			case 'premium':
				return {
					accent: 'text-amber-600',
					bg: 'bg-amber-50',
					border: 'border-amber-200'
				};
			default:
				return {
					accent: 'text-gray-600',
					bg: 'bg-gray-50',
					border: 'border-gray-200'
				};
		}
	}

	const colors = getTierColors(tierKey);
	const IconComponent = getTierIcon(tierKey);
</script>

<Card 
	class={`relative ${isPopular ? 'ring-2 ring-primary' : ''} ${isCurrentTier ? 'bg-muted/50' : ''}`}
>
	{#if isPopular}
		<div class="absolute -top-3 left-1/2 transform -translate-x-1/2">
			<Badge class="bg-primary text-primary-foreground px-3 py-1">
				Most Popular
			</Badge>
		</div>
	{/if}

	{#if isCurrentTier}
		<div class="absolute top-4 right-4">
			<Badge variant="secondary" class="text-green-600">
				Current Plan
			</Badge>
		</div>
	{/if}

	<CardHeader class="text-center pb-4">
		<div class={`inline-flex items-center justify-center w-12 h-12 rounded-full ${colors.bg} ${colors.border} border mb-4 mx-auto`}>
			<IconComponent class={`h-6 w-6 ${colors.accent}`} />
		</div>
		
		<CardTitle class="text-xl font-semibold">{tier.name}</CardTitle>
		
		<div class="text-3xl font-bold">
			{tier.price} <span class="text-lg font-normal text-muted-foreground">{tier.currency}/month</span>
		</div>
	</CardHeader>

	<CardContent class="space-y-6">
		<!-- Features List -->
		<div class="space-y-3">
			{#each tier.features as feature}
				<div class="flex items-start gap-3">
					<div class="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center mt-0.5">
						<Check class="h-3 w-3 text-green-600" />
					</div>
					<span class="text-sm text-muted-foreground">{feature}</span>
				</div>
			{/each}
		</div>

		<!-- Usage Limits -->
		<div class={`rounded-lg p-4 ${colors.bg} ${colors.border} border`}>
			<h4 class="font-medium text-sm mb-3">Usage Limits</h4>
			<div class="space-y-2 text-sm">
				<div class="flex justify-between">
					<span class="text-muted-foreground">Services:</span>
					<span class="font-medium">
						{tier.limits.max_services === -1 ? 'Unlimited' : tier.limits.max_services}
					</span>
				</div>
				<div class="flex justify-between">
					<span class="text-muted-foreground">Monthly Bookings:</span>
					<span class="font-medium">
						{tier.limits.max_bookings_per_month === -1 ? 'Unlimited' : tier.limits.max_bookings_per_month}
					</span>
				</div>
				<div class="flex justify-between">
					<span class="text-muted-foreground">Customers:</span>
					<span class="font-medium">
						{tier.limits.max_customers === -1 ? 'Unlimited' : tier.limits.max_customers.toLocaleString()}
					</span>
				</div>
			</div>
		</div>

		<!-- Action Button -->
		<div class="pt-4">
			{#if isCurrentTier}
				<Button variant="outline" class="w-full" disabled>
					Current Plan
				</Button>
			{:else}
				<Button 
					class="w-full" 
					disabled={isLoading}
					on:click={handleUpgrade}
				>
					{#if isLoading}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
					{/if}
					Upgrade to {tier.name}
				</Button>
			{/if}
		</div>

		<!-- Billing Note -->
		<div class="text-xs text-center text-muted-foreground">
			Billed monthly • Cancel anytime
		</div>
	</CardContent>
</Card>