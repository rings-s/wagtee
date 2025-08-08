<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Phone, Lock, User, Building, MapPin, Eye, EyeOff, Mail, AlertCircle, CheckCircle, ArrowLeft } from '@lucide/svelte';
	import Navbar from '$lib/components/navbar.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	import { goto } from '$app/navigation';
	import type { RegisterForm, ServiceType } from '$lib/types/index.js';

	let registerForm: RegisterForm = $state({
		username: '',
		email: '',
		first_name: '',
		last_name: '',
		phone_number: '',
		password: '',
		confirm_password: '',
		role: 'business_owner',
		business_name: '',
		service_type: 'barber',
		address: '',
		address_ar: '',
		city: '',
		district: '',
		cr_number: '',
		vat_number: '',
		terms_accepted: false
	});

	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let currentStep = $state(1); // 1: Account Info, 2: Business Info, 3: Review & Submit
	let isSubmitting = $state(false);

	const serviceTypes: { value: ServiceType; label: string; label_ar: string }[] = [
		{ value: 'barber', label: 'Barber', label_ar: 'حلاق' },
		{ value: 'salon', label: 'Hair Salon', label_ar: 'صالون تجميل' },
		{ value: 'beauty_center', label: 'Beauty Center', label_ar: 'مركز تجميل' },
		{ value: 'car_wash', label: 'Car Wash', label_ar: 'غسيل السيارات' },
		{ value: 'cleaning', label: 'Cleaning Center', label_ar: 'مركز تنظيف' },
		{ value: 'gym', label: 'Gym', label_ar: 'صالة رياضية' },
		{ value: 'photographer', label: 'Photographer', label_ar: 'مصور' },
		{ value: 'makeup_artist', label: 'Makeup Artist', label_ar: 'فنان مكياج' },
		{ value: 'bazar', label: 'Bazar', label_ar: 'بازار' },
		{ value: 'events', label: 'Events', label_ar: 'فعاليات' }
	];

	const userRoles = [
		{ value: 'business_owner', label: 'صاحب عمل', label_en: 'Business Owner', description: 'إدارة عمل تجاري واحد' },
		{ value: 'admin', label: 'مدير', label_en: 'Admin', description: 'إدارة عدة أعمال تجارية' },
		{ value: 'super_admin', label: 'مدير عام', label_en: 'Super Admin', description: 'صلاحيات كاملة للنظام' }
	];

	const saudiCities = [
		'الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر', 
		'تبوك', 'بريدة', 'خميس مشيط', 'حائل', 'نجران', 'الجبيل', 'الطائف', 'ينبع'
	];

	// Email validation
	const validateEmail = (email: string) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	};

	// Saudi phone number validation
	const validatePhoneNumber = (phone: string) => {
		const saudiPhoneRegex = /^\+966[0-9]{9}$/;
		return saudiPhoneRegex.test(phone);
	};

	// Format phone number as user types
	const formatPhoneNumber = (phone: string) => {
		const digits = phone.replace(/\D/g, '');
		
		if (digits.startsWith('966')) {
			return '+' + digits;
		}
		
		if (digits.startsWith('05')) {
			return '+966' + digits.substring(2);
		}
		
		if (digits.startsWith('5')) {
			return '+966' + digits;
		}
		
		return phone;
	};

	const handlePhoneInput = (e: Event) => {
		const target = e.target as HTMLInputElement;
		const formatted = formatPhoneNumber(target.value);
		registerForm.phone_number = formatted;
	};

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		authStore.clearError();
		
		if (currentStep === 1) {
			// Validate step 1
			if (!step1Valid) {
				return;
			}
			currentStep = 2;
			return;
		}

		if (currentStep === 2) {
			// Validate step 2
			if (!step2Valid) {
				return;
			}
			currentStep = 3;
			return;
		}

		if (currentStep === 3) {
			// Final validation and submit
			if (!step3Valid) {
				return;
			}

			isSubmitting = true;
			
			try {
				const result = await authStore.register(registerForm);
				
				if (result.success) {
					// Redirect to dashboard or email verification page
					goto('/dashboard');
				}
			} catch (error) {
				console.error('Registration error:', error);
			} finally {
				isSubmitting = false;
			}
		}
	};

	const goToPreviousStep = () => {
		if (currentStep > 1) {
			currentStep--;
		}
	};

	// Reactive validation
	const step1Valid = $derived(
		registerForm.username.trim().length > 0 && 
		registerForm.first_name.trim().length > 0 && 
		registerForm.last_name.trim().length > 0 && 
		validateEmail(registerForm.email) && 
		validatePhoneNumber(registerForm.phone_number) && 
		registerForm.password.length >= 8 && 
		registerForm.password === registerForm.confirm_password && 
		registerForm.role
	);

	const step2Valid = $derived(
		registerForm.business_name.trim().length > 0 && 
		registerForm.service_type && 
		registerForm.city && 
		registerForm.district.trim().length > 0 && 
		registerForm.address.trim().length > 0
	);

	const step3Valid = $derived(registerForm.terms_accepted);

	const getStepTitle = (step: number) => {
		switch (step) {
			case 1: return 'معلومات الحساب الأساسية';
			case 2: return 'معلومات العمل التجاري';
			case 3: return 'مراجعة وتأكيد البيانات';
			default: return '';
		}
	};
