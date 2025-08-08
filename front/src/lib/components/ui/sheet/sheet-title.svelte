<script lang="ts">
	import { Dialog as SheetPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/index.js";

	type $$Props = SheetPrimitive.TitleProps & {
		class?: string;
	};

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<SheetPrimitive.Title class={cn("text-lg font-semibold text-foreground", className)} {...restProps}>
	{@render children?.()}
</SheetPrimitive.Title>