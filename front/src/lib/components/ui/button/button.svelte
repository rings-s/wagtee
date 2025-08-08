<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { buttonVariants, type Props, type Events } from "./index.js";
	
	type $$Props = Props;
	type $$Events = Events;

	let {
		class: className,
		variant = "default",
		size = "default",
		loading = false,
		loadingText = "Loading...",
		disabled = false,
		children,
		leftIcon,
		rightIcon,
		ripple = false,
		href,
		target,
		onclick,
		...restProps
	}: $$Props = $props();

	// Reactive state using Svelte 5 runes
	let isPressed = $state(false);
	let ripples = $state<Array<{id: number, x: number, y: number}>>([]);
	let buttonElement = $state<HTMLButtonElement>();

	// Computed disabled state
	let isDisabled = $derived(disabled || loading);

	// Ripple effect function
	const createRipple = (event: MouseEvent) => {
		if (!ripple || !buttonElement) return;
		
		const rect = buttonElement.getBoundingClientRect();
		const x = event.clientX - rect.left;
		const y = event.clientY - rect.top;
		const id = Date.now() + Math.random();
		
		ripples = [...ripples, { id, x, y }];
		
		// Remove ripple after animation
		setTimeout(() => {
			ripples = ripples.filter(r => r.id !== id);
		}, 600);
	};

	// Enhanced click handler
	const handleClick = (event: MouseEvent) => {
		if (isDisabled) return;
		
		isPressed = true;
		setTimeout(() => isPressed = false, 150);
		
		if (ripple) {
			createRipple(event);
		}
		
		onclick?.(event);
	};

	// Loading spinner component
	const LoadingSpinner = () => `
		<svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
			<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
		</svg>
	`;
</script>

{#if href}
<a
	{href}
	{target}
	class={cn(buttonVariants({ variant, size, loading, className }))}
	onclick={handleClick}
	{...restProps}
>
	<!-- Ripple effects -->
	{#if ripple}
		{#each ripples as ripple (ripple.id)}
			<span
				class="absolute rounded-full bg-white/30 pointer-events-none animate-ping"
				style="left: {ripple.x - 10}px; top: {ripple.y - 10}px; width: 20px; height: 20px;"
			></span>
		{/each}
	{/if}

	<!-- Content -->
	<span class="flex items-center justify-center gap-2">
		<!-- Left icon or loading spinner -->
		{#if loading}
			<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
		{:else if leftIcon}
			{@render leftIcon()}
		{/if}

		<!-- Button text -->
		<span class={loading ? "opacity-75" : ""}>
			{#if loading && loadingText}
				{loadingText}
			{:else}
				{@render children?.()}
			{/if}
		</span>

		<!-- Right icon -->
		{#if rightIcon && !loading}
			{@render rightIcon()}
		{/if}
	</span>
</a>
{:else}
<button
	bind:this={buttonElement}
	class={cn(buttonVariants({ variant, size, loading, className }))}
	disabled={isDisabled}
	onclick={handleClick}
	{...restProps}
>
	<!-- Ripple effects -->
	{#if ripple}
		{#each ripples as ripple (ripple.id)}
			<span
				class="absolute rounded-full bg-white/30 pointer-events-none animate-ping"
				style="left: {ripple.x - 10}px; top: {ripple.y - 10}px; width: 20px; height: 20px;"
			></span>
		{/each}
	{/if}

	<!-- Content -->
	<span class="flex items-center justify-center gap-2">
		<!-- Left icon or loading spinner -->
		{#if loading}
			<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
		{:else if leftIcon}
			{@render leftIcon()}
		{/if}

		<!-- Button text -->
		<span class={loading ? "opacity-75" : ""}>
			{#if loading && loadingText}
				{loadingText}
			{:else}
				{@render children?.()}
			{/if}
		</span>

		<!-- Right icon -->
		{#if rightIcon && !loading}
			{@render rightIcon()}
		{/if}
	</span>
</button>
{/if}