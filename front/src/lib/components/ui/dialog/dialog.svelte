<script lang="ts">
	import { setContext } from "svelte";

	type Props = {
		open?: boolean;
		onOpenChange?: (open: boolean) => void;
		children?: any;
	};

	let { 
		open = $bindable(false), 
		onOpenChange,
		children 
	}: Props = $props();

	const handleOpenChange = (newOpen: boolean) => {
		open = newOpen;
		onOpenChange?.(newOpen);
	};

	setContext("dialog", {
		open: () => open,
		setOpen: handleOpenChange
	});
</script>

{@render children?.()}