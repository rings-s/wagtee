<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Mail, Shield, AlertCircle, CheckCircle, ArrowLeft } from '@lucide/svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import type { EmailVerificationForm } from '$lib/types/index.js';

	let verificationForm: EmailVerificationForm = $state({
		email: $page.url.searchParams.get('email') || '',
		verification_code: ''
	});

	let verificationSuccess = $state(false);
	let codeSent = $state(false);

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		authStore.clearError();
		
		const result = await authStore.verifyEmail(verificationForm.email, verificationForm.verification_code);
		
		if (result.success) {
			verificationSuccess = true;
			// Redirect to login after 3 seconds
			setTimeout(() => {
				goto('/auth/login?verified=true');
			}, 3000);
		}
		// Error is handled by the auth store
	};

	const handleResendCode = async () => {
		authStore.clearError();
		
		const result = await authStore.sendEmailVerification(verificationForm.email);
		
		if (result.success) {
			codeSent = true;
			// Reset the flag after 3 seconds
			setTimeout(() => {
				codeSent = false;
			}, 3000);
		}
	};

	// Email validation
	const validateEmail = (email: string) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	};

	// Verification code validation (6 digits)
	const validateCode = (code: string) => {
		return /^\d{6}$/.test(code);
	};

	// Auto-format verification code
	const handleCodeInput = (e: Event) => {
		const target = e.target as HTMLInputElement;
		let value = target.value.replace(/\D/g, ''); // Remove non-digits
		if (value.length > 6) value = value.slice(0, 6); // Max 6 digits
		verificationForm.verification_code = value;
	};
</script>

<svelte:head>
	<title>التحقق من البريد الإلكتروني - Wagtee</title>
	<meta name="description" content="التحقق من البريد الإلكتروني لتفعيل الحساب" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />
	
	<div class="flex items-center justify-center p-4 min-h-[calc(100vh-80px)]">
		<div class="w-full max-w-md space-y-6">

		<Card>
			<CardHeader class="text-center">
				<CardTitle class="text-2xl">التحقق من البريد الإلكتروني</CardTitle>
				<CardDescription>
					{#if !verificationSuccess}
						أدخل رمز التحقق المرسل إلى بريدك الإلكتروني
					{:else}
						تم التحقق من بريدك الإلكتروني بنجاح!
					{/if}
				</CardDescription>
			</CardHeader>
			<CardContent>
				{#if !verificationSuccess}
					{#if authStore.error}
						<div class="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive">
							<AlertCircle class="h-4 w-4" />
							<span class="text-sm">{authStore.error}</span>
						</div>
					{/if}

					{#if codeSent}
						<div class="mb-4 p-3 bg-success/10 border border-success/20 rounded-md flex items-center gap-2 text-success">
							<CheckCircle class="h-4 w-4" />
							<span class="text-sm">تم إرسال رمز التحقق إلى بريدك الإلكتروني</span>
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
									bind:value={verificationForm.email}
									class="pl-10 {!validateEmail(verificationForm.email) && verificationForm.email ? 'border-destructive' : ''}"
									required
									disabled={authStore.isLoading}
								/>
							</div>
							{#if verificationForm.email && !validateEmail(verificationForm.email)}
								<p class="text-sm text-destructive">يرجى إدخال بريد إلكتروني صحيح</p>
							{/if}
						</div>

						<!-- Verification Code Field -->
						<div class="space-y-2">
							<Label for="verification_code">رمز التحقق <span class="text-destructive">*</span></Label>
							<div class="relative">
								<Shield class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
								<Input
									id="verification_code"
									type="text"
									placeholder="123456"
									bind:value={verificationForm.verification_code}
									oninput={handleCodeInput}
									class="pl-10 text-center tracking-widest font-mono text-lg {!validateCode(verificationForm.verification_code) && verificationForm.verification_code ? 'border-destructive' : ''}"
									maxlength="6"
									required
									disabled={authStore.isLoading}
								/>
							</div>
							{#if verificationForm.verification_code && !validateCode(verificationForm.verification_code)}
								<p class="text-sm text-destructive">رمز التحقق يجب أن يكون 6 أرقام</p>
							{/if}
						</div>

						<!-- Submit Button -->
						<Button 
							type="submit" 
							class="w-full h-12 font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.01]" 
							disabled={authStore.isLoading || !validateEmail(verificationForm.email) || !validateCode(verificationForm.verification_code)}
							style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 50%, #059669 100%); border: none; color: white;"
						>
							{#if authStore.isLoading}
								<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
							{/if}
							تأكيد التحقق
						</Button>
					</form>

					<!-- Resend Code -->
					<div class="text-center mt-4 space-y-2">
						<p class="text-sm text-muted-foreground">لم تتلق رمز التحقق؟</p>
						<Button 
							variant="outline" 
							size="sm"
							onclick={handleResendCode}
							disabled={authStore.isLoading || !validateEmail(verificationForm.email)}
						>
							{#if authStore.isLoading}
								<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
							{/if}
							إرسال مرة أخرى
						</Button>
					</div>
				{:else}
					<!-- Success Message -->
					<div class="mb-4 p-4 bg-success/10 border border-success/20 rounded-md flex items-center gap-3 text-success">
						<CheckCircle class="h-5 w-5 flex-shrink-0" />
						<div>
							<p class="font-medium">تم التحقق من البريد الإلكتروني بنجاح!</p>
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