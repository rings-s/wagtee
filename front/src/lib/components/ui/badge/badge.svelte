<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { badgeVariants, type Props } from "./index.js";
	
	type $$Props = Props;

	let {
		class: className,
		variant = "default",
		size = "default",
		interactive = false,
		notification = false,
		count,
		dot = false,
		children,
		leftIcon,
		rightIcon,
		onclick,
		...restProps
	}: $$Props = $props();

	// Reactive state using Svelte 5 runes
	let isPressed = $state(false);

	// Display count or dot indicator
	let shouldShowCount = $derived(count !== undefined && count > 0);
	let displayCount = $derived(() => {
		if (!count) return "";
		return count > 99 ? "99+" : count.toString();
	});

	// Event handlers
	const handleClick = (event: MouseEvent) => {
		if (!interactive) return;
		
		isPressed = true;
		setTimeout(() => isPressed = false, 150);
		
		onclick?.(event);
	};

	const handleKeyDown = (event: KeyboardEvent) => {
		if (!interactive) return;
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			handleClick(event as any);
		}
	};
</script>

<div
	class={cn(
		badgeVariants({ variant, size, interactive, notification }),
		isPressed && interactive && "scale-90",
		className
	)}
	onclick={handleClick}
	onkeydown={handleKeyDown}
	role={interactive ? "button" : undefined}
	tabindex={interactive ? 0 : undefined}
	{...restProps}
>
	<!-- Left icon -->
	{#if leftIcon}
		<span class="mr-1 -ml-0.5">
			{@render leftIcon()}
		</span>
	{/if}

	<!-- Dot indicator -->
	{#if dot}
		<div class="w-2 h-2 rounded-full bg-current opacity-75 mr-1.5"></div>
	{/if}

	<!-- Badge content -->
	<span class="flex items-center gap-1">
		{@render children?.()}
		
		<!-- Count indicator -->
		{#if shouldShowCount}
			<span class="inline-flex items-center justify-center min-w-[1rem] h-4 text-xs font-bold rounded-full bg-destructive text-destructive-foreground -mr-1 ml-1">
				{displayCount}
			</span>
		{/if}
	</span>

	<!-- Right icon -->
	{#if rightIcon}
		<span class="ml-1 -mr-0.5">
			{@render rightIcon()}
		</span>
	{/if}

	<!-- Notification pulse indicator -->
	{#if notification}
		<span class="absolute -top-1 -right-1 h-3 w3 rounded-full bg-destructive animate-ping"></span>
		<span class="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-destructive"></span>
	{/if}
</div>