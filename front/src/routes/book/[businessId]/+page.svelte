<script lang="ts">
	import { page } from '$app/stores';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.ts';
	import { Button } from '$lib/components/ui/button/index.ts';
	import { Input } from '$lib/components/ui/input/index.ts';
	import { Label } from '$lib/components/ui/label/index.ts';
	import Navbar from '$lib/components/navbar.svelte';
	import { api } from '$lib/services/api-client.ts';
	import { formatCurrency, formatTime } from '$lib/utils/index.js';
	import type { BookingForm, Service, BusinessProfile } from '$lib/types/index.js';
	import { onMount } from 'svelte';
	import { 
		MapPin, 
		Star, 
		Clock, 
		Phone, 
		User, 
		Mail, 
		Calendar,
		CheckCircle
	} from '@lucide/svelte';

	const businessId = parseInt($page.params.businessId);
	
	// State management
	let business = $state<BusinessProfile | null>(null);
	let availableServices = $state<Service[]>([]);
	let availableSlots = $state<string[]>([]);
	let selectedService = $state<Service | null>(null);
	let isLoading = $state(false);
	let isLoadingBusiness = $state(true);
	let isLoadingServices = $state(false);
	let isLoadingSlots = $state(false);
	let bookingComplete = $state(false);
	let bookingResult = $state<{ booking_id: string } | null>(null);
	let error = $state<string | null>(null);

	let bookingForm: BookingForm = $state({
		service_id: 0,
		customer: {
			name: '',
			phone_number: '',
			email: ''
		},
		appointment_date: '',
		appointment_time: '',
		notes: ''
	});

	// Load business profile and services on mount
	onMount(async () => {
		await loadBusinessData();
	});

	const loadBusinessData = async () => {
		isLoadingBusiness = true;
		error = null;

		try {
			// Note: For public booking, we would need a public business profile endpoint
			// For now, we'll need to check if such endpoint exists or handle gracefully
			console.log('Loading business data for ID:', businessId);
			
			// Load services using public API
			isLoadingServices = true;
			const servicesResponse = await api.public.getBusinessServices(businessId);
			
			if (servicesResponse.success && servicesResponse.data) {
				availableServices = servicesResponse.data;
			} else {
				error = 'فشل في تحميل الخدمات المتاحة';
				console.error('Failed to load services:', servicesResponse.error);
			}
		} catch (err) {
			error = 'حدث خطأ في تحميل البيانات';
			console.error('Error loading business data:', err);
		} finally {
			isLoadingBusiness = false;
			isLoadingServices = false;
		}
	};

	const selectService = async (service: Service) => {
		selectedService = service;
		bookingForm.service_id = service.id;
		
		// Load available slots for the selected service
		if (bookingForm.appointment_date) {
			await loadAvailableSlots(service.id, bookingForm.appointment_date);
		}
	};

	const loadAvailableSlots = async (serviceId: number, date: string) => {
		if (!serviceId || !date) return;

		isLoadingSlots = true;
		try {
			const response = await api.public.getAvailableSlots(businessId, serviceId, date);
			
			if (response.success && response.data) {
				availableSlots = response.data;
			} else {
				availableSlots = [];
				console.error('Failed to load available slots:', response.error);
			}
		} catch (err) {
			availableSlots = [];
			console.error('Error loading available slots:', err);
		} finally {
			isLoadingSlots = false;
		}
	};

	const handleDateChange = async () => {
		if (selectedService && bookingForm.appointment_date) {
			await loadAvailableSlots(selectedService.id, bookingForm.appointment_date);
		}
		// Reset selected time when date changes
		bookingForm.appointment_time = '';
	};

	const handleSubmit = async (e: Event) => {
		e.preventDefault();
		isLoading = true;
		error = null;

		try {
			const response = await api.public.createBooking({
				service_id: bookingForm.service_id,
				customer: bookingForm.customer,
				appointment_date: bookingForm.appointment_date,
				appointment_time: bookingForm.appointment_time,
				notes: bookingForm.notes || '',
				booking_method: 'online'
			});

			if (response.success && response.data) {
				bookingResult = response.data;
				bookingComplete = true;
			} else {
				error = response.error || 'فشل في إرسال الحجز';
			}
		} catch (err) {
			error = 'حدث خطأ أثناء الحجز';
			console.error('Booking error:', err);
		} finally {
			isLoading = false;
		}
	};

	// Generate next 14 days for date selection
	const getAvailableDates = () => {
		const dates = [];
		const today = new Date();
		for (let i = 1; i <= 14; i++) {
			const date = new Date(today);
			date.setDate(today.getDate() + i);
			dates.push({
				value: date.toISOString().split('T')[0],
				label: date.toLocaleDateString('ar-SA', { 
					weekday: 'long', 
					year: 'numeric', 
					month: 'long', 
					day: 'numeric' 
				})
			});
		}
		return dates;
	};

	const availableDates = getAvailableDates();

	// For now, create a mock business object since we don't have public business profile API
	$: if (availableServices.length > 0 && !business) {
		business = {
			id: businessId,
			name: `Business ${businessId}`,
			description: 'خدمات متميزة وجودة عالية',
			address: 'الرياض، المملكة العربية السعودية',
			phone: '+966123456789',
			rating: 4.8
		} as any;
	}
