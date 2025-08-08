<script lang="ts">
	import { cn } from "$lib/utils";
	import { onMount } from "svelte";

	let {
		src,
		alt = "",
		class: classNames,
		loading: imageLoading = "lazy",
		onLoad,
		onError,
		...restProps
	}: {
		src?: string;
		alt?: string;
		class?: string;
		loading?: "lazy" | "eager";
		onLoad?: () => void;
		onError?: () => void;
	} = $props();

	let imageElement = $state<HTMLImageElement>();
	let imageLoaded = $state(false);
	let imageError = $state(false);
	let isLoading = $state(true);

	// Handle image load/error states
	function handleLoad() {
		imageLoaded = true;
		isLoading = false;
		imageError = false;
		onLoad?.();
	}

	function handleError() {
		imageError = true;
		isLoading = false;
		imageLoaded = false;
		onError?.();
	}

	// Reset states when src changes
	$effect(() => {
		if (src) {
			isLoading = true;
			imageLoaded = false;
			imageError = false;
		}
	});

	onMount(() => {
		// If image is already cached, it might load immediately
		if (imageElement && imageElement.complete) {
			if (imageElement.naturalWidth > 0) {
				handleLoad();
			} else {
				handleError();
			}
		}
	});
</script>

{#if src && !imageError}
	<img
		bind:this={imageElement}
		{src}
		{alt}
		loading={imageLoading}
		class={cn(
			"aspect-square h-full w-full object-cover transition-all duration-300",
			isLoading && "opacity-0 scale-95",
			imageLoaded && "opacity-100 scale-100",
			imageError && "opacity-0",
			classNames
		)}
		onload={handleLoad}
		onerror={handleError}
		{...restProps}
	/>
	
	{#if isLoading}
		<div class="absolute inset-0 flex items-center justify-center bg-muted/50 animate-pulse">
			<div class="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent"></div>
		</div>
	{/if}
{/if}