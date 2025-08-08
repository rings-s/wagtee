<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs/index.js';
	import ModeToggle from '$lib/components/mode-toggle.svelte';
	
	import { 
		MapPin, 
		Clock, 
		Camera, 
		QrCode,
		Scissors,
		Car,
		Dumbbell,
		Image as ImageIcon,
		Sparkles,
		Brush,
		UserCheck,
		Calendar,
		Save,
		ArrowRight,
		Upload,
		X
	} from '@lucide/svelte';

	// Service types from backend models
	const serviceTypes = [
		{ value: 'barber', label: 'حلاق', labelEn: 'Barber', icon: Scissors, color: 'text-blue-600' },
		{ value: 'salon', label: 'صالون شعر', labelEn: 'Hair Salon', icon: Sparkles, color: 'text-pink-600' },
		{ value: 'beauty_center', label: 'مركز تجميل', labelEn: 'Beauty Center', icon: Brush, color: 'text-purple-600' },
		{ value: 'car_wash', label: 'غسيل سيارات', labelEn: 'Car Wash', icon: Car, color: 'text-blue-500' },
		{ value: 'cleaning', label: 'مركز تنظيف', labelEn: 'Cleaning Center', icon: Sparkles, color: 'text-green-600' },
		{ value: 'gym', label: 'نادي رياضي', labelEn: 'Gym', icon: Dumbbell, color: 'text-red-600' },
		{ value: 'photographer', label: 'مصور', labelEn: 'Photographer', icon: Camera, color: 'text-gray-600' },
		{ value: 'makeup_artist', label: 'خبيرة مكياج', labelEn: 'Makeup Artist', icon: Brush, color: 'text-pink-500' },
		{ value: 'bazar', label: 'بازار', labelEn: 'Bazar', icon: ImageIcon, color: 'text-yellow-600' },
		{ value: 'events', label: 'فعاليات', labelEn: 'Events', icon: Calendar, color: 'text-indigo-600' }
	];

	// Days of week for business hours
	const daysOfWeek = [
		{ value: 'saturday', label: 'السبت', labelEn: 'Saturday' },
		{ value: 'sunday', label: 'الأحد', labelEn: 'Sunday' },
		{ value: 'monday', label: 'الاثنين', labelEn: 'Monday' },
		{ value: 'tuesday', label: 'الثلاثاء', labelEn: 'Tuesday' },
		{ value: 'wednesday', label: 'الأربعاء', labelEn: 'Wednesday' },
		{ value: 'thursday', label: 'الخميس', labelEn: 'Thursday' },
		{ value: 'friday', label: 'الجمعة', labelEn: 'Friday' }
	];

	// Form state
	let activeStep = $state('basic');
	let businessProfile = $state({
		service_type: '',
		description: '',
		description_ar: '',
		address: '',
		address_ar: '',
		latitude: null,
		longitude: null,
		working_hours: {},
		images: [],
		is_active: true
	});

	let businessHours = $state(
		daysOfWeek.reduce((acc, day) => {
			acc[day.value] = {
				is_closed: false,
				open_time: '09:00',
				close_time: '18:00'
			};
			return acc;
		}, {} as Record<string, { is_closed: boolean; open_time: string; close_time: string }>)
	);

	let uploadedImages = $state<string[]>([]);

	// Computed properties
	const selectedServiceType = $derived(() => 
		serviceTypes.find(type => type.value === businessProfile.service_type)
	);

	const completedSteps = $derived(() => {
		const steps = [];
		if (businessProfile.service_type && businessProfile.description) steps.push('basic');
		if (businessProfile.address) steps.push('location');
		if (Object.values(businessHours).some(hours => !hours.is_closed)) steps.push('hours');
		return steps;
	});

	// Handlers
	const handleServiceTypeSelect = (serviceType: string) => {
		businessProfile.service_type = serviceType;
	};

	const handleImageUpload = (event: Event) => {
		const target = event.target as HTMLInputElement;
		const files = target.files;
		if (files) {
			Array.from(files).forEach(file => {
				const reader = new FileReader();
				reader.onload = (e) => {
					const result = e.target?.result as string;
					uploadedImages.push(result);
					businessProfile.images.push(result);
				};
				reader.readAsDataURL(file);
			});
		}
	};

	const removeImage = (index: number) => {
		uploadedImages.splice(index, 1);
		businessProfile.images.splice(index, 1);
	};

	const handleHoursChange = (day: string, field: string, value: string | boolean) => {
		businessHours[day] = { ...businessHours[day], [field]: value };
		businessProfile.working_hours = { ...businessHours };
	};

	const handleSave = () => {
		console.log('Saving business profile:', businessProfile);
		// In real app: call API to save business profile
		alert('تم حفظ بيانات العمل بنجاح!');
	};

	const handleGenerateQR = () => {
		console.log('Generating QR code for business');
		// In real app: call API to generate QR code
		alert('تم إنشاء رمز QR بنجاح!');
	};

	const nextStep = () => {
		const steps = ['basic', 'location', 'hours', 'images'];
		const currentIndex = steps.indexOf(activeStep);
		if (currentIndex < steps.length - 1) {
			activeStep = steps[currentIndex + 1];
		}
	};
