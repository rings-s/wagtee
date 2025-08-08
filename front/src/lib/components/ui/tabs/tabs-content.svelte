<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { getContext } from "svelte";

	type Props = {
		value: string;
		class?: string;
		children?: any;
	};

	let { value, class: className, children, ...restProps }: Props = $props();

	const tabsStore = getContext("tabs");
	const isActive = $derived($tabsStore === value);
</script>

{#if isActive}
	<div
		class={cn(
			"mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			className
		)}
		{...restProps}
	>
		{@render children?.()}
	</div>
{/if}