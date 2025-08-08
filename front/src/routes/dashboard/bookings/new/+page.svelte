<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { 
		Calendar,
		Clock,
		User,
		Search,
		Plus,
		Phone,
		Mail,
		Package,
		DollarSign,
		ArrowLeft,
		ArrowRight,
		Check,
		AlertCircle,
		Sparkles,
		QrCode,
		MapPin,
		Timer,
		Star,
		Zap,
		MessageSquare,
		CreditCard,
		CheckCircle
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	// Form state
	let currentStep = $state(1);
	const totalSteps = 5;

	// Mock data - in real app, this would come from API
	let existingCustomers = $state([
		{ id: 1, name: 'أحمد محمد علي', phone: '+966501234567', email: 'ahmed@example.com', isRegular: true },
		{ id: 2, name: 'فاطمة عبدالله', phone: '+966507654321', email: 'fatima@example.com', isVip: true },
		{ id: 3, name: 'محمد سعد', phone: '+966509876543', email: '', isNew: true }
	]);

	let availableServices = $state([
		{ id: 1, name: 'قص شعر رجالي', duration: 30, price: 50, category: 'barber' },
		{ id: 2, name: 'حلاقة وتشذيب', duration: 45, price: 75, category: 'barber' },
		{ id: 3, name: 'صبغة شعر', duration: 120, price: 200, category: 'salon' },
		{ id: 4, name: 'تنظيف بشرة', duration: 60, price: 150, category: 'beauty' }
	]);

	// Booking form data
	let bookingForm = $state({
		customer: null,
		newCustomer: {
			name: '',
			phone: '',
			email: ''
		},
		service: null,
		appointmentDate: '',
		appointmentTime: '',
		bookingMethod: 'online',
		notes: '',
		autoConfirm: true,
		reminderSettings: {
			enabled: true,
			timeBefore: 24 // hours
		}
	});

	// UI state
	let customerSearchQuery = $state('');
	let filteredCustomers = $derived(
		existingCustomers.filter(customer => 
			customer.name.includes(customerSearchQuery) || 
			customer.phone.includes(customerSearchQuery)
		)
	);
	let showNewCustomerForm = $state(false);
	let selectedTimeSlots = $state([]);

	// Form validation
	let errors = $state({});
	let isSubmitting = $state(false);

	// Booking methods
	const bookingMethods = [
		{ value: 'online', label: 'حجز إلكتروني', icon: '💻', description: 'عبر الموقع أو التطبيق' },
		{ value: 'walk_in', label: 'زيارة مباشرة', icon: '🚶', description: 'عميل حضر مباشرة' },
		{ value: 'phone', label: 'مكالمة هاتفية', icon: '📞', description: 'حجز عبر الهاتف' },
		{ value: 'qr_scan', label: 'رمز QR', icon: '🔲', description: 'مسح رمز QR' }
	];

	// Time slots (would be generated based on business hours and existing bookings)
	const generateTimeSlots = (date: string) => {
		const slots = [];
		for (let hour = 9; hour <= 20; hour++) {
			for (let minute = 0; minute < 60; minute += 30) {
				const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
				slots.push({
					time: timeString,
					available: Math.random() > 0.3, // Mock availability
					isRecommended: hour >= 10 && hour <= 16
				});
			}
		}
		return slots;
	};

	// Watch for date changes to update time slots
	$effect(() => {
		if (bookingForm.appointmentDate) {
			selectedTimeSlots = generateTimeSlots(bookingForm.appointmentDate);
		}
	});

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

	// Customer selection
	const selectCustomer = (customer) => {
		bookingForm.customer = customer;
		showNewCustomerForm = false;
	};

	const toggleNewCustomerForm = () => {
		showNewCustomerForm = !showNewCustomerForm;
		if (showNewCustomerForm) {
			bookingForm.customer = null;
		}
	};

	// Service selection
	const selectService = (service) => {
		bookingForm.service = service;
	};

	// Time slot selection
	const selectTimeSlot = (timeSlot) => {
		if (timeSlot.available) {
			bookingForm.appointmentTime = timeSlot.time;
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
		bookingForm.newCustomer.phone = formatted;
	};

	// Validation
	const validatePhoneNumber = (phone: string) => {
		const saudiPhoneRegex = /^\+966[0-9]{9}$/;
		return saudiPhoneRegex.test(phone);
	};

	const validateCurrentStep = () => {
		errors = {};
		
		switch (currentStep) {
			case 1:
				if (!bookingForm.customer && !showNewCustomerForm) {
					errors.customer = 'يجب اختيار عميل أو إضافة عميل جديد';
				}
				if (showNewCustomerForm) {
					if (!bookingForm.newCustomer.name.trim()) {
						errors.customerName = 'اسم العميل مطلوب';
					}
					if (!bookingForm.newCustomer.phone.trim()) {
						errors.customerPhone = 'رقم الهاتف مطلوب';
					} else if (!validatePhoneNumber(bookingForm.newCustomer.phone)) {
						errors.customerPhone = 'رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx';
					}
				}
				break;
			case 2:
				if (!bookingForm.service) {
					errors.service = 'يجب اختيار خدمة';
				}
				break;
			case 3:
				if (!bookingForm.appointmentDate) {
					errors.date = 'يجب اختيار تاريخ الموعد';
				}
				if (!bookingForm.appointmentTime) {
					errors.time = 'يجب اختيار وقت الموعد';
				}
				break;
			case 4:
				if (!bookingForm.bookingMethod) {
					errors.method = 'يجب اختيار طريقة الحجز';
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
			const payload = {
				...bookingForm,
				customer: bookingForm.customer || bookingForm.newCustomer,
				total_price: bookingForm.service?.price || 0
			};
			
			// TODO: Replace with actual API call
			console.log('Creating booking:', payload);
			
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 2000));
			
			// Redirect to bookings list
			goto('/dashboard/bookings');
			
		} catch (error) {
			console.error('Error creating booking:', error);
			errors.submit = 'حدث خطأ أثناء إنشاء الحجز';
		} finally {
			isSubmitting = false;
		}
	};

	// Utility functions
	const formatPrice = (price: number) => {
		return new Intl.NumberFormat('ar-SA', {
			style: 'currency',
			currency: 'SAR',
			minimumFractionDigits: 0
		}).format(price);
	};

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

	const getDateText = (dateString: string) => {
		const date = new Date(dateString);
		return date.toLocaleDateString('ar-SA', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	};

	// Navigation guard
	const handleBack = () => {
		goto('/dashboard/bookings');
	};

	// Set minimum date to today
	const today = new Date().toISOString().split('T')[0];
</script>

<svelte:head>
	<title>حجز موعد جديد - Wagtee</title>
	<meta name="description" content="إنشاء حجز موعد جديد" />
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-5xl">
	<!-- Header -->
	<div class="flex items-center gap-4 mb-8">
		<Button variant="ghost" size="sm" onclick={handleBack} class="gap-2">
			<ArrowLeft class="w-4 h-4" />
			العودة
		</Button>
		<div class="flex-1">
			<h1 class="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
				حجز موعد جديد
			</h1>
			<p class="text-muted-foreground mt-1">
				أنشئ حجز موعد جديد وإدارة تفاصيل الحجز بسهولة
			</p>
		</div>
		<div class="hidden sm:flex items-center gap-2">
			<Badge variant="secondary" class="gap-1">
				<Calendar class="w-3 h-3" />
				نظام الحجوزات
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
				class="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full transition-all duration-500 ease-out"
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
							index + 1 === currentStep ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white' :
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
						{index === 0 ? 'العميل' : 
						 index === 1 ? 'الخدمة' : 
						 index === 2 ? 'التاريخ والوقت' :
						 index === 3 ? 'التفاصيل' :
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
				<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
					{#if currentStep === 1}
						<User class="w-5 h-5 text-white" />
					{:else if currentStep === 2}
						<Package class="w-5 h-5 text-white" />
					{:else if currentStep === 3}
						<Calendar class="w-5 h-5 text-white" />
					{:else if currentStep === 4}
						<MessageSquare class="w-5 h-5 text-white" />
					{:else}
						<Check class="w-5 h-5 text-white" />
					{/if}
				</div>
				<div>
					<CardTitle class="text-xl">
						{currentStep === 1 ? 'اختيار العميل' :
						 currentStep === 2 ? 'اختيار الخدمة' :
						 currentStep === 3 ? 'تاريخ ووقت الموعد' :
						 currentStep === 4 ? 'تفاصيل الحجز' :
						 'مراجعة الحجز'}
					</CardTitle>
					<CardDescription>
						{currentStep === 1 ? 'ابحث عن عميل موجود أو أضف عميل جديد' :
						 currentStep === 2 ? 'اختر الخدمة المطلوبة من قائمة الخدمات المتاحة' :
						 currentStep === 3 ? 'حدد التاريخ والوقت المناسب للموعد' :
						 currentStep === 4 ? 'أضف تفاصيل إضافية وطريقة الحجز' :
						 'راجع جميع التفاصيل قبل تأكيد الحجز'}
					</CardDescription>
				</div>
			</div>
		</CardHeader>

		<CardContent class="space-y-6">
			{#if currentStep === 1}
				<!-- Step 1: Customer Selection -->
				<div class="space-y-6">
					<!-- Search existing customers -->
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<h3 class="text-lg font-semibold">البحث في العملاء الموجودين</h3>
							<Button variant="outline" size="sm" onclick={toggleNewCustomerForm} class="gap-2">
								<Plus class="w-4 h-4" />
								عميل جديد
							</Button>
						</div>
						
						<div class="relative">
							<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
							<Input
								type="text"
								placeholder="ابحث بالاسم أو رقم الهاتف..."
								bind:value={customerSearchQuery}
								class="pl-10 h-11"
								disabled={isSubmitting}
							/>
						</div>

						<!-- Customer list -->
						<div class="space-y-3 max-h-60 overflow-y-auto">
							{#each filteredCustomers as customer}
								<button
									type="button"
									onclick={() => selectCustomer(customer)}
									class="w-full p-4 rounded-lg border-2 transition-all duration-200 hover:scale-[1.02] {
										bookingForm.customer?.id === customer.id 
											? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20' 
											: 'border-border hover:border-indigo-300 bg-background'
									}"
									disabled={isSubmitting}
								>
									<div class="flex items-center gap-3">
										<div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/20 dark:to-purple-900/20 flex items-center justify-center">
											<User class="w-5 h-5 text-indigo-600" />
										</div>
										<div class="flex-1 text-right">
											<div class="flex items-center gap-2 justify-end">
												<h4 class="font-medium">{customer.name}</h4>
												{#if customer.isVip}
													<Badge class="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
														<Star class="w-3 h-3 mr-1" />
														VIP
													</Badge>
												{:else if customer.isRegular}
													<Badge variant="secondary">عميل دائم</Badge>
												{:else if customer.isNew}
													<Badge class="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">جديد</Badge>
												{/if}
											</div>
											<div class="flex items-center gap-4 text-sm text-muted-foreground justify-end">
												<span class="flex items-center gap-1">
													<Phone class="w-3 h-3" />
													{customer.phone}
												</span>
												{#if customer.email}
													<span class="flex items-center gap-1">
														<Mail class="w-3 h-3" />
														{customer.email}
													</span>
												{/if}
											</div>
										</div>
									</div>
								</button>
							{/each}
						</div>
					</div>

					<!-- Add new customer form -->
					{#if showNewCustomerForm}
						<div class="border-t pt-6">
							<h3 class="text-lg font-semibold mb-4">إضافة عميل جديد</h3>
							
							<div class="grid md:grid-cols-2 gap-4">
								<div class="space-y-2">
									<Label for="new-customer-name" class="text-sm font-medium flex items-center gap-2">
										اسم العميل <span class="text-destructive">*</span>
									</Label>
									<Input
										id="new-customer-name"
										type="text"
										placeholder="محمد أحمد علي"
										bind:value={bookingForm.newCustomer.name}
										class="h-11 {errors.customerName ? 'border-destructive' : ''}"
										disabled={isSubmitting}
									/>
									{#if errors.customerName}
										<p class="text-sm text-destructive">{errors.customerName}</p>
									{/if}
								</div>
								
								<div class="space-y-2">
									<Label for="new-customer-phone" class="text-sm font-medium flex items-center gap-2">
										رقم الهاتف <span class="text-destructive">*</span>
									</Label>
									<Input
										id="new-customer-phone"
										type="tel"
										placeholder="+966xxxxxxxxx"
										bind:value={bookingForm.newCustomer.phone}
										oninput={handlePhoneInput}
										class="h-11 {errors.customerPhone ? 'border-destructive' : ''}"
										disabled={isSubmitting}
									/>
									{#if errors.customerPhone}
										<p class="text-sm text-destructive">{errors.customerPhone}</p>
									{/if}
								</div>
								
								<div class="space-y-2 md:col-span-2">
									<Label for="new-customer-email" class="text-sm font-medium">
										البريد الإلكتروني (اختياري)
									</Label>
									<Input
										id="new-customer-email"
										type="email"
										placeholder="mohammed@example.com"
										bind:value={bookingForm.newCustomer.email}
										class="h-11"
										disabled={isSubmitting}
									/>
								</div>
							</div>
						</div>
					{/if}

					{#if errors.customer}
						<p class="text-sm text-destructive">{errors.customer}</p>
					{/if}
				</div>

			{:else if currentStep === 2}
				<!-- Step 2: Service Selection -->
				<div class="space-y-6">
					<div class="flex items-center gap-2">
						<Package class="w-5 h-5 text-indigo-600" />
						<h3 class="text-lg font-semibold">اختر الخدمة المطلوبة</h3>
					</div>
					
					<div class="grid md:grid-cols-2 gap-4">
						{#each availableServices as service}
							<button
								type="button"
								onclick={() => selectService(service)}
								class="p-6 rounded-xl border-2 transition-all duration-200 hover:scale-[1.02] {
									bookingForm.service?.id === service.id 
										? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20' 
										: 'border-border hover:border-indigo-300 bg-background'
								}"
								disabled={isSubmitting}
							>
								<div class="space-y-3">
									<div class="flex items-center justify-between">
										<h4 class="font-semibold text-right">{service.name}</h4>
										<Badge variant="outline">{service.category}</Badge>
									</div>
									
									<div class="flex items-center justify-between text-sm text-muted-foreground">
										<div class="flex items-center gap-1">
											<Clock class="w-3 h-3" />
											{formatDuration(service.duration)}
										</div>
										<div class="flex items-center gap-1 text-green-600 font-semibold">
											<DollarSign class="w-3 h-3" />
											{formatPrice(service.price)}
										</div>
									</div>
								</div>
							</button>
						{/each}
					</div>

					{#if bookingForm.service}
						<div class="bg-indigo-50 dark:bg-indigo-950/20 p-4 rounded-lg">
							<div class="flex items-center gap-2 mb-2">
								<CheckCircle class="w-4 h-4 text-indigo-600" />
								<span class="font-medium">الخدمة المحددة</span>
							</div>
							<div class="text-sm text-muted-foreground">
								{bookingForm.service.name} - {formatDuration(bookingForm.service.duration)} - {formatPrice(bookingForm.service.price)}
							</div>
						</div>
					{/if}

					{#if errors.service}
						<p class="text-sm text-destructive">{errors.service}</p>
					{/if}
				</div>

			{:else if currentStep === 3}
				<!-- Step 3: Date & Time Selection -->
				<div class="space-y-6">
					<!-- Date Selection -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Calendar class="w-5 h-5 text-blue-600" />
							<h3 class="text-lg font-semibold">اختر التاريخ</h3>
						</div>
						
						<div class="grid md:grid-cols-2 gap-4">
							<div class="space-y-2">
								<Label for="appointment-date" class="text-sm font-medium">تاريخ الموعد</Label>
								<Input
									id="appointment-date"
									type="date"
									min={today}
									bind:value={bookingForm.appointmentDate}
									class="h-11 {errors.date ? 'border-destructive' : ''}"
									disabled={isSubmitting}
								/>
								{#if errors.date}
									<p class="text-sm text-destructive">{errors.date}</p>
								{/if}
							</div>
							
							{#if bookingForm.appointmentDate}
								<div class="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
									<div class="text-sm text-muted-foreground mb-1">التاريخ المحدد</div>
									<div class="font-medium">{getDateText(bookingForm.appointmentDate)}</div>
								</div>
							{/if}
						</div>
					</div>

					<!-- Time Selection -->
					{#if bookingForm.appointmentDate}
						<div class="space-y-4">
							<div class="flex items-center gap-2">
								<Clock class="w-5 h-5 text-purple-600" />
								<h3 class="text-lg font-semibold">اختر الوقت</h3>
							</div>

							<div class="grid grid-cols-3 md:grid-cols-6 gap-2 max-h-60 overflow-y-auto">
								{#each selectedTimeSlots as timeSlot}
									<button
										type="button"
										onclick={() => selectTimeSlot(timeSlot)}
										disabled={!timeSlot.available || isSubmitting}
										class="p-3 rounded-lg border text-sm font-medium transition-all duration-200 {
											!timeSlot.available 
												? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed dark:border-gray-800 dark:bg-gray-900/20' 
												: bookingForm.appointmentTime === timeSlot.time 
													? 'border-purple-500 bg-purple-50 text-purple-700 dark:bg-purple-950/20 dark:text-purple-300' 
													: timeSlot.isRecommended 
														? 'border-green-300 bg-green-50 hover:border-green-400 dark:bg-green-950/20 dark:border-green-800' 
														: 'border-border hover:border-purple-300 bg-background'
										}"
									>
										{timeSlot.time}
										{#if timeSlot.isRecommended && timeSlot.available}
											<div class="text-xs text-green-600 mt-1">مُوصى</div>
										{/if}
									</button>
								{/each}
							</div>

							{#if errors.time}
								<p class="text-sm text-destructive">{errors.time}</p>
							{/if}

							{#if bookingForm.appointmentTime}
								<div class="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg">
									<div class="flex items-center gap-2 mb-2">
										<Timer class="w-4 h-4 text-purple-600" />
										<span class="font-medium">الموعد المحدد</span>
									</div>
									<div class="text-sm">
										{getDateText(bookingForm.appointmentDate)} في الساعة {bookingForm.appointmentTime}
									</div>
									{#if bookingForm.service}
										<div class="text-xs text-muted-foreground mt-1">
											مدة الخدمة: {formatDuration(bookingForm.service.duration)}
										</div>
									{/if}
								</div>
							{/if}
						</div>
					{/if}
				</div>

			{:else if currentStep === 4}
				<!-- Step 4: Booking Details -->
				<div class="space-y-6">
					<!-- Booking Method -->
					<div class="space-y-4">
						<div class="flex items-center gap-2">
							<Zap class="w-5 h-5 text-orange-600" />
							<h3 class="text-lg font-semibold">طريقة الحجز</h3>
						</div>
						
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							{#each bookingMethods as method}
								<button
									type="button"
									onclick={() => bookingForm.bookingMethod = method.value}
									class="p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 {
										bookingForm.bookingMethod === method.value 
											? 'border-orange-500 bg-orange-50 dark:bg-orange-950/20' 
											: 'border-border hover:border-orange-300'
									}"
									disabled={isSubmitting}
								>
									<div class="flex flex-col items-center gap-2">
										<span class="text-2xl">{method.icon}</span>
										<span class="text-sm font-medium">{method.label}</span>
										<span class="text-xs text-muted-foreground text-center">{method.description}</span>
									</div>
								</button>
							{/each}
						</div>
					</div>

					<!-- Additional Settings -->
					<div class="space-y-4">
						<h3 class="text-lg font-semibold">إعدادات إضافية</h3>
						
						<div class="space-y-4">
							<!-- Auto Confirm -->
							<div class="flex items-center justify-between p-4 bg-accent/20 rounded-lg">
								<div>
									<div class="font-medium">تأكيد تلقائي</div>
									<div class="text-sm text-muted-foreground">تأكيد الحجز تلقائياً دون انتظار موافقة</div>
								</div>
								<label class="relative inline-flex items-center cursor-pointer">
									<input
										type="checkbox"
										bind:checked={bookingForm.autoConfirm}
										class="sr-only peer"
										disabled={isSubmitting}
									/>
									<div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-600"></div>
								</label>
							</div>

							<!-- Reminder Settings -->
							<div class="flex items-center justify-between p-4 bg-accent/20 rounded-lg">
								<div>
									<div class="font-medium">تذكير العميل</div>
									<div class="text-sm text-muted-foreground">إرسال تذكير قبل الموعد بـ 24 ساعة</div>
								</div>
								<label class="relative inline-flex items-center cursor-pointer">
									<input
										type="checkbox"
										bind:checked={bookingForm.reminderSettings.enabled}
										class="sr-only peer"
										disabled={isSubmitting}
									/>
									<div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
								</label>
							</div>
						</div>
					</div>

					<!-- Notes -->
					<div class="space-y-2">
						<Label for="booking-notes" class="text-sm font-medium">ملاحظات الحجز</Label>
						<Textarea
							id="booking-notes"
							placeholder="أي ملاحظات خاصة بهذا الحجز..."
							bind:value={bookingForm.notes}
							class="min-h-20"
							disabled={isSubmitting}
						/>
					</div>

					{#if errors.method}
						<p class="text-sm text-destructive">{errors.method}</p>
					{/if}
				</div>

			{:else if currentStep === 5}
				<!-- Step 5: Review & Confirmation -->
				<div class="space-y-6">
					<div class="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20 p-6 rounded-xl">
						<div class="flex items-center gap-3 mb-4">
							<div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
								<Check class="w-4 h-4 text-green-600" />
							</div>
							<h3 class="text-lg font-semibold">مراجعة تفاصيل الحجز</h3>
						</div>
						
						<div class="grid md:grid-cols-2 gap-6">
							<!-- Customer Information -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">معلومات العميل</h4>
								{#if bookingForm.customer || bookingForm.newCustomer}
									{@const customer = bookingForm.customer || bookingForm.newCustomer}
									<div class="space-y-2">
										<div class="flex items-center gap-2">
											<User class="w-4 h-4 text-muted-foreground" />
											<span class="text-sm font-medium">{customer.name}</span>
										</div>
										<div class="flex items-center gap-2">
											<Phone class="w-4 h-4 text-muted-foreground" />
											<span class="text-sm font-medium">{customer.phone}</span>
										</div>
										{#if customer.email}
											<div class="flex items-center gap-2">
												<Mail class="w-4 h-4 text-muted-foreground" />
												<span class="text-sm font-medium">{customer.email}</span>
											</div>
										{/if}
									</div>
								{/if}
							</div>

							<!-- Service & Appointment -->
							<div class="space-y-3">
								<h4 class="font-medium text-muted-foreground">تفاصيل الموعد</h4>
								<div class="space-y-2">
									<div class="flex items-center gap-2">
										<Package class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{bookingForm.service?.name}</span>
									</div>
									<div class="flex items-center gap-2">
										<Calendar class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{getDateText(bookingForm.appointmentDate)}</span>
									</div>
									<div class="flex items-center gap-2">
										<Clock class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{bookingForm.appointmentTime}</span>
									</div>
									<div class="flex items-center gap-2">
										<Timer class="w-4 h-4 text-muted-foreground" />
										<span class="text-sm font-medium">{formatDuration(bookingForm.service?.duration || 0)}</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Price Summary -->
						<div class="mt-6 p-4 bg-white/50 dark:bg-gray-900/20 rounded-lg">
							<div class="flex justify-between items-center">
								<span class="font-medium">إجمالي التكلفة:</span>
								<span class="text-xl font-bold text-green-600">{formatPrice(bookingForm.service?.price || 0)}</span>
							</div>
						</div>

						<!-- Additional Details -->
						<div class="mt-4 grid md:grid-cols-2 gap-4 text-sm">
							<div class="flex justify-between">
								<span class="text-muted-foreground">طريقة الحجز:</span>
								<span>{bookingMethods.find(m => m.value === bookingForm.bookingMethod)?.label}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-muted-foreground">حالة الحجز:</span>
								<Badge variant={bookingForm.autoConfirm ? 'default' : 'secondary'}>
									{bookingForm.autoConfirm ? 'مؤكد' : 'قيد الانتظار'}
								</Badge>
							</div>
							<div class="flex justify-between">
								<span class="text-muted-foreground">التذكير:</span>
								<span>{bookingForm.reminderSettings.enabled ? 'مفعل' : 'معطل'}</span>
							</div>
						</div>

						{#if bookingForm.notes}
							<div class="mt-4 p-3 bg-accent/20 rounded-lg">
								<div class="text-sm text-muted-foreground mb-1">الملاحظات:</div>
								<div class="text-sm">{bookingForm.notes}</div>
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
						class="gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
					>
						التالي
						<ArrowRight class="w-4 h-4" />
					</Button>
				{:else}
					<Button
						onclick={handleSubmit}
						disabled={isSubmitting}
						class="gap-2 bg-gradient-to-r from-green-600 to-indigo-600 hover:from-green-700 hover:to-indigo-700"
					>
						{#if isSubmitting}
							<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
						{:else}
							<Check class="w-4 h-4" />
						{/if}
						تأكيد الحجز
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