</script>

<svelte:head>
	<title>إعداد العمل - Wagtee</title>
	<meta name="description" content="إعداد وتكوين بيانات عملك في منصة Wagtee" />
</svelte:head>

<div class="min-h-screen bg-background">
	<!-- Header -->
	<header class="border-b bg-card">
		<div class="container mx-auto px-4 py-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<h1 class="text-2xl font-bold text-primary">Wagtee</h1>
					<span class="text-sm text-muted-foreground">إعداد العمل</span>
				</div>
				<div class="flex items-center space-x-4">
					<ModeToggle />
					<Button variant="outline" href="/dashboard">
						العودة للوحة التحكم
					</Button>
				</div>
			</div>
		</div>
	</header>

	<div class="container mx-auto px-4 py-8">
		<!-- Progress Steps -->
		<div class="mb-8">
			<div class="flex items-center justify-between max-w-3xl mx-auto">
				{#each [
					{ id: 'basic', label: 'البيانات الأساسية', icon: UserCheck },
					{ id: 'location', label: 'الموقع', icon: MapPin },
					{ id: 'hours', label: 'ساعات العمل', icon: Clock },
					{ id: 'images', label: 'الصور', icon: Camera }
				] as step, index}
					{@const IconComponent = step.icon}
					<div class="flex items-center">
						<div class={`w-10 h-10 rounded-full flex items-center justify-center border-2 
							${completedSteps.includes(step.id) ? 'bg-green-600 border-green-600 text-white' : 
							  activeStep === step.id ? 'border-blue-600 text-blue-600' : 'border-gray-300 text-gray-400'}`}>
							<IconComponent class="w-5 h-5" />
						</div>
						<span class={`ml-2 text-sm ${activeStep === step.id ? 'font-medium' : 'text-muted-foreground'}`}>
							{step.label}
						</span>
						{#if index < 3}
							<div class={`w-16 h-0.5 mx-4 ${completedSteps.includes(step.id) ? 'bg-green-600' : 'bg-gray-300'}`}></div>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- Setup Form -->
		<div class="max-w-4xl mx-auto">
			<Tabs bind:value={activeStep}>
				<!-- Basic Information -->
				<TabsContent value="basic">
					<Card>
						<CardHeader>
							<CardTitle>البيانات الأساسية</CardTitle>
							<CardDescription>اختر نوع عملك وأدخل الوصف</CardDescription>
						</CardHeader>
						<CardContent class="space-y-6">
							<!-- Service Type Selection -->
							<div class="space-y-4">
								<Label class="text-base font-medium">نوع العمل</Label>
								<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
									{#each serviceTypes as type}
										{@const IconComponent = type.icon}
										<button
											onclick={() => handleServiceTypeSelect(type.value)}
											class={`p-4 rounded-lg border-2 text-center transition-all hover:shadow-md
												${businessProfile.service_type === type.value 
													? 'border-blue-600 bg-blue-50' 
													: 'border-gray-200 hover:border-gray-300'}`}
										>
											<IconComponent class="w-8 h-8 mx-auto mb-2 {type.color}" />
											<div class="text-sm font-medium">{type.label}</div>
											<div class="text-xs text-muted-foreground">{type.labelEn}</div>
										</button>
									{/each}
								</div>
								{#if selectedServiceType}
									<Badge variant="secondary" class="mt-2">
										تم اختيار: {selectedServiceType.label}
									</Badge>
								{/if}
							</div>

							<!-- Description -->
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div class="space-y-2">
									<Label for="description">وصف العمل (عربي)</Label>
									<textarea
										id="description"
										bind:value={businessProfile.description_ar}
										placeholder="اكتب وصفاً لعملك باللغة العربية..."
										class="min-h-24 flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
									></textarea>
								</div>
								<div class="space-y-2">
									<Label for="description_en">وصف العمل (إنجليزي)</Label>
									<textarea
										id="description_en"
										bind:value={businessProfile.description}
										placeholder="Write a description of your business in English..."
										class="min-h-24 flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
									></textarea>
								</div>
							</div>

							<div class="flex justify-end">
								<Button onclick={nextStep} disabled={!businessProfile.service_type || !businessProfile.description_ar}>
									التالي
									<ArrowRight class="w-4 h-4 mr-2" />
								</Button>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				<!-- Location -->
				<TabsContent value="location">
					<Card>
						<CardHeader>
							<CardTitle>معلومات الموقع</CardTitle>
							<CardDescription>أدخل عنوان عملك والموقع الجغرافي</CardDescription>
						</CardHeader>
						<CardContent class="space-y-6">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div class="space-y-2">
									<Label for="address_ar">العنوان (عربي)</Label>
									<textarea
										id="address_ar"
										bind:value={businessProfile.address_ar}
										placeholder="الرياض، حي النخيل، طريق الملك فهد..."
										class="min-h-20 flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
									></textarea>
								</div>
								<div class="space-y-2">
									<Label for="address_en">العنوان (إنجليزي)</Label>
									<textarea
										id="address_en"
										bind:value={businessProfile.address}
										placeholder="Riyadh, Al Nakheel District, King Fahd Road..."
										class="min-h-20 flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
									></textarea>
								</div>
							</div>

							<!-- Coordinates -->
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div class="space-y-2">
									<Label for="latitude">خط العرض</Label>
									<Input
										id="latitude"
										type="number"
										step="0.000001"
										bind:value={businessProfile.latitude}
										placeholder="24.7136"
									/>
								</div>
								<div class="space-y-2">
									<Label for="longitude">خط الطول</Label>
									<Input
										id="longitude"
										type="number"
										step="0.000001"
										bind:value={businessProfile.longitude}
										placeholder="46.6753"
									/>
								</div>
							</div>

							<div class="p-4 bg-blue-50 rounded-lg">
								<div class="flex items-center gap-3 mb-2">
									<MapPin class="w-5 h-5 text-blue-600" />
									<span class="font-medium text-blue-800">نصيحة</span>
								</div>
								<p class="text-sm text-blue-700">
									يمكنك الحصول على الإحداثيات من خرائط جوجل بالنقر على الموقع واختيار "نسخ الإحداثيات"
								</p>
							</div>

							<div class="flex justify-between">
								<Button variant="outline" onclick={() => activeStep = 'basic'}>
									السابق
								</Button>
								<Button onclick={nextStep} disabled={!businessProfile.address_ar}>
									التالي
									<ArrowRight class="w-4 h-4 mr-2" />
								</Button>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				<!-- Business Hours -->
				<TabsContent value="hours">
					<Card>
						<CardHeader>
							<CardTitle>ساعات العمل</CardTitle>
							<CardDescription>حدد ساعات عمل عملك لكل يوم من أيام الأسبوع</CardDescription>
						</CardHeader>
						<CardContent class="space-y-4">
							{#each daysOfWeek as day}
								<div class="flex items-center justify-between p-4 border rounded-lg">
									<div class="flex items-center gap-4">
										<span class="font-medium w-20">{day.label}</span>
										<label class="flex items-center gap-2">
											<input
												type="checkbox"
												bind:checked={businessHours[day.value].is_closed}
												onchange={(e) => handleHoursChange(day.value, 'is_closed', e.target.checked)}
											/>
											<span class="text-sm text-muted-foreground">مغلق</span>
										</label>
									</div>
									
									{#if !businessHours[day.value].is_closed}
										<div class="flex items-center gap-4">
											<div class="flex items-center gap-2">
												<Label class="text-sm">من</Label>
												<Input
													type="time"
													value={businessHours[day.value].open_time}
													onchange={(e) => handleHoursChange(day.value, 'open_time', e.target.value)}
													class="w-24"
												/>
											</div>
											<div class="flex items-center gap-2">
												<Label class="text-sm">إلى</Label>
												<Input
													type="time"
													value={businessHours[day.value].close_time}
													onchange={(e) => handleHoursChange(day.value, 'close_time', e.target.value)}
													class="w-24"
												/>
											</div>
										</div>
									{/if}
								</div>
							{/each}

							<div class="flex justify-between">
								<Button variant="outline" onclick={() => activeStep = 'location'}>
									السابق
								</Button>
								<Button onclick={nextStep}>
									التالي
									<ArrowRight class="w-4 h-4 mr-2" />
								</Button>
							</div>
						</CardContent>
					</Card>
				</TabsContent>

				<!-- Images -->
				<TabsContent value="images">
					<Card>
						<CardHeader>
							<CardTitle>صور العمل</CardTitle>
							<CardDescription>ارفع صور عملك لجذب العملاء</CardDescription>
						</CardHeader>
						<CardContent class="space-y-6">
							<!-- Upload Area -->
							<div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
								<Upload class="w-12 h-12 mx-auto mb-4 text-gray-400" />
								<h3 class="font-medium mb-2">ارفع صور عملك</h3>
								<p class="text-sm text-muted-foreground mb-4">
									اختر صور عالية الجودة لعرض خدماتك (JPG, PNG, حتى 5MB)
								</p>
								<input
									type="file"
									multiple
									accept="image/*"
									onchange={handleImageUpload}
									class="hidden"
									id="image-upload"
								/>
								<Button variant="outline" onclick={() => document.getElementById('image-upload')?.click()}>
									اختيار الصور
								</Button>
							</div>

							<!-- Uploaded Images -->
							{#if uploadedImages.length > 0}
								<div class="space-y-4">
									<h4 class="font-medium">الصور المرفوعة ({uploadedImages.length})</h4>
									<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
										{#each uploadedImages as image, index}
											<div class="relative group">
												<img src={image} alt="Business" class="w-full h-32 object-cover rounded-lg" />
												<button
													onclick={() => removeImage(index)}
													class="absolute top-2 right-2 w-6 h-6 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
												>
													<X class="w-4 h-4 mx-auto" />
												</button>
											</div>
										{/each}
									</div>
								</div>
							{/if}

							<div class="flex justify-between">
								<Button variant="outline" onclick={() => activeStep = 'hours'}>
									السابق
								</Button>
								<div class="flex gap-2">
									<Button variant="outline" onclick={handleGenerateQR}>
										<QrCode class="w-4 h-4 mr-2" />
										إنشاء رمز QR
									</Button>
									<Button onclick={handleSave}>
										<Save class="w-4 h-4 mr-2" />
										حفظ البيانات
									</Button>
								</div>
							</div>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>
		</div>
	</div>
</div>