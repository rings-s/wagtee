<script lang="ts">
	import { cn } from "$lib/utils";

	type Variant = "default" | "destructive" | "warning" | "success" | "info";

	let {
		children,
		class: classNames,
		variant = "default",
		...restProps
	}: {
		children?: import("svelte").Snippet;
		class?: string;
		variant?: Variant;
	} = $props();

	// Variant classes
	const variantClasses = {
		default: "bg-background text-foreground",
		destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
		warning: "border-yellow-500/50 text-yellow-800 bg-yellow-50 dark:border-yellow-500 dark:text-yellow-300 dark:bg-yellow-950/30 [&>svg]:text-yellow-600 dark:[&>svg]:text-yellow-300",
		success: "border-green-500/50 text-green-800 bg-green-50 dark:border-green-500 dark:text-green-300 dark:bg-green-950/30 [&>svg]:text-green-600 dark:[&>svg]:text-green-300",
		info: "border-blue-500/50 text-blue-800 bg-blue-50 dark:border-blue-500 dark:text-blue-300 dark:bg-blue-950/30 [&>svg]:text-blue-600 dark:[&>svg]:text-blue-300"
	};
</script>

<div
	class={cn(
		"relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
		variantClasses[variant],
		classNames
	)}
	role="alert"
	{...restProps}
>
	{@render children?.()}
</div>