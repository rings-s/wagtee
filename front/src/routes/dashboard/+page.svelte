<script lang="ts">
	// Clean dashboard implementation using PremiumDashboard
	import PremiumDashboard from '$lib/components/business/PremiumDashboard.svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	// Reactive auth state with Svelte 5 runes
	let authState = $derived({
		user: authStore.user,
		isAuthenticated: authStore.isAuthenticated,
		isLoading: authStore.isLoading,
		error: authStore.error
	});

	// Redirect if not authenticated
	$effect(() => {
		if (!authState.isAuthenticated && !authState.isLoading) {
			goto('/auth/login');
		}
	});
</script>

<svelte:head>
	<title>لوحة التحكم - Wagtee</title>
	<meta name="description" content="لوحة تحكم إدارة الأعمال المتقدمة في منصة Wagtee" />
</svelte:head>

{#if !authState.isAuthenticated}
	<!-- Loading state while checking authentication -->
	<div class="flex min-h-screen items-center justify-center bg-background">
		<div class="space-y-4 text-center">
			<div class="relative">
				<div class="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary/20 border-t-primary"></div>
				<div class="absolute inset-0 mx-auto h-12 w-12 animate-spin rounded-full border-4 border-transparent border-l-primary/40" style="animation-delay: -0.3s;"></div>
			</div>
			<div class="space-y-1">
				<p class="font-medium text-muted-foreground">جار التحقق من الهوية</p>
				<p class="text-xs text-muted-foreground">يرجى الانتظار...</p>
			</div>
		</div>
	</div>
{:else}
	<!-- Premium Dashboard Component -->
	<PremiumDashboard />
{/if}