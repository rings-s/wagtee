<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
		tag?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
	};

	let { class: className, children, tag = "h3", ...restProps }: Props = $props();
</script>

<svelte:element
	this={tag}
	class={cn("text-2xl font-semibold leading-none tracking-tight", className)}
	{...restProps}
>
	{@render children?.()}
</svelte:element>