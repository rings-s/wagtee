<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
	};

	let { class: className, children, ...restProps }: Props = $props();
</script>

<thead class={cn("[&_tr]:border-b", className)} {...restProps}>
	{@render children?.()}
</thead>