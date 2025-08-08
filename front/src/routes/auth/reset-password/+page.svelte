<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Lock, Eye, EyeOff, AlertCircle, CheckCircle } from '@lucide/svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import type { PasswordResetConfirmForm } from '$lib/types/index.js';

	let resetForm: PasswordResetConfirmForm = $state({
		email: $page.url.searchParams.get('email') || '',
		token: $page.url.searchParams.get('token') || '',
		new_password: '',
		confirm_password: ''
	});

	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let resetSuccess = $state(false);

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		authStore.clearError();
		
		// Validate passwords match
		if (resetForm.new_password !== resetForm.confirm_password) {
			authStore.clearError();
			// Set error manually (you might want to add this to auth store)
			return;
		}
		
		const result = await authStore.confirmPasswordReset(
			resetForm.email,
			resetForm.token,
			resetForm.new_password,
			resetForm.confirm_password
		);
		
		if (result.success) {
			resetSuccess = true;
			// Redirect to login after 3 seconds
			setTimeout(() => {
				goto('/auth/login?reset=success');
			}, 3000);
		}
		// Error is handled by the auth store
	};

	const togglePasswordVisibility = () => {
		showPassword = !showPassword;
	};

	const toggleConfirmPasswordVisibility = () => {
		showConfirmPassword = !showConfirmPassword;
	};

	// Password validation
	const validatePassword = (password: string) => {
		return password.length >= 8;
	};

	const passwordsMatch = $derived(
		resetForm.new_password === resetForm.confirm_password && resetForm.confirm_password !== ''
	);

	// Check if token and email are present
	const isValidResetLink = $derived(resetForm.email && resetForm.token);
</script>

<svelte:head>
	<title>تأكيد إعادة تعيين كلمة المرور - Wagtee</title>
	<meta name="description" content="تأكيد إعادة تعيين كلمة المرور الجديدة" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />
	
	<div class="flex items-center justify-center p-4 min-h-[calc(100vh-80px)]">
		<div class="w-full max-w-md space-y-6">

		<Card>
			<CardHeader class="text-center">
				<CardTitle class="text-2xl">تعيين كلمة مرور جديدة</CardTitle>
				<CardDescription>
					{#if !resetSuccess}
						أدخل كلمة المرور الجديدة لحسابك
					{:else}
						تم تعيين كلمة المرور بنجاح!
					{/if}
				</CardDescription>
			</CardHeader>
			<CardContent>
				{#if !isValidResetLink}
					<!-- Invalid or expired link -->
					<div class="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-3 text-destructive">
						<AlertCircle class="h-5 w-5 flex-shrink-0" />
						<div>
							<p class="font-medium">رابط غير صحيح أو منتهي الصلاحية</p>
							<p class="text-sm mt-1">يرجى طلب رابط جديد لإعادة تعيين كلمة المرور.</p>
						</div>
					</div>

					<Button 
						variant="outline" 
						class="w-full" 
						onclick={() => goto('/auth/forgot-password')}
					>
						طلب رابط جديد
					</Button>
				{:else if !resetSuccess}
					{#if authStore.error}
						<div class="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive">
							<AlertCircle class="h-4 w-4" />
							<span class="text-sm">{authStore.error}</span>
						</div>
					{/if}

					<form onsubmit={handleSubmit} class="space-y-4">
						<!-- New Password Field -->
						<div class="space-y-2">
							<Label for="new_password">كلمة المرور الجديدة <span class="text-destructive">*</span></Label>
							<div class="relative">
								<Lock class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								<Input
									id="new_password"
									type={showPassword ? "text" : "password"}
									placeholder="أدخل كلمة المرور الجديدة"
									bind:value={resetForm.new_password}
									class="pl-10 pr-10 {!validatePassword(resetForm.new_password) && resetForm.new_password ? 'border-destructive' : ''}"
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
							{#if resetForm.new_password && !validatePassword(resetForm.new_password)}
								<p class="text-sm text-destructive">كلمة المرور يجب أن تكون 8 أحرف على الأقل</p>
							{/if}
						</div>

						<!-- Confirm Password Field -->
						<div class="space-y-2">
							<Label for="confirm_password">تأكيد كلمة المرور <span class="text-destructive">*</span></Label>
							<div class="relative">
								<Lock class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								<Input
									id="confirm_password"
									type={showConfirmPassword ? "text" : "password"}
									placeholder="أعد إدخال كلمة المرور"
									bind:value={resetForm.confirm_password}
									class="pl-10 pr-10 {resetForm.confirm_password && !passwordsMatch ? 'border-destructive' : ''}"
									required
									disabled={authStore.isLoading}
								/>
								<button
									type="button"
									onclick={toggleConfirmPasswordVisibility}
									class="absolute right-3 top-3 h-4 w-4 text-muted-foreground hover:text-foreground"
									disabled={authStore.isLoading}
								>
									{#if showConfirmPassword}
										<EyeOff class="h-4 w-4" />
									{:else}
										<Eye class="h-4 w-4" />
									{/if}
								</button>
							</div>
							{#if resetForm.confirm_password && !passwordsMatch}
								<p class="text-sm text-destructive">كلمات المرور غير متطابقة</p>
							{/if}
						</div>

						<!-- Submit Button -->
						<Button 
							type="submit" 
							class="w-full h-12 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.01]" 
							disabled={authStore.isLoading || !validatePassword(resetForm.new_password) || !passwordsMatch}
							style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #059669 100%); border: none; color: white;"
						>
							{#if authStore.isLoading}
								<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
							{/if}
							تأكيد كلمة المرور الجديدة
						</Button>
					</form>
				{:else}
					<!-- Success Message -->
					<div class="mb-4 p-4 bg-success/10 border border-success/20 rounded-md flex items-center gap-3 text-success">
						<CheckCircle class="h-5 w-5 flex-shrink-0" />
						<div>
							<p class="font-medium">تم تعيين كلمة المرور بنجاح!</p>
							<p class="text-sm mt-1">سيتم توجيهك إلى صفحة تسجيل الدخول خلال ثوانٍ...</p>
						</div>
					</div>

					<Button 
						class="w-full" 
						onclick={() => goto('/auth/login')}
					>
						تسجيل الدخول الآن
					</Button>
				{/if}

				<!-- Back to Login -->
				<div class="text-center mt-4">
					<a href="/auth/login" class="text-sm text-muted-foreground hover:text-foreground">
						← العودة إلى تسجيل الدخول
					</a>
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