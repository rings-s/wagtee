<!--
  Login Page for Wagtee Frontend
  Uses secure JWT authentication with email-based login
-->
<script lang="ts">
  import LoginForm from '$lib/components/auth/LoginForm.svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  // FIXED: Use Svelte 5 runes properly without onMount
  let authState = $derived({
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user,
    isLoading: authStore.isLoading
  });

  // Handle authentication redirect with effect
  $effect(() => {
    if (authState.isAuthenticated && authState.user && !authState.isLoading) {
      const redirectTo = $page.url.searchParams.get('redirect') || '/dashboard';
      goto(redirectTo);
    }
  });
</script>

<!-- Page metadata -->
<svelte:head>
  <title>تسجيل الدخول | Wagtee - واقتي</title>
  <meta name="description" content="تسجيل الدخول إلى منصة واقتي لإدارة الحجوزات والخدمات" />
</svelte:head>

<!-- Login page content -->
<div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <!-- Logo and branding -->
    <div class="text-center">
      <div class="flex justify-center">
        <div class="w-20 h-20 bg-primary rounded-full flex items-center justify-center">
          <span class="text-2xl font-bold text-primary-foreground">W</span>
        </div>
      </div>
      <h1 class="mt-4 text-3xl font-extrabold text-gray-900 dark:text-white">
        واقتي
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        منصة الحجوزات الذكية للسوق السعودي
      </p>
    </div>

    <!-- Login form -->
    <LoginForm />

    <!-- Demo credentials for development -->
    {#if import.meta.env.DEV}
      <div class="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
          بيانات تجريبية للتطوير
        </h3>
        <div class="space-y-1 text-xs text-blue-700 dark:text-blue-300">
          <p><strong>المدير العام:</strong> admin@wagtee.sa / admin123</p>
          <p><strong>مدير:</strong> manager@wagtee.sa / manager123</p>
          <p><strong>صاحب عمل:</strong> business@wagtee.sa / business123</p>
        </div>
      </div>
    {/if}

    <!-- Footer links -->
    <div class="text-center space-y-2">
      <div class="flex justify-center space-x-4 rtl:space-x-reverse text-sm">
        <a href="/privacy" class="text-primary hover:text-primary/80">
          سياسة الخصوصية
        </a>
        <span class="text-gray-300">|</span>
        <a href="/terms" class="text-primary hover:text-primary/80">
          شروط الاستخدام
        </a>
        <span class="text-gray-300">|</span>
        <a href="/support" class="text-primary hover:text-primary/80">
          الدعم الفني
        </a>
      </div>
      <p class="text-xs text-gray-500">
        © 2025 Wagtee. جميع الحقوق محفوظة.
      </p>
    </div>
  </div>
</div>

<style>
  /* Ensure RTL layout for Arabic content */
  :global(body) {
    direction: rtl;
  }

  /* Override for specific LTR elements if needed */
  :global(.ltr) {
    direction: ltr;
  }
</style>