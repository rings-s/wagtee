<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type $$Props = {
		class?: string;
		children?: any;
	};

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<div class={cn("flex flex-col space-y-2 text-center sm:text-left", className)} {...restProps}>
	{@render children?.()}
</div>