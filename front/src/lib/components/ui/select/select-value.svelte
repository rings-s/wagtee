<script lang="ts">
	import { Select as SelectPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/index.js";

	type $$Props = SelectPrimitive.ValueProps & {
		class?: string;
	};

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<SelectPrimitive.Value class={cn("text-sm", className)} {...restProps}>
	{@render children?.()}
</SelectPrimitive.Value>