<script lang="ts">
	import { cn } from "$lib/utils";

	let {
		children,
		class: classNames,
		...restProps
	}: {
		children?: import("svelte").Snippet;
		class?: string;
	} = $props();
</script>

<div
	class={cn("text-sm [&_p]:leading-relaxed", classNames)}
	{...restProps}
>
	{@render children?.()}
</div>