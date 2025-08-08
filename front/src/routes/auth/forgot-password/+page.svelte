<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Mail, AlertCircle, CheckCircle, ArrowLeft } from '@lucide/svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import type { PasswordResetRequestForm } from '$lib/types/index.js';

	let resetForm: PasswordResetRequestForm = $state({
		email: ''
	});

	let emailSent = $state(false);

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		authStore.clearError();
		
		const result = await authStore.requestPasswordReset(resetForm.email);
		
		if (result.success) {
			emailSent = true;
		}
		// Error is handled by the auth store
	};

	// Email validation
	const validateEmail = (email: string) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	};
</script>

<svelte:head>
	<title>إعادة تعيين كلمة المرور - Wagtee</title>
	<meta name="description" content="طلب إعادة تعيين كلمة المرور" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />
	
	<div class="flex items-center justify-center p-4 min-h-[calc(100vh-80px)]">
		<div class="w-full max-w-md space-y-6">

		<Card>
			<CardHeader class="text-center">
				<CardTitle class="text-2xl">إعادة تعيين كلمة المرور</CardTitle>
				<CardDescription>
					{#if !emailSent}
						أدخل بريدك الإلكتروني وسنرسل لك رابط إعادة تعيين كلمة المرور
					{:else}
						تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني
					{/if}
				</CardDescription>
			</CardHeader>
			<CardContent>
				{#if !emailSent}
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
									bind:value={resetForm.email}
									class="pl-10 {!validateEmail(resetForm.email) && resetForm.email ? 'border-destructive' : ''}"
									required
									disabled={authStore.isLoading}
								/>
							</div>
							{#if resetForm.email && !validateEmail(resetForm.email)}
								<p class="text-sm text-destructive">يرجى إدخال بريد إلكتروني صحيح</p>
							{/if}
						</div>

						<!-- Submit Button -->
						<Button 
							type="submit" 
							class="w-full h-12 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.01]" 
							disabled={authStore.isLoading || !validateEmail(resetForm.email)}
							style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #059669 100%); border: none; color: white;"
						>
							{#if authStore.isLoading}
								<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
							{/if}
							إرسال رابط إعادة التعيين
						</Button>
					</form>
				{:else}
					<!-- Success Message -->
					<div class="mb-4 p-4 bg-success/10 border border-success/20 rounded-md flex items-center gap-3 text-success">
						<CheckCircle class="h-5 w-5 flex-shrink-0" />
						<div>
							<p class="font-medium">تم إرسال البريد الإلكتروني بنجاح!</p>
							<p class="text-sm mt-1">يرجى فحص بريدك الإلكتروني واتباع التعليمات لإعادة تعيين كلمة المرور.</p>
						</div>
					</div>

					<!-- Resend Button -->
					<Button 
						variant="outline" 
						class="w-full mb-4" 
						onclick={() => { emailSent = false; authStore.clearError(); }}
					>
						إرسال مرة أخرى
					</Button>
				{/if}

				<!-- Back to Login -->
				<div class="text-center">
					<a href="/auth/login" class="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
						<ArrowLeft class="h-4 w-4" />
						العودة إلى تسجيل الدخول
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