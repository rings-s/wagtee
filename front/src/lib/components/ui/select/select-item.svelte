<script lang="ts">
	import { Select as SelectPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/index.js";

	type $$Props = SelectPrimitive.ItemProps & {
		class?: string;
	};

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<SelectPrimitive.Item
	class={cn(
		"relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none data-[disabled]:pointer-events-none data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground data-[disabled]:opacity-50",
		className
	)}
	{...restProps}
>
	<span class="absolute left-2 flex size-3.5 items-center justify-center">
		<SelectPrimitive.ItemIndicator>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="size-4"
			>
				<path d="M20 6 9 17l-5-5" />
			</svg>
		</SelectPrimitive.ItemIndicator>
	</span>
	<SelectPrimitive.ItemText>
		{@render children?.()}
	</SelectPrimitive.ItemText>
</SelectPrimitive.Item>