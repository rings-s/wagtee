<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { publicService } from '$lib/services/api.js';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	
	import { 
		Search,
		MapPin,
		Star,
		Clock,
		Calendar,
		Phone,
		Filter,
		Scissors,
		Car,
		Dumbbell,
		Camera,
		Sparkles,
		Brush,
		UserCheck,
		Image as ImageIcon,
		Users,
		ChevronRight,
		QrCode,
		Heart,
		AlertCircle,
		Building,
		Crown,
		Zap
	} from '@lucide/svelte';

	// Service type icons mapping
	const serviceTypeIcons = {
		barber: Scissors,
		salon: Sparkles,
		beauty_center: Brush,
		car_wash: Car,
		cleaning: Sparkles,
		gym: Dumbbell,
		photographer: Camera,
		makeup_artist: Brush,
		bazar: ImageIcon,
		events: Calendar
	};

	// State
	let businesses = $state<any[]>([]);
	let filteredBusinesses = $state<any[]>([]);
	let isLoading = $state(true);
	let error = $state<string | null>(null);

	// Filter state
	let searchQuery = $state('');
	let selectedCity = $state('');
	let selectedServiceType = $state('');
	let priceRange = $state('all');
	let sortBy = $state('rating');

	// Saudi cities
	const saudiCities = [
		'الرياض', 'جدة', 'مكة المكرمة', 'المدينة المنورة', 'الدمام', 'الخبر', 
		'تبوك', 'بريدة', 'خميس مشيط', 'حائل', 'نجران', 'الجبيل', 'الطائف', 'ينبع'
	];

	// Load businesses (this would be replaced with actual API call when backend supports it)
	onMount(async () => {
		try {
			isLoading = true;
			error = null;

			// For now, we'll create mock data since the public business listing isn't implemented yet
			// In the real implementation, this would be: await publicService.getBusinesses()
			businesses = createMockBusinesses();
			applyFilters();

		} catch (err) {
			error = 'حدث خطأ في تحميل البيانات';
			console.error('Businesses load error:', err);
		} finally {
			isLoading = false;
		}
	});

	// Create mock businesses for demonstration
	const createMockBusinesses = () => {
		return [
			{
				id: 1,
				name: "صالون الأناقة",
				business_name: "صالون الأناقة",
				service_type: "salon",
				description: "أفضل خدمات العناية بالشعر والجمال",
				description_ar: "أفضل خدمات العناية بالشعر والجمال في الرياض",
				city: "الرياض",
				district: "العليا",
				address: "العليا، الرياض",
				phone_number: "+966501234567",
				rating: 4.8,
				total_reviews: 127,
				is_active: true,
				services: [
					{ id: 1, name: "قص شعر", price: 50, duration: 30 },
					{ id: 2, name: "صبغة شعر", price: 120, duration: 90 },
					{ id: 3, name: "تسريحة", price: 80, duration: 45 }
				]
			},
			{
				id: 2,
				name: "حلاق الملوك",
				business_name: "حلاق الملوك",
				service_type: "barber",
				description: "حلاقة رجالية احترافية",
				description_ar: "أفضل حلاقة رجالية في جدة مع خدمة احترافية",
				city: "جدة",
				district: "الحمراء",
				address: "الحمراء، جدة",
				phone_number: "+966507891234",
				rating: 4.9,
				total_reviews: 89,
				is_active: true,
				services: [
					{ id: 4, name: "حلاقة عادية", price: 25, duration: 20 },
					{ id: 5, name: "حلاقة وحلاقة ذقن", price: 35, duration: 30 },
					{ id: 6, name: "حلاقة كاملة", price: 45, duration: 45 }
				]
			},
			{
				id: 3,
				name: "مركز اللياقة الذهبي",
				business_name: "مركز اللياقة الذهبي",
				service_type: "gym",
				description: "نادي رياضي متكامل مع أحدث المعدات",
				description_ar: "نادي رياضي متكامل مع أحدث المعدات والمدربين المحترفين",
				city: "الدمام",
				district: "الفيصلية",
				address: "الفيصلية، الدمام",
				phone_number: "+966551234567",
				rating: 4.6,
				total_reviews: 234,
				is_active: true,
				services: [
					{ id: 7, name: "اشتراك يومي", price: 30, duration: 480 },
					{ id: 8, name: "جلسة مدرب شخصي", price: 80, duration: 60 },
					{ id: 9, name: "اشتراك أسبوعي", price: 150, duration: 7 }
				]
			},
			{
				id: 4,
				name: "غسيل السرعة",
				business_name: "غسيل السرعة",
				service_type: "car_wash",
				description: "غسيل سيارات سريع ومميز",
				description_ar: "أفضل خدمات غسيل السيارات مع التنظيف الداخلي والخارجي",
				city: "الرياض",
				district: "الملز",
				address: "الملز، الرياض",
				phone_number: "+966556789012",
				rating: 4.4,
				total_reviews: 156,
				is_active: true,
				services: [
					{ id: 10, name: "غسيل خارجي", price: 20, duration: 15 },
					{ id: 11, name: "غسيل شامل", price: 45, duration: 45 },
					{ id: 12, name: "تنظيف داخلي", price: 35, duration: 30 }
				]
			}
		];
	};

	// Apply filters function
	const applyFilters = () => {
		let filtered = [...businesses];

		// Search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(business => 
				business.name.toLowerCase().includes(query) ||
				business.description_ar?.toLowerCase().includes(query) ||
				business.city?.toLowerCase().includes(query) ||
				business.district?.toLowerCase().includes(query)
			);
		}

		// City filter
		if (selectedCity) {
			filtered = filtered.filter(business => 
				business.city === selectedCity
			);
		}

		// Service type filter
		if (selectedServiceType) {
			filtered = filtered.filter(business => 
				business.service_type === selectedServiceType
			);
		}

		// Price range filter
		if (priceRange !== 'all') {
			filtered = filtered.filter(business => {
				const businessServices = business.services || [];
				return businessServices.some(service => {
					switch (priceRange) {
						case 'low': return service.price <= 30;
						case 'medium': return service.price > 30 && service.price <= 60;
						case 'high': return service.price > 60;
						default: return true;
					}
				});
			});
		}

		// Sort
		switch (sortBy) {
			case 'rating':
				filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
				break;
			case 'price_low':
				filtered.sort((a, b) => {
					const aMinPrice = Math.min(...(a.services?.map(s => s.price) || [0]));
					const bMinPrice = Math.min(...(b.services?.map(s => s.price) || [0]));
					return aMinPrice - bMinPrice;
				});
				break;
			case 'price_high':
				filtered.sort((a, b) => {
					const aMaxPrice = Math.max(...(a.services?.map(s => s.price) || [0]));
					const bMaxPrice = Math.max(...(b.services?.map(s => s.price) || [0]));
					return bMaxPrice - aMaxPrice;
				});
				break;
			case 'name':
				filtered.sort((a, b) => a.name.localeCompare(b.name, 'ar'));
				break;
		}

		filteredBusinesses = filtered;
	};

	// Watch for filter changes
	$effect(() => {
		if (businesses.length > 0) {
			applyFilters();
		}
	});

	// Format currency (Saudi Riyal)
	const formatCurrency = (amount: number) => {
		return new Intl.NumberFormat('ar-SA', {
			style: 'currency',
			currency: 'SAR',
			minimumFractionDigits: 0
		}).format(amount);
	};

	// Get service type label
	const getServiceTypeLabel = (type: string) => {
		const labels = {
			barber: 'حلاق',
			salon: 'صالون شعر',
			beauty_center: 'مركز تجميل',
			car_wash: 'غسيل سيارات',
			cleaning: 'مركز تنظيف',
			gym: 'نادي رياضي',
			photographer: 'مصور',
			makeup_artist: 'خبيرة مكياج',
			bazar: 'بازار',
			events: 'فعاليات'
		};
		return labels[type] || type;
	};

	// Handle booking
	const handleBookNow = (businessId: number) => {
		goto(`/book/${businessId}`);
	};

	// Handle favorite (store in localStorage for now)
	const handleFavorite = (businessId: number) => {
		try {
			const favorites = JSON.parse(localStorage.getItem('wagtee_favorites') || '[]');
			const index = favorites.indexOf(businessId);
			
			if (index === -1) {
				favorites.push(businessId);
			} else {
				favorites.splice(index, 1);
			}
			
			localStorage.setItem('wagtee_favorites', JSON.stringify(favorites));
		} catch (err) {
			console.error('Error managing favorites:', err);
		}
	};

	// Check if business is favorite
	const isFavorite = (businessId: number) => {
		try {
			const favorites = JSON.parse(localStorage.getItem('wagtee_favorites') || '[]');
			return favorites.includes(businessId);
		} catch {
			return false;
		}
	};

	// Clear all filters
	const clearFilters = () => {
		searchQuery = '';
		selectedCity = '';
		selectedServiceType = '';
		priceRange = 'all';
		sortBy = 'rating';
	};
