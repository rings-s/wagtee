<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Mail, Lock, Eye, EyeOff, AlertCircle } from '@lucide/svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import { goto } from '$app/navigation';
	import type { LoginForm } from '$lib/types/index.js';

	let loginForm: LoginForm = $state({
		email: '',
		password: ''
	});

	let showPassword = $state(false);

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		authStore.clearError();
		
		const result = await authStore.login(loginForm.email, loginForm.password);
		
		if (result.success) {
			// Redirect to dashboard or intended page
			goto('/dashboard');
		}
		// Error is handled by the auth store
	};

	const togglePasswordVisibility = () => {
		showPassword = !showPassword;
	};

	// Email validation
	const validateEmail = (email: string) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	};
</script>

<svelte:head>
	<title>تسجيل الدخول - Wagtee</title>
	<meta name="description" content="تسجيل الدخول إلى منصة Wagtee للحجوزات" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />
	
	<div class="flex items-center justify-center p-4 min-h-[calc(100vh-80px)]">
		<div class="w-full max-w-md space-y-6">

		<Card>
			<CardHeader class="text-center">
				<CardTitle class="text-2xl">تسجيل الدخول</CardTitle>
				<CardDescription>
					أدخل البريد الإلكتروني وكلمة المرور للوصول إلى حسابك
				</CardDescription>
			</CardHeader>
			<CardContent>
				{#if authStore.error}
					<div class="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive">
						<AlertCircle class="h-4 w-4" />
						<span class="text-sm">{authStore.error}</span>
					</div>
				{/if}

				<form onsubmit={handleSubmit} class="space-y-4">
					<!-- Email Field -->
					<div class="space-y-2">
						<Label for="email">البريد الإلكتروني <span class="text-destructive">*</span></Label>
						<div class="relative">
							<Mail class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
							<Input
								id="email"
								type="email"
								placeholder="example@email.com"
								bind:value={loginForm.email}
								class="pl-10 {!validateEmail(loginForm.email) && loginForm.email ? 'border-destructive' : ''}"
								required
								disabled={authStore.isLoading}
							/>
						</div>
						{#if loginForm.email && !validateEmail(loginForm.email)}
							<p class="text-sm text-destructive">يرجى إدخال بريد إلكتروني صحيح</p>
						{/if}
					</div>

					<!-- Password Field -->
					<div class="space-y-2">
						<Label for="password">كلمة المرور <span class="text-destructive">*</span></Label>
						<div class="relative">
							<Lock class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
							<Input
								id="password"
								type={showPassword ? "text" : "password"}
								placeholder="أدخل كلمة المرور"
								bind:value={loginForm.password}
								class="pl-10 pr-10"
								required
								disabled={authStore.isLoading}
							/>
							<button
								type="button"
								onclick={togglePasswordVisibility}
								class="absolute right-3 top-3 h-4 w-4 text-muted-foreground hover:text-foreground"
								disabled={authStore.isLoading}
							>
								{#if showPassword}
									<EyeOff class="h-4 w-4" />
								{:else}
									<Eye class="h-4 w-4" />
								{/if}
							</button>
						</div>
					</div>

					<!-- Submit Button -->
					<Button 
						type="submit" 
						class="w-full h-12 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.01]" 
						disabled={authStore.isLoading || !validateEmail(loginForm.email) || !loginForm.password}
						style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #059669 100%); border: none; color: white;"
					>
						{#if authStore.isLoading}
							<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
						{/if}
						تسجيل الدخول
					</Button>
				</form>

				<!-- Forgot Password -->
				<div class="text-center mt-4">
					<a href="/auth/forgot-password" class="text-sm text-primary hover:underline">
						نسيت كلمة المرور؟
					</a>
				</div>

				<!-- Divider -->
				<div class="relative my-6">
					<div class="absolute inset-0 flex items-center">
						<span class="w-full border-t"></span>
					</div>
					<div class="relative flex justify-center text-xs uppercase">
						<span class="bg-background px-2 text-muted-foreground">أو</span>
					</div>
				</div>

				<!-- Register Link -->
				<div class="text-center">
					<p class="text-sm text-muted-foreground">
						ليس لديك حساب؟
						<a href="/auth/register" class="text-primary hover:underline font-medium">
							إنشاء حساب جديد
						</a>
					</p>
				</div>
			</CardContent>
		</Card>

		<!-- Back to Home -->
		<div class="text-center">
			<a href="/" class="text-sm text-muted-foreground hover:text-foreground">
				← العودة إلى الصفحة الرئيسية
			</a>
		</div>
		</div>
	</div>
</div>