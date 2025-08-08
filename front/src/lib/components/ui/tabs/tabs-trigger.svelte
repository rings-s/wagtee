<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { getContext } from "svelte";

	type Props = {
		value: string;
		class?: string;
		disabled?: boolean;
		children?: any;
	};

	let { value, class: className, disabled = false, children, ...restProps }: Props = $props();

	const tabsStore = getContext("tabs");
	const handleValueChange = getContext("handleValueChange");

	const isActive = $derived($tabsStore === value);

	const handleClick = () => {
		if (!disabled) {
			handleValueChange(value);
		}
	};
</script>

<button
	type="button"
	class={cn(
		"inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
		isActive ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:bg-background/50",
		className
	)}
	{disabled}
	onclick={handleClick}
	{...restProps}
>
	{@render children?.()}
</button>