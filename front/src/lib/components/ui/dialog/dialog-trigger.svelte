<script lang="ts">
	import { getContext } from "svelte";

	type Props = {
		children?: any;
		asChild?: boolean;
	};

	let { children, asChild = false }: Props = $props();

	const dialog = getContext("dialog");

	const handleClick = () => {
		dialog.setOpen(true);
	};
</script>

{#if asChild}
	{@render children?.({ onClick: handleClick })}
{:else}
	<button onclick={handleClick}>
		{@render children?.()}
	</button>
{/if}