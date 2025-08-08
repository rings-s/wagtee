<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
	};

	let { class: className, children, ...restProps }: Props = $props();
</script>

<div class={cn("flex items-center p-6 pt-0", className)} {...restProps}>
	{@render children?.()}
</div>