<!--
  Secure Login Form Component for Wagtee
  Integrates with Django secure JWT authentication
-->
<script lang="ts">
  import { authStore } from '$lib/stores/auth.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '$lib/components/ui/card';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Eye, EyeOff, Loader2, Mail, Lock } from 'lucide-svelte';

  // Form state using Svelte 5 runes
  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let isSubmitting = $state(false);
  let validationErrors = $state<Record<string, string>>({});

  // Get auth state reactively
  let authState = $derived({
    error: authStore.error,
    isLoading: authStore.isLoading
  });

  // Form validation
  function validateForm(): boolean {
    const errors: Record<string, string> = {};

    // Email validation
    if (!email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!password.trim()) {
      errors.password = 'Password is required';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    validationErrors = errors;
    return Object.keys(errors).length === 0;
  }

  // Handle form submission
  async function handleSubmit(event: Event) {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    isSubmitting = true;
    authStore.clearError();

    try {
      const result = await authStore.login(email.trim(), password);
      if (result.success) {
        // Navigation is handled by auth store
        console.log('Login successful');
      } else {
        console.error('Login failed:', result.error);
      }
    } catch (error) {
      console.error('Login failed:', error);
      // Error is handled by auth store
    } finally {
      isSubmitting = false;
    }
  }

  // Clear validation errors when user types
  function clearFieldError(field: string) {
    if (validationErrors[field]) {
      validationErrors = { ...validationErrors };
      delete validationErrors[field];
    }
  }

  // Toggle password visibility
  function togglePasswordVisibility() {
    showPassword = !showPassword;
  }
</script>

<Card class="w-full max-w-md mx-auto">
  <CardHeader class="space-y-1">
    <CardTitle class="text-2xl font-bold text-center">تسجيل الدخول</CardTitle>
    <CardDescription class="text-center text-muted-foreground">
      أدخل بريدك الإلكتروني وكلمة المرور للوصول إلى حسابك
    </CardDescription>
  </CardHeader>
  
  <CardContent>
    <form onsubmit={handleSubmit} class="space-y-4" novalidate>
      <!-- Email Field -->
      <div class="space-y-2">
        <Label for="email">البريد الإلكتروني</Label>
        <div class="relative">
          <Mail class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="email"
            type="email"
            placeholder="admin@wagtee.sa"
            bind:value={email}
            oninput={() => clearFieldError('email')}
            class={`pl-10 ${validationErrors.email ? 'border-destructive' : ''}`}
            disabled={isSubmitting}
            autocomplete="email"
            required
          />
        </div>
        {#if validationErrors.email}
          <p class="text-sm text-destructive">{validationErrors.email}</p>
        {/if}
      </div>

      <!-- Password Field -->
      <div class="space-y-2">
        <Label for="password">كلمة المرور</Label>
        <div class="relative">
          <Lock class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="أدخل كلمة المرور"
            bind:value={password}
            oninput={() => clearFieldError('password')}
            class={`pl-10 pr-10 ${validationErrors.password ? 'border-destructive' : ''}`}
            disabled={isSubmitting}
            autocomplete="current-password"
            required
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            class="absolute right-2 top-1 h-8 w-8 p-0"
            onclick={togglePasswordVisibility}
            disabled={isSubmitting}
          >
            {#if showPassword}
              <EyeOff class="h-4 w-4" />
            {:else}
              <Eye class="h-4 w-4" />
            {/if}
          </Button>
        </div>
        {#if validationErrors.password}
          <p class="text-sm text-destructive">{validationErrors.password}</p>
        {/if}
      </div>

      <!-- Error Alert -->
      {#if authState.error}
        <Alert variant="destructive">
          <AlertDescription>
            {authState.error}
          </AlertDescription>
        </Alert>
      {/if}

      <!-- Submit Button -->
      <Button 
        type="submit" 
        class="w-full" 
        disabled={isSubmitting}
      >
        {#if isSubmitting}
          <Loader2 class="mr-2 h-4 w-4 animate-spin" />
          جاري تسجيل الدخول...
        {:else}
          تسجيل الدخول
        {/if}
      </Button>
    </form>

    <!-- Additional Links -->
    <div class="mt-4 text-center text-sm">
      <p class="text-muted-foreground">
        ليس لديك حساب؟ 
        <a href="/register" class="text-primary hover:underline">
          إنشاء حساب جديد
        </a>
      </p>
      <p class="mt-2">
        <a href="/forgot-password" class="text-primary hover:underline">
          نسيت كلمة المرور؟
        </a>
      </p>
    </div>
  </CardContent>
</Card>

<style>
  /* RTL support for Arabic text */
  :global([dir="rtl"]) .relative input {
    padding-left: 2.5rem;
    padding-right: 0.75rem;
  }

  :global([dir="rtl"]) .absolute.left-3 {
    left: auto;
    right: 0.75rem;
  }

  :global([dir="rtl"]) .absolute.right-2 {
    right: auto;
    left: 0.5rem;
  }
</style>