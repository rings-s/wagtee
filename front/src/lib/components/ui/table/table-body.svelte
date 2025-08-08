<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
	};

	let { class: className, children, ...restProps }: Props = $props();
</script>

<tbody class={cn("[&_tr:last-child]:border-0", className)} {...restProps}>
	{@render children?.()}
</tbody>