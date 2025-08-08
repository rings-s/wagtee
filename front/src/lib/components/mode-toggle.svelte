<script lang="ts">
	import { Sun, Moon } from "@lucide/svelte";
	import { browser } from '$app/environment';

	// FIXED: Use Svelte 5 runes with proper lifecycle management
	let isDark = $state(false);

	// Check for saved theme or system preference
	$effect(() => {
		if (!browser) return;
		
		const savedTheme = localStorage.getItem('theme');
		const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		
		isDark = savedTheme === 'dark' || (!savedTheme && systemDark);
		applyTheme(isDark);
	});

	const applyTheme = (dark: boolean) => {
		if (!browser) return;
		
		if (dark) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	};

	const toggleMode = () => {
		if (!browser) return;
		
		isDark = !isDark;
		localStorage.setItem('theme', isDark ? 'dark' : 'light');
		applyTheme(isDark);
	};
</script>

<button
	class="inline-flex items-center justify-center rounded-md w-9 h-9 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
	onclick={toggleMode}
	aria-label="Toggle theme"
>
	{#if isDark}
		<Moon class="h-4 w-4" />
	{:else}
		<Sun class="h-4 w-4" />
	{/if}
</button>