<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { 
		Package,
		Clock,
		DollarSign,
		Globe,
		Settings,
		ArrowLeft,
		ArrowRight,
		Check,
		AlertCircle,
		Sparkles,
		Calendar,
		Timer,
		Star
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	// Form state
	let currentStep = $state(1);
	const totalSteps = 4;

	// Service form data
	let serviceForm = $state({
		name: '',
		name_ar: '',
		description: '',
		description_ar: '',
		price: 0,
		duration: 60, // in minutes
		is_active: true,
		category: 'general'
	});

	// Form validation
	let errors = $state({});
	let isSubmitting = $state(false);

	// Duration options (in minutes)
	const durationOptions = [
		{ value: 15, label: '15 دقيقة', icon: Timer },
		{ value: 30, label: '30 دقيقة', icon: Timer },
		{ value: 45, label: '45 دقيقة', icon: Timer },
		{ value: 60, label: 'ساعة واحدة', icon: Clock },
		{ value: 90, label: 'ساعة ونصف', icon: Clock },
		{ value: 120, label: 'ساعتين', icon: Clock },
		{ value: 180, label: '3 ساعات', icon: Clock }
	];

	// Service categories
	const categories = [
		{ value: 'barber', label: 'حلاق', icon: '✂️' },
		{ value: 'salon', label: 'صالون تجميل', icon: '💄' },
		{ value: 'beauty_center', label: 'مركز تجميل', icon: '✨' },
		{ value: 'car_wash', label: 'غسيل السيارات', icon: '🚗' },
		{ value: 'cleaning', label: 'تنظيف', icon: '🧽' },
		{ value: 'gym', label: 'صالة رياضية', icon: '💪' },
		{ value: 'photographer', label: 'مصور', icon: '📸' },
		{ value: 'makeup_artist', label: 'فنان مكياج', icon: '🎨' },
		{ value: 'general', label: 'عام', icon: '📦' }
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

	// Validation
	const validateCurrentStep = () => {
		errors = {};
		
		switch (currentStep) {
			case 1:
				if (!serviceForm.name.trim()) {
					errors.name = 'اسم الخدمة مطلوب';
				}
				if (!serviceForm.description.trim()) {
					errors.description = 'وصف الخدمة مطلوب';
				}
				break;
			case 2:
				if (serviceForm.price <= 0) {
					errors.price = 'السعر يجب أن يكون أكبر من صفر';
				}
				if (serviceForm.duration <= 0) {
					errors.duration = 'مدة الخدمة مطلوبة';
				}
				break;
		}
		
		return Object.keys(errors).length === 0;
	};

	// Form submission
	const handleSubmit = async () => {
		if (!validateCurrentStep()) return;
		
		isSubmitting = true;
		
		try {
			// Convert duration from minutes to Django duration format
			const durationFormatted = `00:${String(Math.floor(serviceForm.duration / 60)).padStart(2, '0')}:${String(serviceForm.duration % 60).padStart(2, '0')}`;
			
			const payload = {
				...serviceForm,
				duration: durationFormatted
			};
			
			// TODO: Replace with actual API call
			console.log('Creating service:', payload);
			
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 2000));
			
			// Redirect to services list
			goto('/dashboard/services');
			
		} catch (error) {
			console.error('Error creating service:', error);
			errors.submit = 'حدث خطأ أثناء إنشاء الخدمة';
		} finally {
			isSubmitting = false;
		}
	};

	// Format price display
	const formatPrice = (price: number) => {
		return new Intl.NumberFormat('ar-SA', {
			style: 'currency',
			currency: 'SAR',
			minimumFractionDigits: 0
		}).format(price);
	};

	// Format duration display
	const formatDuration = (minutes: number) => {
		const hours = Math.floor(minutes / 60);
		const mins = minutes % 60;
		
		if (hours === 0) {
			return `${mins} دقيقة`;
		} else if (mins === 0) {
			return `${hours} ساعة`;
		} else {
			return `${hours} ساعة و ${mins} دقيقة`;
		}
	};

	// Navigation guard
	const handleBack = () => {
		goto('/dashboard/services');
	};
