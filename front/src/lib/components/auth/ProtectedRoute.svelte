<!--
  Protected Route Component for Role-Based Access Control
  Integrates with secure JWT authentication and role system
-->
<script lang="ts">
  import { authStore } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  import { Loader2 } from 'lucide-svelte';
  import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
  import { Button } from '$lib/components/ui/button';

  // Props using Svelte 5 runes
  interface Props {
    requiredRoles?: string[];
    requireAuth?: boolean;
    requireSubscription?: boolean;
    fallbackPath?: string;
    children: import('svelte').Snippet;
  }

  let {
    requiredRoles = [],
    requireAuth = true,
    requireSubscription = false,
    fallbackPath = '/login',
    children
  }: Props = $props();

  // State
  let isChecking = $state(true);
  let hasAccess = $state(false);
  let accessError = $state<string | null>(null);

  // Get auth state reactively
  let authState = $derived({
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user,
    isLoading: authStore.isLoading,
    isSubscriptionActive: authStore.isSubscriptionActive
  });

  // React to auth state changes
  $effect(() => {
    checkAccess();
  });

  // Check access permissions
  function checkAccess() {
    if (authState.isLoading) {
      isChecking = true;
      return;
    }

    isChecking = false;
    hasAccess = false;
    accessError = null;

    // Check authentication requirement
    if (requireAuth && !authState.isAuthenticated) {
      accessError = 'يجب تسجيل الدخول للوصول إلى هذه الصفحة';
      goto(fallbackPath);
      return;
    }

    // If no auth required and user is not authenticated, allow access
    if (!requireAuth && !authState.isAuthenticated) {
      hasAccess = true;
      return;
    }

    // Check role requirements
    if (requiredRoles.length > 0 && authState.user) {
      const userHasRole = requiredRoles.includes(authState.user.role);
      if (!userHasRole) {
        accessError = `غير مسموح لك بالوصول إلى هذه الصفحة. الأدوار المطلوبة: ${requiredRoles.join(', ')}`;
        return;
      }
    }

    // Check subscription requirement
    if (requireSubscription && authState.user) {
      if (!authState.isSubscriptionActive) {
        accessError = 'يتطلب الوصول إلى هذه الصفحة اشتراكاً نشطاً';
        goto('/subscription');
        return;
      }
    }

    // All checks passed
    hasAccess = true;
  }

  // Handle navigation to fallback
  function handleGoToFallback() {
    goto(fallbackPath);
  }

  // Handle subscription redirect
  function handleGoToSubscription() {
    goto('/subscription');
  }

  // FIXED: Removed onMount - effect already handles initialization
</script>

{#if isChecking}
  <!-- Loading State -->
  <div class="flex items-center justify-center min-h-[400px]">
    <div class="text-center space-y-4">
      <Loader2 class="h-8 w-8 animate-spin mx-auto" />
      <p class="text-muted-foreground">جاري التحقق من صلاحيات الوصول...</p>
    </div>
  </div>

{:else if accessError}
  <!-- Access Denied -->
  <div class="flex items-center justify-center min-h-[400px] p-4">
    <div class="max-w-md w-full">
      <Alert variant="destructive">
        <AlertTitle>غير مسموح بالوصول</AlertTitle>
        <AlertDescription class="mt-2">
          {accessError}
        </AlertDescription>
      </Alert>
      
      <div class="mt-4 flex gap-2 justify-center">
        {#if !authState.isAuthenticated}
          <Button onclick={handleGoToFallback}>
            تسجيل الدخول
          </Button>
        {:else if requireSubscription && !authState.isSubscriptionActive}
          <Button onclick={handleGoToSubscription}>
            الاشتراك
          </Button>
        {:else}
          <Button variant="outline" onclick={() => goto('/dashboard')}>
            العودة إلى الرئيسية
          </Button>
        {/if}
      </div>
    </div>
  </div>

{:else if hasAccess}
  <!-- Render protected content -->
  {@render children()}

{:else}
  <!-- Fallback for unexpected states -->
  <div class="flex items-center justify-center min-h-[400px]">
    <div class="text-center space-y-4">
      <p class="text-muted-foreground">حدث خطأ في التحقق من صلاحيات الوصول</p>
      <Button variant="outline" onclick={handleGoToFallback}>
        المحاولة مرة أخرى
      </Button>
    </div>
  </div>
{/if}

<!--
Usage Examples:

Basic authentication required:
<ProtectedRoute>
  <div>Protected content here</div>
</ProtectedRoute>

Admin only access:
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
  <div>Admin content here</div>
</ProtectedRoute>

Subscription required:
<ProtectedRoute requireSubscription={true}>
  <div>Premium content here</div>
</ProtectedRoute>

Business owner with subscription:
<ProtectedRoute 
  requiredRoles={['business_owner']} 
  requireSubscription={true}
>
  <div>Business owner premium content</div>
</ProtectedRoute>

Public route (no auth required):
<ProtectedRoute requireAuth={false}>
  <div>Public content here</div>
</ProtectedRoute>
-->