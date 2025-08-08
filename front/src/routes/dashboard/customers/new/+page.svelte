<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs/index.js';
	import { 
		User,
		Phone,
		Mail,
		MapPin,
		ArrowLeft,
		ArrowRight,
		Check,
		AlertCircle,
		Sparkles,
		Heart,
		Star,
		MessageSquare,
		Users,
		Calendar,
		Clock
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/services/api-client.js';
	import { toast } from 'svelte-sonner';

	// Form state
	let currentStep = $state(1);
	const totalSteps = 3;

	// Customer form data
	let customerForm = $state({
		name: '',
		phone_number: '',
		email: '',
		address: '',
		notes: '',
		preferences: {
			preferredTime: 'morning',
			communicationMethod: 'whatsapp',
			specialRequests: ''
		},
		tags: []
	});

	// Form validation
	let errors = $state({});
	let isSubmitting = $state(false);

	// Predefined customer tags
	const availableTags = [
		{ value: 'vip', label: 'عميل مميز', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' },
		{ value: 'regular', label: 'عميل دائم', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300' },
		{ value: 'new', label: 'عميل جديد', color: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' },
		{ value: 'referral', label: 'إحالة', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300' },
		{ value: 'sensitive', label: 'حساس للوقت', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300' },
		{ value: 'flexible', label: 'مرن', color: 'bg-teal-100 text-teal-800 dark:bg-teal-900/20 dark:text-teal-300' }
	];

	// Preferred time options
	const timePreferences = [
		{ value: 'morning', label: 'الصباح', icon: '🌅', description: '8:00 - 12:00' },
		{ value: 'afternoon', label: 'بعد الظهر', icon: '☀️', description: '12:00 - 17:00' },
		{ value: 'evening', label: 'المساء', icon: '🌆', description: '17:00 - 21:00' },
		{ value: 'flexible', label: 'مرن', icon: '⏰', description: 'أي وقت متاح' }
	];

	// Communication preferences
	const communicationMethods = [
		{ value: 'whatsapp', label: 'واتساب', icon: '💬', color: 'text-green-600' },
		{ value: 'sms', label: 'رسائل نصية', icon: '📱', color: 'text-blue-600' },
		{ value: 'call', label: 'مكالمة هاتفية', icon: '📞', color: 'text-purple-600' },
		{ value: 'email', label: 'بريد إلكتروني', icon: '✉️', color: 'text-orange-600' }
	];

	// Step navigation
	const goToStep = (step: number) => {
		if (step >= 1 && step <= totalSteps) {
			currentStep = step;
		}
	};

	const nextStep = () => {
		if (validateCurrentStep()) {
			if (currentStep < totalSteps) {
				currentStep++;
			}
		}
	};

	const prevStep = () => {
		if (currentStep > 1) {
			currentStep--;
		}
	};

	// Phone number formatting
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
		customerForm.phone_number = formatted;
	};

	// Saudi phone number validation
	const validatePhoneNumber = (phone: string) => {
		const saudiPhoneRegex = /^\+966[0-9]{9}$/;
		return saudiPhoneRegex.test(phone);
	};

	// Tag management
	const toggleTag = (tagValue: string) => {
		const index = customerForm.tags.indexOf(tagValue);
		if (index > -1) {
			customerForm.tags = customerForm.tags.filter(t => t !== tagValue);
		} else {
			customerForm.tags = [...customerForm.tags, tagValue];
		}
	};

	// Validation
	const validateCurrentStep = () => {
		errors = {};
		
		switch (currentStep) {
			case 1:
				if (!customerForm.name.trim()) {
					errors.name = 'اسم العميل مطلوب';
				}
				if (!customerForm.phone_number.trim()) {
					errors.phone_number = 'رقم الهاتف مطلوب';
				} else if (!validatePhoneNumber(customerForm.phone_number)) {
					errors.phone_number = 'رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx';
				}
				if (customerForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerForm.email)) {
					errors.email = 'البريد الإلكتروني غير صحيح';
				}
				break;
			case 2:
				// Optional validation for step 2
				break;
		}
		
		return Object.keys(errors).length === 0;
	};

	// Form submission
	const handleSubmit = async () => {
		if (!validateCurrentStep()) return;
		
		isSubmitting = true;
		
		try {
			const payload = {
				name: customerForm.name,
				phone_number: customerForm.phone_number,
				email: customerForm.email || null,
				address: customerForm.address || null,
				notes: customerForm.notes || null
			};
			
			// Create customer using real API
			const result = await api.customers.create(payload);
			
			if (result.success && result.data) {
				toast.success('تم إنشاء العميل بنجاح');
				goto('/dashboard/customers');
			} else {
				errors.submit = result.error || 'فشل في إنشاء العميل';
			}
			
		} catch (error) {
			console.error('Error creating customer:', error);
			errors.submit = 'حدث خطأ أثناء إضافة العميل';
		} finally {
			isSubmitting = false;
		}
	};

	// Navigation guard
	const handleBack = () => {
		goto('/dashboard/customers');
	};
</script>

<svelte:head>
	<title>إضافة عميل جديد - Wagtee</title>
	<meta name="description" content="إضافة عميل جديد إلى قاعدة العملاء" />
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<!-- Header -->
	<div class="flex items-center gap-4 mb-8">
		<Button variant="ghost" size="sm" onclick={handleBack} class="gap-2">
			<ArrowLeft class="w-4 h-4" />
			العودة
		</Button>
		<div class="flex-1">
			<h1 class="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
				إضافة عميل جديد
			</h1>
			<p class="text-muted-foreground mt-1">
				أضف عميل جديد إلى قاعدة العملاء وابدأ في بناء علاقة تجارية مثمرة
			</p>
		</div>
		<div class="hidden sm:flex items-center gap-2">
			<Badge variant="secondary" class="gap-1">
				<Users class="w-3 h-3" />
				إدارة العملاء
			</Badge>
		</div>
	</div>

	<!-- Progress Indicator -->
	<div class="mb-8">
		<div class="flex items-center justify-between mb-4">
			<span class="text-sm text-muted-foreground">الخطوة {currentStep} من {totalSteps}</span>
			<span class="text-sm text-muted-foreground">{Math.round((currentStep / totalSteps) * 100)}% مكتمل</span>
		</div>
		<div class="w-full bg-border rounded-full h-2">
			<div 
				class="bg-gradient-to-r from-emerald-600 to-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
				style="width: {(currentStep / totalSteps) * 100}%"
			></div>
		</div>
		
		<!-- Step indicators -->
		<div class="flex justify-between mt-4">
			{#each Array(totalSteps) as _, index}
				<div class="flex flex-col items-center">
					<div 
						class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 {
							index + 1 < currentStep ? 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400' :
							index + 1 === currentStep ? 'bg-gradient-to-r from-emerald-600 to-blue-600 text-white' :
							'bg-border text-muted-foreground'
						}"
					>
						{#if index + 1 < currentStep}
							<Check class="w-4 h-4" />
						{:else}
							{index + 1}
						{/if}
					</div>
					<span class="text-xs text-muted-foreground mt-1 text-center">
						{index === 0 ? 'معلومات الاتصال' : 
						 index === 1 ? 'التفضيلات' : 
						 'المراجعة'}
					</span>
				</div>
			{/each}
		</div>
	</div>

	<!-- Main Form Card -->
	<Card class="border-0 shadow-2xl bg-gradient-to-br from-card/50 to-card backdrop-blur-sm">
		<CardHeader class="pb-6">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-blue-600 flex items-center justify-center">
					{#if currentStep === 1}
						<User class="w-5 h-5 text-white" />
					{:else if currentStep === 2}
						<Heart class="w-5 h-5 text-white" />
					{:else}
						<Check class="w-5 h-5 text-white" />
					{/if}
				</div>
				<div>
					<CardTitle class="text-xl">
						{currentStep === 1 ? 'معلومات الاتصال' :
						 currentStep === 2 ? 'تفضيلات العميل' :
						 'مراجعة وحفظ'}
					</CardTitle>
					<CardDescription>
						{currentStep === 1 ? 'أدخل معلومات الاتصال الأساسية للعميل' :
						 currentStep === 2 ? 'حدد تفضيلات العميل لتقديم خدمة أفضل' :
						 'راجع المعلومات قبل حفظ بيانات العميل'}
					</CardDescription>
				</div>
			</div>
		</CardHeader>

		<CardContent class="space-y-6">
			{#if currentStep === 1}
				<!-- Step 1: Contact Information -->
				<div class="grid gap-6">
					<div class="grid md:grid-cols-2 gap-4">
						<!-- Customer Name -->
						<div class="space-y-2">
							<Label for="name" class="text-sm font-medium flex items-center gap-2">
								<User class="w-4 h-4" />
								اسم العميل <span class="text-destructive">*</span>
							</Label>
							<Input
								id="name"
								type="text"
								placeholder="محمد أحمد علي"
								bind:value={customerForm.name}
								class="h-11 {errors.name ? 'border-destructive' : ''}"
								disabled={isSubmitting}
							/>
							{#if errors.name}
								<p class="text-sm text-destructive">{errors.name}</p>
							{/if}
						</div>

						<!-- Phone Number -->
						<div class="space-y-2">
							<Label for="phone" class="text-sm font-medium flex items-center gap-2">
								<Phone class="w-4 h-4" />
								رقم الهاتف <span class="text-destructive">*</span>
							</Label>
							<Input
								id="phone"
								type="tel"
								placeholder="+966xxxxxxxxx"
								bind:value={customerForm.phone_number}
								oninput={handlePhoneInput}
								class="h-11 {errors.phone_number ? 'border-destructive' : ''}"
								disabled={isSubmitting}
							/>
							{#if errors.phone_number}
								<p class="text-sm text-destructive">{errors.phone_number}</p>
							{/if}
						</div>
					</div>

					<div class="grid md:grid-cols-2 gap-4">
						<!-- Email -->
						<div class="space-y-2">
							<Label for="email" class="text-sm font-medium flex items-center gap-2">
								<Mail class="w-4 h-4" />
								البريد الإلكتروني
							</Label>
							<Input
								id="email"
								type="email"
								placeholder="mohammed@example.com"
								bind:value={customerForm.email}
								class="h-11 {errors.email ? 'border-destructive' : ''}"
								disabled={isSubmitting}
							/>
							{#if errors.email}
								<p class="text-sm text-destructive">{errors.email}</p>
							{/if}
							<p class="text-xs text-muted-foreground">اختياري - يُستخدم لإرسال الإشعارات والعروض</p>
						</div>

						<!-- Address -->
						<div class="space-y-2">
							<Label for="address" class="text-sm font-medium flex items-center gap-2">
								<MapPin class="w-4 h-4" />
								العنوان
							</Label>
							<Input
								id="address"
								type="text"
								placeholder="الرياض، حي النخيل"
								bind:value={customerForm.address}
								class="h-11"
								disabled={isSubmitting}
							/>
							<p class="text-xs text-muted-foreground">اختياري - مفيد للخدمات المنزلية</p>
						</div>
					</div>

					<!-- Notes -->
					<div class="space-y-2">
						<Label for="notes" class="text-sm font-medium flex items-center gap-2">
							<MessageSquare class="w-4 h-4" />
							ملاحظات إضافية
						</Label>
						<Textarea
							id="notes"
							placeholder="أي ملاحظات مهمة عن العميل..."
							bind:value={customerForm.notes}
							class="min-h-20"
							disabled={isSubmitting}
						/>
						<p class="text-xs text-muted-foreground">معلومات إضافية قد تساعد في تقديم خدمة أفضل</p>
					</div>
				</div>

			{:else if currentStep === 2}
				<!-- Step 2: Preferences -->
				<div class="space-y-6">
					<!-- Preferred Time -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Clock class="w-5 h-5 text-blue-600" />
							<h3 class="text-lg font-semibold">الوقت المفضل للحجز</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							{#each timePreferences as time}
								<button
									type="button"
									onclick={() => customerForm.preferences.preferredTime = time.value}
									class="p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 {
										customerForm.preferences.preferredTime === time.value 
											? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20' 
											: 'border-border hover:border-blue-300'
									}"
									disabled={isSubmitting}
								>
									<div class="flex flex-col items-center gap-2">
										<span class="text-2xl">{time.icon}</span>
										<span class="text-sm font-medium">{time.label}</span>
										<span class="text-xs text-muted-foreground">{time.description}</span>
									</div>
								</button>
							{/each}
						</div>
					</div>

					<!-- Communication Method -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<MessageSquare class="w-5 h-5 text-green-600" />
							<h3 class="text-lg font-semibold">طريقة التواصل المفضلة</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							{#each communicationMethods as method}
								<button
									type="button"
									onclick={() => customerForm.preferences.communicationMethod = method.value}
									class="p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 {
										customerForm.preferences.communicationMethod === method.value 
											? 'border-green-500 bg-green-50 dark:bg-green-950/20' 
											: 'border-border hover:border-green-300'
									}"
									disabled={isSubmitting}
								>
									<div class="flex flex-col items-center gap-2">
										<span class="text-2xl">{method.icon}</span>
										<span class="text-sm font-medium {method.color}">{method.label}</span>
									</div>
								</button>
							{/each}
						</div>
					</div>

					<!-- Customer Tags -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Star class="w-5 h-5 text-yellow-600" />
							<h3 class="text-lg font-semibold">تصنيف العميل</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-3 gap-3">
							{#each availableTags as tag}
								<button
									type="button"
									onclick={() => toggleTag(tag.value)}
									class="p-3 rounded-lg border-2 transition-all duration-200 {
										customerForm.tags.includes(tag.value) 
											? 'border-transparent ' + tag.color 
											: 'border-border hover:border-gray-300 bg-background'
									}"
									disabled={isSubmitting}
								>
									<div class="flex items-center gap-2">
										{#if customerForm.tags.includes(tag.value)}
											<Check class="w-4 h-4" />
										{/if}
										<span class="text-sm font-medium">{tag.label}</span>
									</div>
								</button>
							{/each}
						</div>
						<p class="text-xs text-muted-foreground">يمكنك اختيار أكثر من تصنيف</p>
					</div>

					<!-- Special Requests -->
					<div class="space-y-2">
						<Label for="special-requests" class="text-sm font-medium">طلبات خاصة</Label>
						<Textarea
							id="special-requests"
							placeholder="مثال: يفضل الخدمة في مكان هادئ، حساس من بعض المنتجات..."
							bind:value={customerForm.preferences.specialRequests}
							class="min-h-20"
							disabled={isSubmitting}
						/>
						<p class="text-xs text-muted-foreground">أي متطلبات خاصة يجب مراعاتها عند تقديم الخدمة</p>
					</div>
				</div>

			{:else if currentStep === 3}
				<!-- Step 3: Review & Confirmation -->
				<div class="space-y-6">
					<div class="bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-950/20 dark:to-blue-950/20 p-6 rounded-xl">
						<div class="flex items-center gap-3 mb-4">
							<div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
								<Check class="w-4 h-4 text-green-600" />
							</div>
							<h3 class="text-lg font-semibold">مراجعة بيانات العميل</h3>
						</div>
						
						<div class="grid md:grid-cols-2 gap-6">
							<!-- Contact Information -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">معلومات الاتصال</h4>
								<div class="space-y-2">
									<div class="flex items-center gap-2">
										<User class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{customerForm.name}</span>
									</div>
									<div class="flex items-center gap-2">
										<Phone class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{customerForm.phone_number}</span>
									</div>
									{#if customerForm.email}
										<div class="flex items-center gap-2">
											<Mail class="w-4 h-4 text-muted-foreground" />
											<span class="text-sm font-medium">{customerForm.email}</span>
										</div>
									{/if}
									{#if customerForm.address}
										<div class="flex items-center gap-2">
											<MapPin class="w-4 h-4 text-muted-foreground" />
											<span class="text-sm font-medium">{customerForm.address}</span>
										</div>
									{/if}
								</div>
							</div>

							<!-- Preferences -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">التفضيلات</h4>
								<div class="space-y-2">
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">وقت مفضل:</span>
										<span class="text-sm font-medium">
											{timePreferences.find(t => t.value === customerForm.preferences.preferredTime)?.label}
										</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">طريقة التواصل:</span>
										<span class="text-sm font-medium">
											{communicationMethods.find(m => m.value === customerForm.preferences.communicationMethod)?.label}
										</span>
									</div>
									{#if customerForm.tags.length > 0}
										<div class="flex flex-wrap gap-1 mt-2">
											<span class="text-sm text-muted-foreground">التصنيفات:</span>
											{#each customerForm.tags as tagValue}
												{@const tag = availableTags.find(t => t.value === tagValue)}
												{#if tag}
													<Badge class={tag.color}>{tag.label}</Badge>
												{/if}
											{/each}
										</div>
									{/if}
								</div>
							</div>
						</div>

						{#if customerForm.notes}
							<div class="mt-4 p-3 bg-accent/20 rounded-lg">
								<div class="text-sm text-muted-foreground mb-1">ملاحظات:</div>
								<div class="text-sm">{customerForm.notes}</div>
							</div>
						{/if}

						{#if customerForm.preferences.specialRequests}
							<div class="mt-4 p-3 bg-accent/20 rounded-lg">
								<div class="text-sm text-muted-foreground mb-1">طلبات خاصة:</div>
								<div class="text-sm">{customerForm.preferences.specialRequests}</div>
							</div>
						{/if}
					</div>

					{#if errors.submit}
						<div class="p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive">
							<AlertCircle class="h-4 w-4" />
							<span class="text-sm">{errors.submit}</span>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Navigation Buttons -->
			<div class="flex justify-between pt-6 border-t">
				<Button
					variant="outline"
					onclick={prevStep}
					disabled={currentStep === 1 || isSubmitting}
					class="gap-2"
				>
					<ArrowLeft class="w-4 h-4" />
					السابق
				</Button>

				{#if currentStep < totalSteps}
					<Button
						onclick={nextStep}
						disabled={isSubmitting}
						class="gap-2 bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
					>
						التالي
						<ArrowRight class="w-4 h-4" />
					</Button>
				{:else}
					<Button
						onclick={handleSubmit}
						disabled={isSubmitting}
						class="gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
					>
						{#if isSubmitting}
							<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
						{:else}
							<Check class="w-4 h-4" />
						{/if}
						حفظ العميل
					</Button>
				{/if}
			</div>
		</CardContent>
	</Card>
</div>

<style>
	:global(.bg-gradient-to-br) {
		background-image: linear-gradient(135deg, var(--tw-gradient-stops));
	}
</style>