</script>

<svelte:head>
	<title>حجز موعد - {business?.description?.split(' ').slice(0, 3).join(' ')} | Wagtee</title>
	<meta name="description" content="احجز موعد في {business?.description}" />
</svelte:head>

{#if bookingComplete}
	<!-- Booking Success Page -->
	<div class="min-h-screen bg-background flex items-center justify-center p-4">
		<Card class="w-full max-w-md text-center">
			<CardHeader>
				<div class="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
					<CheckCircle class="w-8 h-8 text-green-600" />
				</div>
				<CardTitle class="text-2xl text-green-600">تم الحجز بنجاح!</CardTitle>
				<CardDescription>
					تم إرسال تفاصيل الحجز إلى رقم الهاتف المحدد
				</CardDescription>
			</CardHeader>
			<CardContent>
				<div class="bg-muted p-4 rounded-lg mb-6">
					<h3 class="font-semibold mb-2">تفاصيل الحجز:</h3>
					<div class="text-sm space-y-1">
						{#if bookingResult?.booking_id}
							<p><strong>رقم الحجز:</strong> {bookingResult.booking_id}</p>
						{/if}
						<p><strong>الخدمة:</strong> {selectedService?.name}</p>
						<p><strong>التاريخ:</strong> {bookingForm.appointment_date}</p>
						<p><strong>الوقت:</strong> {bookingForm.appointment_time}</p>
						<p><strong>السعر:</strong> {formatCurrency(selectedService?.price || 0)}</p>
					</div>
				</div>
				<div class="space-y-3">
					<Button class="w-full" onclick={() => window.location.href = '/'}>
						العودة إلى الصفحة الرئيسية
					</Button>
					<Button variant="outline" class="w-full" onclick={() => bookingComplete = false}>
						حجز موعد آخر
					</Button>
				</div>
			</CardContent>
		</Card>
	</div>
{:else}
	<div class="min-h-screen bg-background">
		<Navbar variant="landing" />

		<div class="container mx-auto px-4 py-8 max-w-4xl">
			{#if isLoadingBusiness}
				<div class="flex justify-center items-center min-h-[400px]">
					<div class="text-center">
						<div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
						<p class="text-muted-foreground">جاري تحميل البيانات...</p>
					</div>
				</div>
			{:else if error && !business}
				<Card>
					<CardContent class="text-center py-16">
						<h2 class="text-2xl font-semibold mb-4 text-destructive">حدث خطأ</h2>
						<p class="text-muted-foreground mb-6">{error}</p>
						<Button onclick={() => window.location.reload()}>
							إعادة المحاولة
						</Button>
					</CardContent>
				</Card>
			{:else if business}
				<!-- Business Information -->
				<Card class="mb-8">
					<CardHeader>
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<CardTitle class="text-2xl mb-2">
									{business.description?.split(' ').slice(0, 4).join(' ')}
								</CardTitle>
								<div class="flex items-center gap-4 text-sm text-muted-foreground mb-4">
									<div class="flex items-center gap-1">
										<MapPin class="w-4 h-4" />
										{business.address?.split(',').slice(0, 2).join(', ')}
									</div>
									<div class="flex items-center gap-1">
										<Star class="w-4 h-4 fill-yellow-400 text-yellow-400" />
										{business.rating} (125 تقييم)
									</div>
								</div>
								<p class="text-muted-foreground">{business.description}</p>
							</div>
							<div class="w-24 h-24 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-lg flex items-center justify-center">
								<Calendar class="w-8 h-8 text-primary" />
							</div>
						</div>
					</CardHeader>
				</Card>

				<div class="grid lg:grid-cols-3 gap-8">
					<!-- Services Selection -->
					<div class="lg:col-span-2 space-y-6">
						<!-- Step 1: Select Service -->
						<Card>
							<CardHeader>
								<CardTitle>اختر الخدمة</CardTitle>
								<CardDescription>اختر الخدمة التي تريد حجز موعد لها</CardDescription>
							</CardHeader>
							<CardContent>
								{#if isLoadingServices}
									<div class="flex justify-center py-8">
										<div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
									</div>
								{:else if availableServices.length === 0}
									<div class="text-center py-8 text-muted-foreground">
										لا توجد خدمات متاحة حالياً
									</div>
								{:else}
									<div class="grid gap-4">
										{#each availableServices as service}
											<button
												onclick={() => selectService(service)}
												class="p-4 border rounded-lg text-left hover:border-primary transition-colors {selectedService?.id === service.id ? 'border-primary bg-primary/5' : ''}"
											>
											<div class="flex items-center justify-between">
												<div>
													<h4 class="font-medium">{service.name}</h4>
													{#if service.description}
														<p class="text-sm text-muted-foreground mt-1">{service.description}</p>
													{/if}
													<div class="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
														<Clock class="w-3 h-3" />
														30 دقيقة
													</div>
												</div>
												<div class="text-right">
													<p class="font-semibold text-primary">{formatCurrency(service.price)}</p>
												</div>
											</div>
										</button>
									{/each}
								</div>
							{/if}
						</CardContent>
						</Card>

						<!-- Step 2: Booking Form -->
						{#if selectedService}
							<Card>
								<CardHeader>
									<CardTitle>تفاصيل الحجز</CardTitle>
									<CardDescription>أدخل تفاصيلك ووقت الموعد المطلوب</CardDescription>
								</CardHeader>
								<CardContent>
									<form onsubmit={handleSubmit} class="space-y-4">
										<!-- Customer Information -->
										<div class="grid md:grid-cols-2 gap-4">
											<div class="space-y-2">
												<Label for="name">الاسم الكامل</Label>
												<div class="relative">
													<User class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
													<Input
														id="name"
														type="text"
														placeholder="أدخل اسمك الكامل"
														bind:value={bookingForm.customer.name}
														class="pl-10"
														required
													/>
												</div>
											</div>
											<div class="space-y-2">
												<Label for="phone">رقم الهاتف</Label>
												<div class="relative">
													<Phone class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
													<Input
														id="phone"
														type="tel"
														placeholder="+966xxxxxxxxx"
														bind:value={bookingForm.customer.phone_number}
														class="pl-10"
														required
													/>
												</div>
											</div>
										</div>

										<div class="space-y-2">
											<Label for="email">البريد الإلكتروني (اختياري)</Label>
											<div class="relative">
												<Mail class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
												<Input
													id="email"
													type="email"
													placeholder="your@email.com"
													bind:value={bookingForm.customer.email}
													class="pl-10"
												/>
											</div>
										</div>

										<!-- Date & Time Selection -->
										<div class="grid md:grid-cols-2 gap-4">
											<div class="space-y-2">
												<Label for="date">تاريخ الموعد</Label>
												<select
													id="date"
													bind:value={bookingForm.appointment_date}
													on:change={handleDateChange}
													class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
													required
												>
													<option value="">اختر التاريخ</option>
													{#each availableDates as date}
														<option value={date.value}>{date.label}</option>
													{/each}
												</select>
											</div>
											<div class="space-y-2">
												<Label for="time">وقت الموعد</Label>
												<select
													id="time"
													bind:value={bookingForm.appointment_time}
													class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
													required
													disabled={!selectedService || !bookingForm.appointment_date || isLoadingSlots}
												>
													<option value="">
														{#if isLoadingSlots}
															جاري تحميل الأوقات المتاحة...
														{:else if !selectedService}
															اختر الخدمة أولاً
														{:else if !bookingForm.appointment_date}
															اختر التاريخ أولاً
														{:else}
															اختر الوقت
														{/if}
													</option>
													{#each availableSlots as time}
														<option value={time}>{formatTime(time)}</option>
													{/each}
												</select>
											</div>
										</div>

										<div class="space-y-2">
											<Label for="notes">ملاحظات إضافية (اختياري)</Label>
											<Input
												id="notes"
												type="text"
												placeholder="أي ملاحظات أو طلبات خاصة"
												bind:value={bookingForm.notes}
											/>
										</div>

										{#if error}
											<div class="p-4 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
												{error}
											</div>
										{/if}

										<Button 
											type="submit" 
											class="w-full" 
											disabled={isLoading || !bookingForm.customer.name || !bookingForm.customer.phone_number || !bookingForm.appointment_date || !bookingForm.appointment_time || !selectedService}
										>
											{#if isLoading}
												<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
											{/if}
											تأكيد الحجز
										</Button>
									</form>
								</CardContent>
							</Card>
						{/if}
					</div>

					<!-- Booking Summary -->
					{#if selectedService}
						<div>
							<Card class="sticky top-4">
								<CardHeader>
									<CardTitle>ملخص الحجز</CardTitle>
								</CardHeader>
								<CardContent>
									<div class="space-y-4">
										<div class="pb-4 border-b">
											<h4 class="font-medium">{selectedService.name}</h4>
											<p class="text-sm text-muted-foreground">{selectedService.description}</p>
											<div class="flex items-center justify-between mt-2">
												<span class="text-sm text-muted-foreground">المدة:</span>
												<span class="text-sm">30 دقيقة</span>
											</div>
										</div>
										
										{#if bookingForm.appointment_date}
											<div class="pb-4 border-b">
												<div class="flex items-center justify-between">
													<span class="text-sm text-muted-foreground">التاريخ:</span>
													<span class="text-sm">{availableDates.find(d => d.value === bookingForm.appointment_date)?.label.split(',')[0]}</span>
												</div>
												{#if bookingForm.appointment_time}
													<div class="flex items-center justify-between mt-1">
														<span class="text-sm text-muted-foreground">الوقت:</span>
														<span class="text-sm">{formatTime(bookingForm.appointment_time)}</span>
													</div>
												{/if}
											</div>
										{/if}

										<div class="pt-2">
											<div class="flex items-center justify-between text-lg font-semibold">
												<span>الإجمالي:</span>
												<span class="text-primary">{formatCurrency(selectedService.price)}</span>
											</div>
										</div>
									</div>
								</CardContent>
							</Card>
						</div>
					{/if}
				</div>
			{:else}
				<Card>
					<CardContent class="text-center py-16">
						<h2 class="text-2xl font-semibold mb-4">العمل التجاري غير موجود</h2>
						<p class="text-muted-foreground mb-6">لم نتمكن من العثور على العمل التجاري المطلوب</p>
						<Button onclick={() => window.location.href = '/'}>
							العودة إلى الصفحة الرئيسية
						</Button>
					</CardContent>
				</Card>
			{/if}
		</div>
	</div>
{/if}