<script lang="ts">
	import { Calendar as CalendarPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/index.js";
	import type { Snippet } from "svelte";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = CalendarPrimitive.Props & {
		class?: string;
	};

	let {
		class: className,
		placeholder,
		weekdayFormat = "short",
		...restProps
	}: $$Props = $props();
</script>

<CalendarPrimitive.Root
	class={cn("p-3", className)}
	{weekdayFormat}
	{placeholder}
	{...restProps}
>
	{#snippet children({ months, weekdays })}
		<CalendarPrimitive.Header class="flex w-full items-center justify-between">
			<CalendarPrimitive.PrevButton
				class="inline-flex size-10 items-center justify-center whitespace-nowrap rounded-md border border-input bg-background text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="size-4"
				>
					<path d="m15 18-6-6 6-6" />
				</svg>
			</CalendarPrimitive.PrevButton>
			<CalendarPrimitive.Heading class="text-sm font-medium" />
			<CalendarPrimitive.NextButton
				class="inline-flex size-10 items-center justify-center whitespace-nowrap rounded-md border border-input bg-background text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="size-4"
				>
					<path d="m9 18 6-6-6-6" />
				</svg>
			</CalendarPrimitive.NextButton>
		</CalendarPrimitive.Header>
		<div class="flex flex-col space-y-4 pt-4 sm:flex-row sm:space-x-4 sm:space-y-0">
			{#each months as month}
				<CalendarPrimitive.Grid class="w-full border-collapse select-none space-y-1">
					<CalendarPrimitive.GridHead>
						<CalendarPrimitive.GridRow class="mb-1 flex w-full justify-between">
							{#each weekdays as day}
								<CalendarPrimitive.HeadCell
									class="w-10 rounded-md text-[0.8rem] font-normal text-muted-foreground"
								>
									<div>{day.slice(0, 2)}</div>
								</CalendarPrimitive.HeadCell>
							{/each}
						</CalendarPrimitive.GridRow>
					</CalendarPrimitive.GridHead>
					<CalendarPrimitive.GridBody>
						{#each month.weeks as weekDates}
							<CalendarPrimitive.GridRow class="mt-2 flex w-full justify-between">
								{#each weekDates as date}
									<CalendarPrimitive.Cell
										{date}
										class="relative size-10 !p-0 text-center text-sm focus-within:relative focus-within:z-20 [&:has([data-selected])]:bg-accent [&:has([data-selected][data-outside-month])]:bg-accent/50"
									>
										<CalendarPrimitive.Day
											{date}
											class="inline-flex size-10 items-center justify-center whitespace-nowrap rounded-md p-0 text-sm font-normal ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[disabled]:text-muted-foreground data-[outside-month]:text-muted-foreground data-[selected]:bg-primary data-[selected]:text-primary-foreground data-[selected]:opacity-100"
										/>
									</CalendarPrimitive.Cell>
								{/each}
							</CalendarPrimitive.GridRow>
						{/each}
					</CalendarPrimitive.GridBody>
				</CalendarPrimitive.Grid>
			{/each}
		</div>
	{/snippet}
</CalendarPrimitive.Root>