</script>

<svelte:head>
	<title>إنشاء حساب جديد - Wagtee</title>
	<meta name="description" content="إنشاء حساب جديد في منصة Wagtee للحجوزات" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50/30 via-background to-purple-50/30 dark:from-blue-950/10 dark:via-background dark:to-purple-950/10">
	<Navbar variant="landing" />
	
	<div class="flex items-center justify-center p-6 min-h-[calc(100vh-80px)]">
		<div class="w-full max-w-lg space-y-8 relative">
			<!-- Background effects -->
			<div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-100/20 dark:bg-blue-900/10 rounded-full blur-3xl"></div>
			<div class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-100/20 dark:bg-purple-900/10 rounded-full blur-3xl"></div>

		<Card class="card-premium relative z-10 border-0 shadow-2xl">
			<CardHeader class="text-center pb-8 pt-8">
				<CardTitle class="text-3xl font-bold mb-3">إنشاء حساب جديد</CardTitle>
				<CardDescription class="text-lg">
					{getStepTitle(currentStep)}
				</CardDescription>
				
				<!-- Progress Indicator -->
				<div class="flex justify-center mt-8">
					<div class="flex space-x-3">
						<div class="w-10 h-3 rounded-full transition-all duration-500 {currentStep >= 1 ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : 'bg-border'}"></div>
						<div class="w-10 h-3 rounded-full transition-all duration-500 {currentStep >= 2 ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : 'bg-border'}"></div>
						<div class="w-10 h-3 rounded-full transition-all duration-500 {currentStep >= 3 ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg' : 'bg-border'}"></div>
					</div>
				</div>
				<p class="text-sm text-muted-foreground mt-3 font-medium">خطوة {currentStep} من 3</p>
			</CardHeader>
			
			<CardContent class="px-8 pb-8">
				{#if authStore.error}
					<div class="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-center gap-3 text-destructive">
						<AlertCircle class="h-5 w-5 flex-shrink-0" />
						<span class="text-sm font-medium">{authStore.error}</span>
					</div>
				{/if}

				<form onsubmit={handleSubmit} class="space-y-6">
					{#if currentStep === 1}
						<!-- Step 1: Account Information -->
						
						<!-- Username Field -->
						<div class="space-y-3">
							<Label for="username" class="text-sm font-semibold">اسم المستخدم <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<User class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="username"
									type="text"
									placeholder="أدخل اسم المستخدم"
									bind:value={registerForm.username}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
								/>
							</div>
						</div>

						<!-- Email Field -->
						<div class="space-y-3">
							<Label for="email" class="text-sm font-semibold">البريد الإلكتروني <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<Mail class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="email"
									type="email"
									placeholder="example@domain.com"
									bind:value={registerForm.email}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300 {!validateEmail(registerForm.email) && registerForm.email ? 'border-destructive' : ''}"
									required
									disabled={isSubmitting}
								/>
							</div>
							{#if registerForm.email && !validateEmail(registerForm.email)}
								<p class="text-sm text-destructive">يرجى إدخال بريد إلكتروني صحيح</p>
							{/if}
						</div>

						<!-- First Name Field -->
						<div class="space-y-3">
							<Label for="first-name" class="text-sm font-semibold">الاسم الأول <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<User class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="first-name"
									type="text"
									placeholder="أدخل الاسم الأول"
									bind:value={registerForm.first_name}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
								/>
							</div>
						</div>

						<!-- Last Name Field -->
						<div class="space-y-3">
							<Label for="last-name" class="text-sm font-semibold">اسم العائلة <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<User class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="last-name"
									type="text"
									placeholder="أدخل اسم العائلة"
									bind:value={registerForm.last_name}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
								/>
							</div>
						</div>

						<!-- Phone Number Field -->
						<div class="space-y-3">
							<Label for="phone" class="text-sm font-semibold">رقم الهاتف <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<Phone class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="phone"
									type="tel"
									placeholder="+966xxxxxxxxx"
									bind:value={registerForm.phone_number}
									oninput={handlePhoneInput}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300 {!validatePhoneNumber(registerForm.phone_number) && registerForm.phone_number ? 'border-destructive' : ''}"
									required
									disabled={isSubmitting}
								/>
							</div>
							{#if registerForm.phone_number && !validatePhoneNumber(registerForm.phone_number)}
								<p class="text-sm text-destructive">رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx</p>
							{/if}
						</div>

						<!-- Password Field -->
						<div class="space-y-3">
							<Label for="password" class="text-sm font-semibold">كلمة المرور <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<Lock class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="password"
									type={showPassword ? "text" : "password"}
									placeholder="أدخل كلمة المرور (8 أحرف على الأقل)"
									bind:value={registerForm.password}
									class="pl-12 pr-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
									minlength="8"
								/>
								<button
									type="button"
									onclick={() => showPassword = !showPassword}
									class="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground hover:text-primary transition-colors"
									disabled={isSubmitting}
								>
									{#if showPassword}
										<EyeOff class="h-5 w-5" />
									{:else}
										<Eye class="h-5 w-5" />
									{/if}
								</button>
							</div>
							{#if registerForm.password.length > 0 && registerForm.password.length < 8}
								<p class="text-sm text-destructive">كلمة المرور يجب أن تكون 8 أحرف على الأقل</p>
							{/if}
						</div>

						<!-- Confirm Password Field -->
						<div class="space-y-3">
							<Label for="confirm-password" class="text-sm font-semibold">تأكيد كلمة المرور <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<Lock class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="confirm-password"
									type={showConfirmPassword ? "text" : "password"}
									placeholder="أعد إدخال كلمة المرور"
									bind:value={registerForm.confirm_password}
									class="pl-12 pr-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300 {registerForm.confirm_password && registerForm.password !== registerForm.confirm_password ? 'border-destructive' : ''}"
									required
									disabled={isSubmitting}
								/>
								<button
									type="button"
									onclick={() => showConfirmPassword = !showConfirmPassword}
									class="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground hover:text-primary transition-colors"
									disabled={isSubmitting}
								>
									{#if showConfirmPassword}
										<EyeOff class="h-5 w-5" />
									{:else}
										<Eye class="h-5 w-5" />
									{/if}
								</button>
							</div>
							{#if registerForm.confirm_password && registerForm.password !== registerForm.confirm_password}
								<p class="text-sm text-destructive">كلمات المرور غير متطابقة</p>
							{/if}
						</div>

						<!-- Role Selection Field -->
						<div class="space-y-3">
							<Label for="role" class="text-sm font-semibold">نوع الحساب <span class="text-destructive">*</span></Label>
							<select
								id="role"
								bind:value={registerForm.role}
								class="flex h-12 w-full rounded-xl border border-input bg-card/50 backdrop-blur-sm px-4 py-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-all duration-300 hover:bg-card/70"
								required
								disabled={isSubmitting}
							>
								{#each userRoles as role}
									<option value={role.value}>{role.label} - {role.description}</option>
								{/each}
							</select>
							<p class="text-xs text-muted-foreground mt-2">
								اختر نوع الحساب المناسب لاحتياجاتك
							</p>
						</div>

					{:else if currentStep === 2}
						<!-- Step 2: Business Information -->
						
						<!-- Business Name -->
						<div class="space-y-3">
							<Label for="business-name" class="text-sm font-semibold">اسم العمل التجاري <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<Building class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="business-name"
									type="text"
									placeholder="أدخل اسم العمل التجاري"
									bind:value={registerForm.business_name}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
								/>
							</div>
						</div>

						<!-- Service Type -->
						<div class="space-y-3">
							<Label for="service-type" class="text-sm font-semibold">نوع الخدمة <span class="text-destructive">*</span></Label>
							<select
								id="service-type"
								bind:value={registerForm.service_type}
								class="flex h-12 w-full rounded-xl border border-input bg-card/50 backdrop-blur-sm px-4 py-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-all duration-300"
								required
								disabled={isSubmitting}
							>
								{#each serviceTypes as serviceType}
									<option value={serviceType.value}>{serviceType.label_ar}</option>
								{/each}
							</select>
						</div>

						<!-- City -->
						<div class="space-y-3">
							<Label for="city" class="text-sm font-semibold">المدينة <span class="text-destructive">*</span></Label>
							<select
								id="city"
								bind:value={registerForm.city}
								class="flex h-12 w-full rounded-xl border border-input bg-card/50 backdrop-blur-sm px-4 py-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-all duration-300"
								required
								disabled={isSubmitting}
							>
								<option value="">اختر المدينة</option>
								{#each saudiCities as city}
									<option value={city}>{city}</option>
								{/each}
							</select>
						</div>

						<!-- District -->
						<div class="space-y-3">
							<Label for="district" class="text-sm font-semibold">الحي <span class="text-destructive">*</span></Label>
							<Input
								id="district"
								type="text"
								placeholder="أدخل اسم الحي"
								bind:value={registerForm.district}
								class="h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
								required
								disabled={isSubmitting}
							/>
						</div>

						<!-- Address -->
						<div class="space-y-3">
							<Label for="address" class="text-sm font-semibold">العنوان التفصيلي <span class="text-destructive">*</span></Label>
							<div class="relative group">
								<MapPin class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
								<Input
									id="address"
									type="text"
									placeholder="أدخل العنوان التفصيلي"
									bind:value={registerForm.address}
									class="pl-12 h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
									required
									disabled={isSubmitting}
								/>
							</div>
						</div>

						<!-- CR Number (Optional) -->
						<div class="space-y-3">
							<Label for="cr-number" class="text-sm font-semibold">رقم السجل التجاري (اختياري)</Label>
							<Input
								id="cr-number"
								type="text"
								placeholder="أدخل رقم السجل التجاري"
								bind:value={registerForm.cr_number}
								class="h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
								disabled={isSubmitting}
							/>
						</div>

						<!-- VAT Number (Optional) -->
						<div class="space-y-3">
							<Label for="vat-number" class="text-sm font-semibold">الرقم الضريبي (اختياري)</Label>
							<Input
								id="vat-number"
								type="text"
								placeholder="أدخل الرقم الضريبي"
								bind:value={registerForm.vat_number}
								class="h-12 rounded-xl bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300"
								disabled={isSubmitting}
							/>
						</div>

					{:else if currentStep === 3}
						<!-- Step 3: Review & Terms -->
						
						<div class="space-y-6">
							<!-- Review Summary -->
							<div class="bg-card/30 backdrop-blur-sm rounded-xl p-6 border border-border/50">
								<h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
									<CheckCircle class="h-5 w-5 text-green-600" />
									مراجعة البيانات
								</h3>
								
								<div class="space-y-3 text-sm">
									<div class="flex justify-between">
										<span class="text-muted-foreground">اسم المستخدم:</span>
										<span class="font-medium">{registerForm.username}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">الاسم الأول:</span>
										<span class="font-medium">{registerForm.first_name}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">اسم العائلة:</span>
										<span class="font-medium">{registerForm.last_name}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">البريد الإلكتروني:</span>
										<span class="font-medium">{registerForm.email}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">رقم الهاتف:</span>
										<span class="font-medium">{registerForm.phone_number}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">اسم العمل:</span>
										<span class="font-medium">{registerForm.business_name}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">نوع الخدمة:</span>
										<span class="font-medium">{serviceTypes.find(s => s.value === registerForm.service_type)?.label_ar}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-muted-foreground">المدينة:</span>
										<span class="font-medium">{registerForm.city}</span>
									</div>
								</div>
							</div>

							<!-- Terms and Conditions -->
							<div class="space-y-4">
								<div class="flex items-start space-x-3 space-x-reverse">
									<input
										type="checkbox"
										id="terms"
										bind:checked={registerForm.terms_accepted}
										class="mt-1 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
										disabled={isSubmitting}
									/>
									<Label for="terms" class="text-sm font-medium cursor-pointer">
										أوافق على 
										<a href="/terms" class="text-primary hover:underline">الشروط والأحكام</a>
										و
										<a href="/privacy" class="text-primary hover:underline">سياسة الخصوصية</a>
										<span class="text-destructive">*</span>
									</Label>
								</div>

								{#if !registerForm.terms_accepted}
									<p class="text-sm text-muted-foreground">
										يجب الموافقة على الشروط والأحكام لإنشاء الحساب
									</p>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="flex gap-4 pt-6">
						{#if currentStep > 1}
							<Button 
								type="button" 
								variant="outline" 
								onclick={goToPreviousStep}
								class="flex-1 h-12 rounded-xl hover-lift transition-all duration-300"
								disabled={isSubmitting}
							>
								<ArrowLeft class="h-4 w-4 mr-2" />
								السابق
							</Button>
						{/if}
						<Button 
							type="submit" 
							class="flex-1 h-14 rounded-xl font-bold text-white shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] relative overflow-hidden border-0 ring-2 ring-transparent hover:ring-white/30" 
							disabled={isSubmitting || 
								(currentStep === 1 && !step1Valid) ||
								(currentStep === 2 && !step2Valid) ||
								(currentStep === 3 && !step3Valid)}
							style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 30%, #0891b2 70%, #059669 100%); border: none;"
						>
							{#if isSubmitting}
								<div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
							{/if}
							<span class="relative z-10 font-medium">
								{currentStep === 1 ? 'التالي' : 
								 currentStep === 2 ? 'مراجعة البيانات' : 
								 'إنشاء الحساب'}
							</span>
							<!-- Shine effect -->
							<div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 translate-x-full group-hover:translate-x-[-200%] transition-transform duration-1000"></div>
						</Button>
					</div>
				</form>

				{#if currentStep === 1}
					<!-- Divider -->
					<div class="relative my-8">
						<div class="absolute inset-0 flex items-center">
							<span class="w-full border-t border-border/50"></span>
						</div>
						<div class="relative flex justify-center text-xs uppercase">
							<span class="bg-background px-3 text-muted-foreground font-medium">أو</span>
						</div>
					</div>

					<!-- Login Link -->
					<div class="text-center">
						<p class="text-sm text-muted-foreground">
							لديك حساب بالفعل؟
							<a href="/auth/login" class="text-primary hover:underline font-semibold transition-colors">
								تسجيل الدخول
							</a>
						</p>
					</div>
				{/if}
			</CardContent>
		</Card>

		<!-- Back to Home -->
		<div class="text-center mt-6">
			<a href="/" class="text-sm text-muted-foreground hover:text-foreground transition-colors">
				← العودة إلى الصفحة الرئيسية
			</a>
		</div>
		</div>
	</div>
</div>