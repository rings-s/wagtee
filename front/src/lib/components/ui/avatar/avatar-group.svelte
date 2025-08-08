<script lang="ts">
	import { cn } from "$lib/utils";

	type Spacing = "tight" | "normal" | "loose";
	type Direction = "left" | "right";

	let {
		children,
		class: classNames,
		spacing = "normal",
		direction = "left",
		max = 0,
		showCount = true,
		total = 0,
		...restProps
	}: {
		children?: import("svelte").Snippet;
		class?: string;
		spacing?: Spacing;
		direction?: Direction;
		max?: number;
		showCount?: boolean;
		total?: number;
	} = $props();

	// Spacing classes
	const spacingClasses = {
		tight: "-space-x-2",
		normal: "-space-x-1",
		loose: "space-x-1"
	};

	// Direction classes
	const directionClasses = {
		left: "flex-row",
		right: "flex-row-reverse"
	};

	const hasOverflow = $derived(max > 0 && total > max);
	const overflowCount = $derived(hasOverflow ? total - max : 0);
</script>

<div
	class={cn(
		"flex items-center",
		spacingClasses[spacing],
		directionClasses[direction],
		classNames
	)}
	{...restProps}
>
	{@render children?.()}
	
	{#if hasOverflow && showCount}
		<div
			class="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-sm font-medium text-muted-foreground ring-2 ring-background transition-all duration-200 hover:bg-muted/80 hover:scale-105"
		>
			+{overflowCount}
		</div>
	{/if}
</div>