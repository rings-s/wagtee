<script lang="ts">
	import { cn } from "$lib/utils/index.js";
	import { inputVariants, type Props } from "./index.js";

	type $$Props = Props;

	let {
		class: className,
		variant = "default",
		size = "default",
		type = "text",
		value = $bindable(),
		label,
		error,
		success,
		helperText,
		placeholder,
		disabled = false,
		readonly = false,
		required = false,
		floatingLabel = false,
		leftIcon,
		rightIcon,
		...restProps
	}: $$Props = $props();

	// Reactive state using Svelte 5 runes
	let isFocused = $state(false);
	let inputElement = $state<HTMLInputElement>();
	
	// Computed states
	let hasValue = $derived(value && value.length > 0);
	let shouldFloatLabel = $derived(floatingLabel && (isFocused || hasValue));
	let hasError = $derived(!!error);
	let hasSuccess = $derived(!!success);
	
	// Input state for styling
	let inputState = $derived(() => {
		if (hasError) return "error";
		if (hasSuccess) return "success";
		if (isFocused) return "focused";
		return "default";
	});

	// Event handlers
	const handleFocus = (event: FocusEvent) => {
		isFocused = true;
	};

	const handleBlur = (event: FocusEvent) => {
		isFocused = false;
	};

	// Generate unique ID for accessibility
	const inputId = `input-${Math.random().toString(36).substr(2, 9)}`;
</script>

<div class="relative w-full">
	<!-- Floating Label -->
	{#if floatingLabel && label}
		<label
			for={inputId}
			class={cn(
				"absolute left-3 transition-all duration-200 pointer-events-none text-muted-foreground",
				shouldFloatLabel 
					? "top-2 text-xs font-medium text-foreground" 
					: "top-1/2 -translate-y-1/2 text-sm",
				hasError && "text-destructive",
				hasSuccess && "text-success"
			)}
		>
			{label}
			{#if required}
				<span class="text-destructive ml-1">*</span>
			{/if}
		</label>
	{/if}

	<!-- Input wrapper for icons -->
	<div class="relative">
		<!-- Left icon -->
		{#if leftIcon}
			<div class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
				{@render leftIcon()}
			</div>
		{/if}

		<!-- Input field -->
		<input
			bind:this={inputElement}
			bind:value
			{type}
			id={inputId}
			placeholder={floatingLabel ? "" : placeholder}
			{disabled}
			{readonly}
			{required}
			class={cn(
				inputVariants({ variant, size, state: inputState }),
				leftIcon && "pl-10",
				rightIcon && "pr-10",
				floatingLabel && label && "pt-6 pb-2",
				className
			)}
			onfocus={handleFocus}
			onblur={handleBlur}
			{...restProps}
		/>

		<!-- Right icon -->
		{#if rightIcon}
			<div class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
				{@render rightIcon()}
			</div>
		{/if}

		<!-- Success/Error icons -->
		{#if hasSuccess && !rightIcon}
			<div class="absolute right-3 top-1/2 -translate-y-1/2 text-success">
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
				</svg>
			</div>
		{:else if hasError && !rightIcon}
			<div class="absolute right-3 top-1/2 -translate-y-1/2 text-destructive">
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
				</svg>
			</div>
		{/if}
	</div>

	<!-- Regular label (non-floating) -->
	{#if !floatingLabel && label}
		<label for={inputId} class="block text-sm font-medium text-foreground mb-2">
			{label}
			{#if required}
				<span class="text-destructive ml-1">*</span>
			{/if}
		</label>
	{/if}

	<!-- Helper text, error, or success message -->
	{#if error || success || helperText}
		<div class="mt-2 text-xs">
			{#if error}
				<p class="text-destructive">{error}</p>
			{:else if success}
				<p class="text-success">{success}</p>
			{:else if helperText}
				<p class="text-muted-foreground">{helperText}</p>
			{/if}
		</div>
	{/if}
</div>