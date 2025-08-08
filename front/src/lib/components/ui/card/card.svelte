<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { cardVariants, type Props } from "./index.js";

	type $$Props = Props;

	let {
		class: className,
		variant = "default",
		interactive = false,
		hover = false,
		children,
		onclick,
		...restProps
	}: $$Props = $props();

	// Reactive state using Svelte 5 runes
	let isHovered = $state(false);
	let isPressed = $state(false);

	// Computed classes
	let interactiveClasses = $derived(() => {
		if (!interactive) return "";
		return `cursor-pointer select-none ${isPressed ? "scale-98" : ""} ${
			isHovered ? "transform transition-all duration-200" : ""
		}`;
	});

	// Event handlers
	const handleMouseEnter = () => {
		if (interactive || hover) isHovered = true;
	};

	const handleMouseLeave = () => {
		if (interactive || hover) {
			isHovered = false;
			isPressed = false;
		}
	};

	const handleMouseDown = () => {
		if (interactive) isPressed = true;
	};

	const handleMouseUp = () => {
		if (interactive) isPressed = false;
	};

	const handleClick = (event: MouseEvent) => {
		if (interactive && onclick) {
			onclick(event);
		}
	};
</script>

<div
	class={cn(cardVariants({ variant }), interactiveClasses, className)}
	onmouseenter={handleMouseEnter}
	onmouseleave={handleMouseLeave}
	onmousedown={handleMouseDown}
	onmouseup={handleMouseUp}
	onclick={handleClick}
	role={interactive ? "button" : undefined}
	tabindex={interactive ? 0 : undefined}
	{...restProps}
>
	{@render children?.()}
</div>