</script>

<svelte:head>
	<title>إضافة خدمة جديدة - Wagtee</title>
	<meta name="description" content="إضافة خدمة جديدة إلى عملك التجاري" />
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<!-- Header -->
	<div class="flex items-center gap-4 mb-8">
		<Button variant="ghost" size="sm" onclick={handleBack} class="gap-2">
			<ArrowLeft class="w-4 h-4" />
			العودة
		</Button>
		<div class="flex-1">
			<h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
				إضافة خدمة جديدة
			</h1>
			<p class="text-muted-foreground mt-1">
				أضف خدمة جديدة إلى عملك التجاري واستقبل المزيد من الحجوزات
			</p>
		</div>
		<div class="hidden sm:flex items-center gap-2">
			<Badge variant="secondary" class="gap-1">
				<Sparkles class="w-3 h-3" />
				تصميم متطور
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
				class="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500 ease-out"
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
							index + 1 === currentStep ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' :
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
						{index === 0 ? 'المعلومات' : 
						 index === 1 ? 'السعر والمدة' : 
						 index === 2 ? 'الإعدادات' : 
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
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
					{#if currentStep === 1}
						<Package class="w-5 h-5 text-white" />
					{:else if currentStep === 2}
						<DollarSign class="w-5 h-5 text-white" />
					{:else if currentStep === 3}
						<Settings class="w-5 h-5 text-white" />
					{:else}
						<Check class="w-5 h-5 text-white" />
					{/if}
				</div>
				<div>
					<CardTitle class="text-xl">
						{currentStep === 1 ? 'المعلومات الأساسية' :
						 currentStep === 2 ? 'السعر ومدة الخدمة' :
						 currentStep === 3 ? 'الإعدادات المتقدمة' :
						 'مراجعة وحفظ'}
					</CardTitle>
					<CardDescription>
						{currentStep === 1 ? 'أدخل اسم ووصف الخدمة باللغتين العربية والإنجليزية' :
						 currentStep === 2 ? 'حدد سعر الخدمة والوقت المطلوب لتنفيذها' :
						 currentStep === 3 ? 'اختر التصنيف وحالة النشاط للخدمة' :
						 'راجع المعلومات قبل حفظ الخدمة'}
					</CardDescription>
				</div>
			</div>
		</CardHeader>

		<CardContent class="space-y-6">
			{#if currentStep === 1}
				<!-- Step 1: Basic Information -->
				<div class="grid gap-6">
					<div class="grid md:grid-cols-2 gap-4">
						<!-- Service Name -->
						<div class="space-y-2">
							<Label for="name" class="text-sm font-medium flex items-center gap-2">
								اسم الخدمة (عربي) <span class="text-destructive">*</span>
							</Label>
							<Input
								id="name"
								type="text"
								placeholder="مثال: قص شعر وتشذيب"
								bind:value={serviceForm.name}
								class="h-11 {errors.name ? 'border-destructive' : ''}"
								disabled={isSubmitting}
							/>
							{#if errors.name}
								<p class="text-sm text-destructive">{errors.name}</p>
							{/if}
						</div>

						<!-- Service Name English -->
						<div class="space-y-2">
							<Label for="name_ar" class="text-sm font-medium">
								اسم الخدمة (إنجليزي)
							</Label>
							<Input
								id="name_ar"
								type="text"
								placeholder="Example: Haircut & Trim"
								bind:value={serviceForm.name_ar}
								class="h-11"
								disabled={isSubmitting}
							/>
						</div>
					</div>

					<div class="grid md:grid-cols-2 gap-4">
						<!-- Description Arabic -->
						<div class="space-y-2">
							<Label for="description" class="text-sm font-medium flex items-center gap-2">
								وصف الخدمة (عربي) <span class="text-destructive">*</span>
							</Label>
							<Textarea
								id="description"
								placeholder="وصف مفصل عن الخدمة المقدمة..."
								bind:value={serviceForm.description}
								class="min-h-24 {errors.description ? 'border-destructive' : ''}"
								disabled={isSubmitting}
							/>
							{#if errors.description}
								<p class="text-sm text-destructive">{errors.description}</p>
							{/if}
						</div>

						<!-- Description English -->
						<div class="space-y-2">
							<Label for="description_ar" class="text-sm font-medium">
								وصف الخدمة (إنجليزي)
							</Label>
							<Textarea
								id="description_ar"
								placeholder="Detailed description of the service..."
								bind:value={serviceForm.description_ar}
								class="min-h-24"
								disabled={isSubmitting}
							/>
						</div>
					</div>
				</div>

			{:else if currentStep === 2}
				<!-- Step 2: Pricing & Duration -->
				<div class="space-y-6">
					<!-- Price Section -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<DollarSign class="w-5 h-5 text-green-600" />
							<h3 class="text-lg font-semibold">تحديد السعر</h3>
						</div>
						
						<div class="grid md:grid-cols-2 gap-4">
							<div class="space-y-2">
								<Label for="price" class="text-sm font-medium flex items-center gap-2">
									سعر الخدمة <span class="text-destructive">*</span>
								</Label>
								<div class="relative">
									<Input
										id="price"
										type="number"
										min="0"
										step="0.01"
										placeholder="0.00"
										bind:value={serviceForm.price}
										class="h-11 pr-12 {errors.price ? 'border-destructive' : ''}"
										disabled={isSubmitting}
									/>
									<div class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
										ر.س
									</div>
								</div>
								{#if errors.price}
									<p class="text-sm text-destructive">{errors.price}</p>
								{/if}
							</div>
							
							<div class="bg-accent/20 p-4 rounded-lg">
								<div class="text-sm text-muted-foreground mb-1">معاينة السعر</div>
								<div class="text-2xl font-bold text-green-600">
									{formatPrice(serviceForm.price)}
								</div>
							</div>
						</div>
					</div>

					<!-- Duration Section -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Clock class="w-5 h-5 text-blue-600" />
							<h3 class="text-lg font-semibold">مدة الخدمة</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							{#each durationOptions as option}
								<button
									type="button"
									onclick={() => serviceForm.duration = option.value}
									class="p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 {
										serviceForm.duration === option.value 
											? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20' 
											: 'border-border hover:border-blue-300'
									}"
									disabled={isSubmitting}
								>
									<div class="flex flex-col items-center gap-2">
										<svelte:component this={option.icon} class="w-5 h-5 {
											serviceForm.duration === option.value ? 'text-blue-600' : 'text-muted-foreground'
										}" />
										<span class="text-sm font-medium">{option.label}</span>
									</div>
								</button>
							{/each}
						</div>
						
						<!-- Custom Duration -->
						<div class="bg-accent/20 p-4 rounded-lg">
							<Label for="custom-duration" class="text-sm font-medium">مدة مخصصة (بالدقائق)</Label>
							<Input
								id="custom-duration"
								type="number"
								min="1"
								placeholder="60"
								bind:value={serviceForm.duration}
								class="h-10 mt-2"
								disabled={isSubmitting}
							/>
							<div class="text-sm text-muted-foreground mt-2">
								المدة المحددة: {formatDuration(serviceForm.duration)}
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 3}
				<!-- Step 3: Advanced Settings -->
				<div class="space-y-6">
					<!-- Category Selection -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Package class="w-5 h-5 text-purple-600" />
							<h3 class="text-lg font-semibold">تصنيف الخدمة</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-3 gap-3">
							{#each categories as category}
								<button
									type="button"
									onclick={() => serviceForm.category = category.value}
									class="p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 {
										serviceForm.category === category.value 
											? 'border-purple-500 bg-purple-50 dark:bg-purple-950/20' 
											: 'border-border hover:border-purple-300'
									}"
									disabled={isSubmitting}
								>
									<div class="flex flex-col items-center gap-2">
										<span class="text-2xl">{category.icon}</span>
										<span class="text-sm font-medium">{category.label}</span>
									</div>
								</button>
							{/each}
						</div>
					</div>

					<!-- Status Toggle -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Settings class="w-5 h-5 text-orange-600" />
							<h3 class="text-lg font-semibold">حالة الخدمة</h3>
						</div>
						
						<div class="bg-accent/20 p-4 rounded-lg">
							<div class="flex items-center justify-between">
								<div>
									<div class="font-medium">تفعيل الخدمة</div>
									<div class="text-sm text-muted-foreground">
										عند التفعيل، ستكون الخدمة متاحة للحجز من قبل العملاء
									</div>
								</div>
								<label class="relative inline-flex items-center cursor-pointer">
									<input
										type="checkbox"
										bind:checked={serviceForm.is_active}
										class="sr-only peer"
										disabled={isSubmitting}
									/>
									<div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
								</label>
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 4}
				<!-- Step 4: Review & Confirmation -->
				<div class="space-y-6">
					<div class="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-950/20 dark:to-blue-950/20 p-6 rounded-xl">
						<div class="flex items-center gap-3 mb-4">
							<div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
								<Check class="w-4 h-4 text-green-600" />
							</div>
							<h3 class="text-lg font-semibold">مراجعة بيانات الخدمة</h3>
						</div>
						
						<div class="grid md:grid-cols-2 gap-6">
							<!-- Basic Information -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">المعلومات الأساسية</h4>
								<div class="space-y-2">
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">اسم الخدمة:</span>
										<span class="text-sm font-medium">{serviceForm.name}</span>
									</div>
									{#if serviceForm.name_ar}
										<div class="flex justify-between">
											<span class="text-sm text-muted-foreground">الاسم بالإنجليزية:</span>
											<span class="text-sm font-medium">{serviceForm.name_ar}</span>
										</div>
									{/if}
									<div class="flex justify-between items-start">
										<span class="text-sm text-muted-foreground">الوصف:</span>
										<span class="text-sm font-medium text-right max-w-48">{serviceForm.description}</span>
									</div>
								</div>
							</div>

							<!-- Pricing & Duration -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">السعر والمدة</h4>
								<div class="space-y-2">
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">السعر:</span>
										<span class="text-sm font-bold text-green-600">{formatPrice(serviceForm.price)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">المدة:</span>
										<span class="text-sm font-medium">{formatDuration(serviceForm.duration)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">التصنيف:</span>
										<span class="text-sm font-medium">
											{categories.find(c => c.value === serviceForm.category)?.label || 'عام'}
										</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm text-muted-foreground">الحالة:</span>
										<Badge variant={serviceForm.is_active ? 'default' : 'secondary'}>
											{serviceForm.is_active ? 'نشط' : 'غير نشط'}
										</Badge>
									</div>
								</div>
							</div>
						</div>
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
						class="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
					>
						التالي
						<ArrowRight class="w-4 h-4" />
					</Button>
				{:else}
					<Button
						onclick={handleSubmit}
						disabled={isSubmitting}
						class="gap-2 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
					>
						{#if isSubmitting}
							<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
						{:else}
							<Check class="w-4 h-4" />
						{/if}
						حفظ الخدمة
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
	
	:global(.animate-gradient) {
		background-size: 200% 200%;
		animation: gradient 3s ease infinite;
	}
	
	@keyframes gradient {
		0% { background-position: 0% 50%; }
		50% { background-position: 100% 50%; }
		100% { background-position: 0% 50%; }
	}
</style>