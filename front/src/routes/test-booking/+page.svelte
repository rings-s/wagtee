<script lang="ts">
	import BookingManager from '$lib/components/business/BookingManager.svelte';
	import { Toaster } from '$lib/components/ui/sonner';
</script>

<svelte:head>
	<title>اختبار إدارة الحجوزات</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto p-4">
		<div class="mb-6">
			<h1 class="text-3xl font-bold text-center mb-2">اختبار إدارة الحجوزات</h1>
			<p class="text-center text-gray-600">
				هذه صفحة اختبار للتأكد من عمل مكون إدارة الحجوزات بشكل صحيح
			</p>
		</div>
		
		<BookingManager />
	</div>
</div>

<!-- Toast notifications -->
<Toaster />

<style>
	:global(body) {
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		direction: rtl;
	}
</style>