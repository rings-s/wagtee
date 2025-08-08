<script lang="ts">
	import { Popover as PopoverPrimitive } from "bits-ui";

	type $$Props = PopoverPrimitive.Props;

	let { children, ...restProps }: $$Props = $props();
</script>

<PopoverPrimitive.Root {...restProps}>
	{@render children?.()}
</PopoverPrimitive.Root>