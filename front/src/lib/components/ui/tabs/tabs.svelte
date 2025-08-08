<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { setContext } from "svelte";
	import { writable } from "svelte/store";

	type Props = {
		value?: string;
		defaultValue?: string;
		class?: string;
		children?: any;
		onValueChange?: (value: string) => void;
	};

	let {
		value = $bindable(),
		defaultValue = "",
		class: className,
		children,
		onValueChange,
		...restProps
	}: Props = $props();

	// Initialize value if not provided
	if (value === undefined) {
		value = defaultValue;
	}

	const tabsStore = writable(value || defaultValue);
	setContext("tabs", tabsStore);

	// Update store when value changes
	$effect(() => {
		tabsStore.set(value || defaultValue);
	});

	// Handle tab change
	const handleValueChange = (newValue: string) => {
		value = newValue;
		tabsStore.set(newValue);
		onValueChange?.(newValue);
	};

	setContext("handleValueChange", handleValueChange);
</script>

<div
	class={cn("", className)}
	{...restProps}
>
	{@render children?.()}
</div>