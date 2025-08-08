<script lang="ts">
	import { Dialog as SheetPrimitive } from "bits-ui";

	type $$Props = SheetPrimitive.Props;

	let { children, ...restProps }: $$Props = $props();
</script>

<SheetPrimitive.Root {...restProps}>
	{@render children?.()}
</SheetPrimitive.Root>