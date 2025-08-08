<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
	};

	let { class: className, children, ...restProps }: Props = $props();
</script>

<caption
	class={cn("mt-4 text-sm text-muted-foreground", className)}
	{...restProps}
>
	{@render children?.()}
</caption>