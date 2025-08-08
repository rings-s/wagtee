<script lang="ts">
	import { cn } from "$lib/utils";

	type Size = "xs" | "sm" | "default" | "lg" | "xl" | "2xl" | "3xl";
	type Variant = "default" | "secondary" | "success" | "warning" | "danger" | "premium" | "vip";
	type Status = "none" | "online" | "offline" | "busy" | "away";

	let {
		children,
		class: classNames,
		size = "default",
		variant = "default",
		status = "none",
		clickable = false,
		loading = false,
		...restProps
	}: {
		children?: import("svelte").Snippet;
		class?: string;
		size?: Size;
		variant?: Variant;
		status?: Status;
		clickable?: boolean;
		loading?: boolean;
	} = $props();

	// Size classes
	const sizeClasses = {
		xs: "h-6 w-6 text-xs",
		sm: "h-8 w-8 text-sm",
		default: "h-10 w-10 text-base",
		lg: "h-12 w-12 text-lg",
		xl: "h-16 w-16 text-xl",
		"2xl": "h-20 w-20 text-2xl",
		"3xl": "h-24 w-24 text-3xl"
	};

	// Variant classes
	const variantClasses = {
		default: "bg-gradient-to-br from-primary/10 to-primary/5",
		secondary: "bg-gradient-to-br from-secondary/20 to-secondary/10",
		success: "bg-gradient-to-br from-green-100 to-green-50 ring-green-200",
		warning: "bg-gradient-to-br from-yellow-100 to-yellow-50 ring-yellow-200",
		danger: "bg-gradient-to-br from-red-100 to-red-50 ring-red-200",
		premium: "bg-gradient-to-br from-purple-100 via-pink-50 to-indigo-100 ring-purple-200 shadow-md",
		vip: "bg-gradient-to-br from-yellow-100 via-amber-50 to-orange-100 ring-yellow-300 shadow-lg border border-yellow-200"
	};

	// Status classes
	const statusClasses = {
		none: "",
		online: "after:absolute after:bottom-0 after:right-0 after:h-3 after:w-3 after:rounded-full after:bg-green-500 after:ring-2 after:ring-white after:content-['']",
		offline: "after:absolute after:bottom-0 after:right-0 after:h-3 after:w-3 after:rounded-full after:bg-gray-400 after:ring-2 after:ring-white after:content-['']",
		busy: "after:absolute after:bottom-0 after:right-0 after:h-3 after:w-3 after:rounded-full after:bg-red-500 after:ring-2 after:ring-white after:content-['']",
		away: "after:absolute after:bottom-0 after:right-0 after:h-3 after:w-3 after:rounded-full after:bg-yellow-500 after:ring-2 after:ring-white after:content-['']"
	};

	const avatarClass = $derived(
		cn(
			"relative flex shrink-0 overflow-hidden rounded-full transition-all duration-300 hover:shadow-lg hover:scale-105 ring-2 ring-transparent hover:ring-primary/20",
			sizeClasses[size],
			variantClasses[variant],
			statusClasses[status],
			clickable && "cursor-pointer hover:shadow-xl transform-gpu",
			loading && "animate-pulse",
			classNames
		)
	);
</script>

<div
	class={avatarClass}
	role={clickable ? "button" : undefined}
	tabindex={clickable ? 0 : undefined}
	{...restProps}
>
	{#if loading}
		<div class="absolute inset-0 flex items-center justify-center">
			<div class="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
		</div>
	{:else}
		{@render children?.()}
	{/if}
</div>