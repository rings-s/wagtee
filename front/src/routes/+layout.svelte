<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { ModeWatcher } from "mode-watcher";
	import ViewTransition from '$lib/components/ViewTransition.svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import { page } from '$app/stores';
	
	let { children } = $props();
	
	// Determine navbar variant based on current route
	let navbarVariant = $derived(() => {
		const pathname = $page.url.pathname;
		
		if (pathname.startsWith('/dashboard')) {
			return 'dashboard';
		} else if (pathname.startsWith('/book/') || pathname === '/book') {
			return 'public';
		} else {
			return 'landing';
		}
	});
	
	// Determine if auth buttons should be shown
	let showAuthButtons = $derived(() => {
		const pathname = $page.url.pathname;
		// Hide auth buttons on auth pages
		return !pathname.startsWith('/auth/');
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="description" content="Wagtee - منصة الحجوزات الرائدة في المملكة العربية السعودية" />
</svelte:head>

<ModeWatcher />
<ViewTransition />

<!-- Show navbar on all pages except auth pages -->
{#if !$page.url.pathname.startsWith('/auth/')}
	<Navbar variant={navbarVariant} showAuthButtons={showAuthButtons} />
{/if}

{@render children?.()}
