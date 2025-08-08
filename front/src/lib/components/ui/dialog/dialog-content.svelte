<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { getContext } from "svelte";
	import { X } from "@lucide/svelte";
	import { dialogContentVariants, type DialogContentProps } from "./index.js";

	type $$Props = DialogContentProps;

	let { 
		class: className, 
		variant = "default",
		size = "default",
		showCloseButton = true,
		closeOnBackdropClick = true,
		closeOnEscape = true,
		children, 
		...restProps 
	}: $$Props = $props();

	const dialog = getContext("dialog");

	// Reactive state using Svelte 5 runes
	let isAnimating = $state(false);
	let contentElement = $state<HTMLDivElement>();

	// Animation states
	let isClosing = $state(false);

	const handleClose = () => {
		if (!closeOnEscape && !closeOnBackdropClick) return;
		
		isClosing = true;
		setTimeout(() => {
			dialog.setOpen(false);
			isClosing = false;
		}, 200);
	};

	const handleBackdropClick = (e: MouseEvent) => {
		if (!closeOnBackdropClick) return;
		if (e.target === e.currentTarget) {
			handleClose();
		}
	};

	const handleKeydown = (e: KeyboardEvent) => {
		if (!closeOnEscape) return;
		if (e.key === 'Escape') {
			handleClose();
		}
	};

	// Focus trap effect
	$effect(() => {
		if (dialog.open() && contentElement) {
			const focusableElements = contentElement.querySelectorAll(
				'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
			);
			const firstFocusable = focusableElements[0] as HTMLElement;
			const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement;

			const handleTabKey = (e: KeyboardEvent) => {
				if (e.key === 'Tab') {
					if (e.shiftKey) {
						if (document.activeElement === firstFocusable) {
							e.preventDefault();
							lastFocusable?.focus();
						}
					} else {
						if (document.activeElement === lastFocusable) {
							e.preventDefault();
							firstFocusable?.focus();
						}
					}
				}
			};

			document.addEventListener('keydown', handleTabKey);
			firstFocusable?.focus();

			return () => {
				document.removeEventListener('keydown', handleTabKey);
			};
		}
	});
</script>

{#if dialog.open()}
	<!-- Backdrop with enhanced blur and animation -->
	<div 
		class={cn(
			"fixed inset-0 z-50 transition-all duration-300",
			"bg-background/60 backdrop-blur-md",
			variant === "glass" && "backdrop-blur-xl bg-background/40",
			variant === "dark" && "bg-black/60",
			isClosing ? "opacity-0 backdrop-blur-none" : "opacity-100"
		)}
		onclick={handleBackdropClick}
		onkeydown={handleKeydown}
		role="dialog"
		aria-modal="true"
	>
		<!-- Dialog Content with enhanced animations -->
		<div 
			bind:this={contentElement}
			class={cn(
				dialogContentVariants({ variant, size }),
				"fixed left-[50%] top-[50%] z-50 translate-x-[-50%] translate-y-[-50%]",
				"transition-all duration-300 ease-out",
				isClosing 
					? "opacity-0 scale-95 translate-y-[-48%]" 
					: "opacity-100 scale-100 translate-y-[-50%] animate-scale-in"
			)}
		>
			<div
				class={cn("relative w-full h-full", className)}
				{...restProps}
			>
				<!-- Enhanced Close Button -->
				{#if showCloseButton}
					<button
						onclick={handleClose}
						class={cn(
							"absolute right-4 top-4 z-10 rounded-full p-2",
							"bg-background/80 backdrop-blur-sm border border-border/50",
							"opacity-70 ring-offset-background transition-all duration-200",
							"hover:opacity-100 hover:bg-background hover:scale-110",
							"focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
							"active:scale-95"
						)}
					>
						<X class="h-4 w-4" />
						<span class="sr-only">Close</span>
					</button>
				{/if}

				{@render children?.()}
			</div>
		</div>
	</div>
{/if}