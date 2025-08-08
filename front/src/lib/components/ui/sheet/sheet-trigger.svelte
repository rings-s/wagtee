<script lang="ts">
	import { Dialog as SheetPrimitive } from "bits-ui";

	type $$Props = SheetPrimitive.TriggerProps;

	let { children, ...restProps }: $$Props = $props();
</script>

<SheetPrimitive.Trigger {...restProps}>
	{@render children?.()}
</SheetPrimitive.Trigger>