</script>

<svelte:head>
	<title>احجز الآن - Wagtee</title>
	<meta name="description" content="اكتشف واحجز خدمات الأعمال المحلية في السعودية عبر منصة Wagtee" />
</svelte:head>

<div class="min-h-screen bg-background">
	<!-- Responsive Navbar -->
	<Navbar variant="public" />

	<!-- Hero Search Section -->
	<section class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 py-12">
		<div class="container mx-auto px-4">
			<div class="max-w-4xl mx-auto text-center">
				<h2 class="text-4xl font-bold mb-4">اكتشف واحجز خدمتك المفضلة</h2>
				<p class="text-xl text-muted-foreground mb-8">
					آلاف الخدمات المميزة في انتظارك - احجز بسهولة وبسرعة
				</p>

				<!-- Search Bar -->
				<div class="relative max-w-2xl mx-auto mb-8">
					<Search class="absolute left-4 top-4 h-5 w-5 text-muted-foreground" />
					<Input
						placeholder="ابحث عن خدمة، عمل، أو موقع..."
						bind:value={searchQuery}
						class="pl-12 pr-4 py-6 text-lg"
					/>
				</div>

				<!-- Quick Filters -->
				<div class="flex items-center justify-center gap-4 flex-wrap">
					{#each [
						{ value: '', label: 'الكل', icon: Users },
						{ value: 'barber', label: 'حلاقة', icon: Scissors },
						{ value: 'salon', label: 'صالونات', icon: Sparkles },
						{ value: 'car_wash', label: 'غسيل سيارات', icon: Car },
						{ value: 'gym', label: 'رياضة', icon: Dumbbell }
					] as quickFilter}
						<Button
							variant={selectedServiceType === quickFilter.value ? 'default' : 'outline'}
							size="sm"
							onclick={() => selectedServiceType = quickFilter.value}
						>
							{@const IconComponent = quickFilter.icon}
							<IconComponent class="w-4 h-4 mr-2" />
							{quickFilter.label}
						</Button>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<div class="container mx-auto px-4 py-8">
		{#if isLoading}
			<!-- Loading State -->
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
					<p class="text-muted-foreground">جار تحميل الأعمال...</p>
				</div>
			</div>
		{:else if error}
			<!-- Error State -->
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<AlertCircle class="w-12 h-12 text-destructive mx-auto mb-4" />
					<h3 class="text-lg font-semibold mb-2">حدث خطأ</h3>
					<p class="text-muted-foreground mb-4">{error}</p>
					<Button onclick={() => window.location.reload()}>إعادة التحميل</Button>
				</div>
			</div>
		{:else}
			<div class="flex gap-8">
				<!-- Filters Sidebar -->
				<div class="w-80 flex-shrink-0 hidden lg:block">
					<Card class="sticky top-24">
						<CardHeader>
							<CardTitle class="flex items-center gap-2">
								<Filter class="w-5 h-5" />
								تصفية النتائج
							</CardTitle>
						</CardHeader>
						<CardContent class="space-y-6">
							<!-- City Filter -->
							<div class="space-y-2">
								<Label>المدينة</Label>
								<select bind:value={selectedCity} class="w-full px-3 py-2 border border-input rounded-md bg-background">
									<option value="">جميع المدن</option>
									{#each saudiCities as city}
										<option value={city}>{city}</option>
									{/each}
								</select>
							</div>

							<!-- Service Type Filter -->
							<div class="space-y-2">
								<Label>نوع الخدمة</Label>
								<select bind:value={selectedServiceType} class="w-full px-3 py-2 border border-input rounded-md bg-background">
									<option value="">جميع الخدمات</option>
									<option value="barber">حلاق</option>
									<option value="salon">صالون شعر</option>
									<option value="beauty_center">مركز تجميل</option>
									<option value="car_wash">غسيل سيارات</option>
									<option value="cleaning">تنظيف</option>
									<option value="gym">نادي رياضي</option>
									<option value="photographer">تصوير</option>
									<option value="makeup_artist">مكياج</option>
								</select>
							</div>

							<!-- Price Range Filter -->
							<div class="space-y-2">
								<Label>نطاق السعر</Label>
								<select bind:value={priceRange} class="w-full px-3 py-2 border border-input rounded-md bg-background">
									<option value="all">جميع الأسعار</option>
									<option value="low">أقل من 30 ريال</option>
									<option value="medium">30 - 60 ريال</option>
									<option value="high">أكثر من 60 ريال</option>
								</select>
							</div>

							<!-- Sort Options -->
							<div class="space-y-2">
								<Label>ترتيب حسب</Label>
								<select bind:value={sortBy} class="w-full px-3 py-2 border border-input rounded-md bg-background">
									<option value="rating">الأعلى تقييماً</option>
									<option value="price_low">السعر من الأقل للأعلى</option>
									<option value="price_high">السعر من الأعلى للأقل</option>
									<option value="name">الاسم أبجدياً</option>
								</select>
							</div>

							<!-- Clear Filters -->
							<Button variant="outline" class="w-full" onclick={clearFilters}>
								مسح جميع المرشحات
							</Button>
						</CardContent>
					</Card>
				</div>

				<!-- Results -->
				<div class="flex-1">
					<!-- Results Header -->
					<div class="flex items-center justify-between mb-6">
						<div>
							<h3 class="text-2xl font-bold">نتائج البحث</h3>
							<p class="text-muted-foreground">
								تم العثور على {filteredBusinesses.length} نتيجة
							</p>
						</div>
						
						<!-- Mobile Filter Button -->
						<Button variant="outline" class="lg:hidden">
							<Filter class="w-4 h-4 mr-2" />
							تصفية
						</Button>
					</div>

					<!-- Business Cards -->
					<div class="space-y-6">
						{#each filteredBusinesses as business}
							{@const businessServices = business.services || []}
							{@const minPrice = businessServices.length > 0 ? Math.min(...businessServices.map(s => s.price)) : 0}
							{@const maxPrice = businessServices.length > 0 ? Math.max(...businessServices.map(s => s.price)) : 0}
							{@const IconComponent = serviceTypeIcons[business.service_type] || Building}
							
							<Card class="overflow-hidden hover:shadow-lg transition-shadow">
								<div class="flex flex-col md:flex-row">
									<!-- Business Image -->
									<div class="w-full md:w-64 h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 flex items-center justify-center flex-shrink-0">
										<IconComponent class="w-16 h-16 text-blue-600" />
									</div>

									<!-- Business Info -->
									<div class="flex-1 p-6">
										<div class="flex items-start justify-between mb-4">
											<div class="flex-1">
												<div class="flex items-center gap-3 mb-2">
													<h4 class="text-xl font-bold">{business.name}</h4>
													<Badge variant="secondary">
														{getServiceTypeLabel(business.service_type)}
													</Badge>
												</div>
												<div class="flex items-center gap-4 text-sm text-muted-foreground mb-2">
													<div class="flex items-center gap-1">
														<Star class="w-4 h-4 fill-yellow-400 text-yellow-400" />
														<span class="font-medium">{business.rating || 4.5}</span>
														<span>({business.total_reviews || 0} تقييم)</span>
													</div>
													<div class="flex items-center gap-1">
														<MapPin class="w-4 h-4" />
														<span>{business.city}</span>
														{#if business.district}
															<span>- {business.district}</span>
														{/if}
													</div>
													{#if business.phone_number}
														<div class="flex items-center gap-1">
															<Phone class="w-4 h-4" />
															<span>{business.phone_number}</span>
														</div>
													{/if}
												</div>
												<p class="text-muted-foreground line-clamp-2 max-w-2xl">
													{business.description_ar || business.description}
												</p>
											</div>
											
											<button 
												onclick={() => handleFavorite(business.id)} 
												class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
											>
												<Heart class="w-5 h-5 {isFavorite(business.id) ? 'text-red-500 fill-red-500' : 'text-gray-400 hover:text-red-500'}" />
											</button>
										</div>

										<!-- Services Preview -->
										{#if businessServices.length > 0}
											<div class="mb-4">
												<h5 class="font-medium mb-2">الخدمات المتاحة:</h5>
												<div class="flex items-center gap-2 flex-wrap">
													{#each businessServices.slice(0, 3) as service}
														<Badge variant="outline" class="text-xs">
															{service.name} - {formatCurrency(service.price)}
														</Badge>
													{/each}
													{#if businessServices.length > 3}
														<Badge variant="secondary" class="text-xs">
															+{businessServices.length - 3} أخرى
														</Badge>
													{/if}
												</div>
											</div>
										{/if}

										<!-- Action Buttons -->
										<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
											{#if businessServices.length > 0}
												<div class="text-sm text-muted-foreground">
													<span class="font-medium">الأسعار تبدأ من:</span>
													<span class="text-lg font-bold text-green-600 mr-2">
														{formatCurrency(minPrice)}
													</span>
													{#if minPrice !== maxPrice}
														<span class="text-muted-foreground">- {formatCurrency(maxPrice)}</span>
													{/if}
												</div>
											{/if}
											
											<div class="flex items-center gap-3">
												<Button variant="outline" size="sm" onclick={() => goto(`/business/${business.id}`)}>
													عرض التفاصيل
												</Button>
												<Button onclick={() => handleBookNow(business.id)}>
													احجز الآن
													<ChevronRight class="w-4 h-4 mr-2" />
												</Button>
											</div>
										</div>
									</div>
								</div>
							</Card>
						{/each}

						{#if filteredBusinesses.length === 0}
							<div class="text-center py-12">
								<Search class="w-16 h-16 mx-auto mb-4 text-gray-400" />
								<h3 class="text-xl font-medium mb-2">لم نجد نتائج</h3>
								<p class="text-muted-foreground mb-4">جرب تعديل معايير البحث أو التصفية</p>
								<Button onclick={clearFilters}>مسح جميع المرشحات</Button>
							</div>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- QR Code Section -->
	<section class="bg-gray-50 dark:bg-gray-900/20 py-12">
		<div class="container mx-auto px-4 text-center">
			<QrCode class="w-16 h-16 mx-auto mb-4 text-blue-600" />
			<h3 class="text-2xl font-bold mb-4">احجز بسرعة مع رمز QR</h3>
			<p class="text-muted-foreground mb-6 max-w-2xl mx-auto">
				امسح رمز QR الموجود في المحل للحجز السريع دون الحاجة لإدخال بيانات
			</p>
			<Button variant="outline" size="lg" onclick={() => goto('/book/qr')}>
				<QrCode class="w-5 h-5 mr-2" />
				مسح رمز QR
			</Button>
		</div>
	</section>
</div>