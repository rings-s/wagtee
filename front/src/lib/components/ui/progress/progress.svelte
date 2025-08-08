<script lang="ts">
	import { cn } from "$lib/utils";

	let {
		value = $bindable(0),
		max = 100,
		class: className,
		...restProps
	}: {
		value?: number;
		max?: number;
		class?: string;
	} = $props();

	const percentage = $derived(Math.min(Math.max((value / max) * 100, 0), 100));
</script>

<div
	class={cn(
		"relative h-2 w-full overflow-hidden rounded-full bg-primary/20",
		className
	)}
	{...restProps}
>
	<div
		class="h-full w-full flex-1 bg-primary transition-all duration-500 ease-out progress-bar"
		style="transform: translateX(-{100 - percentage}%)"
	/>
</div>