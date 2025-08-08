<script lang="ts">
	import { cn } from "$lib/utils/index.js";

	type Props = {
		class?: string;
		children?: any;
		sortable?: boolean;
		sortDirection?: 'asc' | 'desc' | null;
		onSort?: () => void;
	};

	let { 
		class: className, 
		children, 
		sortable = false,
		sortDirection = null,
		onSort,
		...restProps 
	}: Props = $props();
</script>

<th
	class={cn(
		"h-12 px-4 text-right align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",
		sortable && "cursor-pointer hover:bg-muted/50",
		className
	)}
	onclick={sortable ? onSort : undefined}
	{...restProps}
>
	<div class="flex items-center gap-2">
		{@render children?.()}
		{#if sortable}
			<div class="flex flex-col">
				<div class="w-0 h-0 border-x-2 border-x-transparent border-b-2 {sortDirection === 'asc' ? 'border-b-foreground' : 'border-b-muted-foreground/50'}"></div>
				<div class="w-0 h-0 border-x-2 border-x-transparent border-t-2 {sortDirection === 'desc' ? 'border-t-foreground' : 'border-t-muted-foreground/50'}"></div>
			</div>
		{/if}
	</div>
</th>