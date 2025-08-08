<script lang="ts">
	import { cn } from "$lib/utils";
	import { User, Crown, Star, Shield, Zap } from "@lucide/svelte";

	let {
		children,
		class: classNames,
		delayMs = 0,
		type = "initials",
		name,
		email,
		userId,
		variant = "default",
		showIcon = false,
		...restProps
	}: {
		children?: import("svelte").Snippet;
		class?: string;
		delayMs?: number;
		type?: "initials" | "icon" | "pattern" | "gradient";
		name?: string;
		email?: string;
		userId?: string | number;
		variant?: "default" | "premium" | "vip" | "minimal";
		showIcon?: boolean;
	} = $props();

	let canRender = $state(delayMs <= 0);

	// Generate initials from name or email
	function getInitials(name?: string, email?: string): string {
		if (name) {
			return name
				.split(' ')
				.slice(0, 2)
				.map(part => part.charAt(0))
				.join('')
				.toUpperCase();
		}
		if (email) {
			return email.charAt(0).toUpperCase();
		}
		return '?';
	}

	// Generate consistent colors based on user data
	function getConsistentColor(str?: string | number): { bg: string; text: string } {
		if (!str) {
			return { bg: 'bg-muted', text: 'text-muted-foreground' };
		}

		const colors = [
			{ bg: 'bg-blue-100', text: 'text-blue-700' },
			{ bg: 'bg-green-100', text: 'text-green-700' },
			{ bg: 'bg-purple-100', text: 'text-purple-700' },
			{ bg: 'bg-pink-100', text: 'text-pink-700' },
			{ bg: 'bg-indigo-100', text: 'text-indigo-700' },
			{ bg: 'bg-orange-100', text: 'text-orange-700' },
			{ bg: 'bg-teal-100', text: 'text-teal-700' },
			{ bg: 'bg-red-100', text: 'text-red-700' },
			{ bg: 'bg-yellow-100', text: 'text-yellow-700' },
			{ bg: 'bg-cyan-100', text: 'text-cyan-700' }
		];

		const hash = String(str).split('').reduce((a, b) => {
			a = ((a << 5) - a) + b.charCodeAt(0);
			return a & a;
		}, 0);

		const index = Math.abs(hash) % colors.length;
		return colors[index];
	}

	// Generate geometric pattern based on user ID
	function generatePattern(id?: string | number): string {
		if (!id) return '';
		
		const seed = String(id);
		const patterns = [
			'radial-gradient(circle at 30% 70%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
			'linear-gradient(45deg, rgba(168, 85, 247, 0.2) 25%, transparent 25%)',
			'conic-gradient(from 0deg, rgba(34, 197, 94, 0.3), transparent)',
			'radial-gradient(ellipse at center, rgba(249, 115, 22, 0.2) 0%, transparent 70%)'
		];
		
		const hash = seed.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
		return patterns[hash % patterns.length];
	}

	// Icon selection based on variant
	function getVariantIcon(variant: string) {
		switch (variant) {
			case 'premium': return Crown;
			case 'vip': return Star;
			default: return User;
		}
	}

	// Set up delay rendering
	if (delayMs > 0) {
		setTimeout(() => {
			canRender = true;
		}, delayMs);
	}

	// Compute derived values
	const initials = $derived(getInitials(name, email));
	const colors = $derived(getConsistentColor(name || email || userId));
	const pattern = $derived(generatePattern(userId));
	const IconComponent = $derived(getVariantIcon(variant));
</script>

{#if canRender}
	<div
		class={cn(
			"flex h-full w-full items-center justify-center rounded-full font-medium transition-all duration-300",
			type === "pattern" && "relative overflow-hidden",
			type === "gradient" && "bg-gradient-to-br from-primary/20 to-secondary/20",
			type === "initials" && colors.bg,
			type === "initials" && colors.text,
			variant === "premium" && "bg-gradient-to-br from-purple-100 to-pink-100 text-purple-700 shadow-inner",
			variant === "vip" && "bg-gradient-to-br from-yellow-100 to-amber-100 text-yellow-800 shadow-inner border border-yellow-200",
			variant === "minimal" && "bg-muted text-muted-foreground",
			classNames
		)}
		{...restProps}
	>
		{#if type === "pattern"}
			<div 
				class="absolute inset-0 opacity-30"
				style="background: {pattern}"
			></div>
			<div class="relative z-10 flex items-center justify-center">
				{#if showIcon}
					<IconComponent class="h-1/2 w-1/2" />
				{:else}
					{initials}
				{/if}
			</div>
		{:else if type === "icon" || showIcon}
			<IconComponent class="h-1/2 w-1/2" />
		{:else if children}
			{@render children()}
		{:else}
			{initials}
		{/if}
	</div>
{/if}