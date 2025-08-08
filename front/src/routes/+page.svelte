<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	
	import { 
		Search,
		Filter,
		MapPin, 
		Star, 
		Clock,
		Users,
		Smartphone,
		Shield,
		Bell,
		QrCode,
		CreditCard,
		TrendingUp,
		CheckCircle,
		ArrowRight,
		MessageCircle,
		BarChart3,
		Globe,
		Crown,
		Zap,
		Scissors,
		Car,
		Dumbbell,
		Camera,
		Sparkles,
		Calendar,
		Heart,
		SlidersHorizontal,
		X,
		ChevronDown,
		Layers,
		Verified,
		ThumbsUp,
		Eye,
		Play
	} from '@lucide/svelte';

	import { formatCurrency } from '$lib/utils/index.js';
	import { api } from '$lib/services/api-client.js';
	import { onMount } from 'svelte';

	// Advanced search and filtering state
	let searchQuery = $state('');
	let selectedCity = $state('all');
	let businessData = $state([]);
	let servicesData = $state([]);
	let isLoading = $state(false);
	let error = $state(null);
	let selectedCategory = $state('all');
	let selectedRating = $state('all');
	let showFilters = $state(false);
	let selectedTags = $state([]);

	// Service categories with enhanced data
	const serviceCategories = [
		{ 
			id: 'barber', 
			name: 'حلاقة رجالية', 
			icon: Scissors, 
			color: 'text-blue-600',
			bgColor: 'bg-blue-50',
			gradient: 'from-blue-500 to-indigo-600',
			count: 45,
			trending: true
		},
		{ 
			id: 'salon', 
			name: 'صالونات نسائية', 
			icon: Sparkles, 
			color: 'text-pink-600',
			bgColor: 'bg-pink-50',
			gradient: 'from-pink-500 to-rose-600',
			count: 38,
			trending: true
		},
		{ 
			id: 'car_wash', 
			name: 'غسيل سيارات', 
			icon: Car, 
			color: 'text-green-600',
			bgColor: 'bg-green-50',
			gradient: 'from-green-500 to-emerald-600',
			count: 29,
			trending: false
		},
		{ 
			id: 'gym', 
			name: 'نوادي رياضية', 
			icon: Dumbbell, 
			color: 'text-red-600',
			bgColor: 'bg-red-50',
			gradient: 'from-red-500 to-orange-600',
			count: 22,
			trending: true
		},
		{ 
			id: 'photography', 
			name: 'تصوير احترافي', 
			icon: Camera, 
			color: 'text-purple-600',
			bgColor: 'bg-purple-50',
			gradient: 'from-purple-500 to-violet-600',
			count: 18,
			trending: false
		},
		{ 
			id: 'beauty', 
			name: 'مراكز تجميل', 
			icon: Heart, 
			color: 'text-indigo-600',
			bgColor: 'bg-indigo-50',
			gradient: 'from-indigo-500 to-blue-600',
			count: 31,
			trending: true
		}
	];

	// Saudi cities with enhanced data
	const saudiCities = [
		{ id: 'riyadh', name: 'الرياض', count: 89, popular: true },
		{ id: 'jeddah', name: 'جدة', count: 67, popular: true },
		{ id: 'dammam', name: 'الدمام', count: 34, popular: true },
		{ id: 'khobar', name: 'الخبر', count: 28, popular: false },
		{ id: 'mecca', name: 'مكة المكرمة', count: 42, popular: true },
		{ id: 'medina', name: 'المدينة المنورة', count: 31, popular: false },
		{ id: 'taif', name: 'الطائف', count: 19, popular: false },
		{ id: 'tabuk', name: 'تبوك', count: 15, popular: false }
	];

	// Popular search tags
	const popularTags = [
		'قريب مني', 'متاح الآن', 'تقييم عالي', 'أسعار مناسبة', 
		'حجز فوري', 'دفع إلكتروني', 'خدمة منزلية', 'احترافي'
	];

	// Featured businesses with enhanced data
	const featuredBusinesses = [
		{
			id: 1,
			name: 'صالون النخبة للرجال',
			category: 'barber',
			city: 'riyadh',
			rating: 4.9,
			reviews: 234,
			image: '/placeholder-barber.jpg',
			services: ['قص شعر', 'حلاقة ذقن', 'تصفيف'],
			price_range: '25-80',
			badges: ['verified', 'trending', 'top_rated'],
			next_available: '15 دقيقة',
			description: 'أفضل صالون حلاقة رجالية في الرياض مع خدمات متميزة',
			features: ['واي فاي مجاني', 'موقف سيارات', 'خدمة VIP']
		},
		{
			id: 2,
			name: 'استوديو الجمال الملكي',
			category: 'salon',
			city: 'jeddah',
			rating: 4.8,
			reviews: 189,
			image: '/placeholder-salon.jpg',
			services: ['تصفيف الشعر', 'مكياج', 'عناية البشرة'],
			price_range: '150-500',
			badges: ['verified', 'premium'],
			next_available: '30 دقيقة',
			description: 'صالون نسائي راقي متخصص في أحدث صيحات الموضة',
			features: ['منطقة استقبال مريحة', 'مستحضرات عالمية', 'خصوصية تامة']
		},
		{
			id: 3,
			name: 'نادي اللياقة المتقدم',
			category: 'gym',
			city: 'riyadh',
			rating: 4.7,
			reviews: 312,
			image: '/placeholder-gym.jpg',
			services: ['تدريب شخصي', 'تمارين جماعية', 'تغذية رياضية'],
			price_range: '200-400',
			badges: ['verified', 'equipment_modern'],
			next_available: 'متاح الآن',
			description: 'نادي رياضي حديث مع أحدث الأجهزة والمدربين المحترفين',
			features: ['أجهزة حديثة', 'مدربين معتمدين', 'خطط تغذية']
		}
	];

	// Load real data from Django API
	async function loadBusinesses() {
		isLoading = true;
		error = null;
		
		try {
			console.log('Loading real businesses and services from API...');
			
			// Load businesses and services in parallel
			const [businessesResponse, servicesResponse] = await Promise.all([
				api.public.getBusinesses(),
				api.public.getAllServices()
			]);
			
			// Process businesses data
			if (businessesResponse.success && businessesResponse.data) {
				businessData = businessesResponse.data.map(business => ({
					id: business.id,
					name: business.business_name || business.name,
					category: business.business_type || 'barber',
					city: business.city || 'riyadh',
					rating: business.average_rating || 4.8,
					reviews: business.total_reviews || 0,
					image: '/placeholder-business.jpg',
					services: Array.isArray(business.services) ? business.services : ['خدمة عامة'],
					price_range: business.price_range || '50-200',
					badges: ['verified'],
					next_available: 'متاح الآن',
					description: business.description || business.business_name,
					features: ['خدمة احترافية', 'جودة عالية'],
					phone_number: business.phone_number,
					email: business.email,
					district: business.district,
					address: business.address
				}));
				console.log(`✅ Loaded ${businessData.length} real businesses from API`);
			} else {
				console.warn('⚠️ No businesses data received, using fallback:', businessesResponse);
				businessData = featuredBusinesses; // Fallback
			}
			
			// Process services data
			if (servicesResponse.success && servicesResponse.data) {
				servicesData = servicesResponse.data;
				console.log(`✅ Loaded ${servicesData.length} real services from API`);
			} else {
				console.warn('⚠️ No services data received:', servicesResponse);
			}
			
		} catch (err) {
			console.error('❌ Failed to load real data from API:', err);
			error = 'فشل في تحميل البيانات من الخادم - يرجى المحاولة لاحقاً';
			// Use fallback data
			businessData = featuredBusinesses;
		} finally {
			isLoading = false;
		}
	}

	// Load data on component mount
	onMount(() => {
		loadBusinesses();
	});

	// Advanced search functionality
	const filteredBusinesses = $derived(() => {
		let filtered = businessData.length > 0 ? businessData : featuredBusinesses;

		// Search by name
		if (searchQuery.trim()) {
			filtered = filtered.filter(business => 
				business.name.includes(searchQuery) || 
				business.description.includes(searchQuery) ||
				business.services.some(service => service.includes(searchQuery))
			);
		}

		// Filter by city
		if (selectedCity !== 'all') {
			filtered = filtered.filter(business => business.city === selectedCity);
		}

		// Filter by category
		if (selectedCategory !== 'all') {
			filtered = filtered.filter(business => business.category === selectedCategory);
		}

		// Filter by rating
		if (selectedRating !== 'all') {
			const rating = parseFloat(selectedRating);
			filtered = filtered.filter(business => business.rating >= rating);
		}

		// Filter by tags
		if (selectedTags.length > 0) {
			filtered = filtered.filter(business => {
				return selectedTags.some(tag => {
					if (tag === 'قريب مني') return business.city === 'riyadh'; // Example logic
					if (tag === 'متاح الآن') return business.next_available === 'متاح الآن';
					if (tag === 'تقييم عالي') return business.rating >= 4.8;
					if (tag === 'احترافي') return business.badges.includes('verified');
					return true;
				});
			});
		}

		return filtered;
	});

	// Tag management
	const toggleTag = (tag: string) => {
		if (selectedTags.includes(tag)) {
			selectedTags = selectedTags.filter(t => t !== tag);
		} else {
			selectedTags = [...selectedTags, tag];
		}
	};

	const clearAllFilters = () => {
		searchQuery = '';
		selectedCity = 'all';
		selectedCategory = 'all';
		selectedRating = 'all';
		selectedTags = [];
	};

	// Premium features data
	const premiumFeatures = [
		{
			icon: Search,
			title: 'بحث ذكي وتصفية متقدمة',
			description: 'اعثر على الخدمة المثالية بسهولة مع خوارزميات البحث الذكية والتصفية المتقدمة',
			color: 'text-blue-600',
			bgColor: 'bg-blue-50',
			demo: true
		},
		{
			icon: MapPin,
			title: 'خرائط تفاعلية ومواقع دقيقة',
			description: 'تحديد الموقع الدقيق لكل خدمة مع خرائط تفاعلية وحساب المسافات',
			color: 'text-green-600',
			bgColor: 'bg-green-50',
			demo: false
		},
		{
			icon: Calendar,
			title: 'حجز فوري ومرن',
			description: 'احجز موعدك على الفور أو اختر وقتاً مناسباً مع نظام المواعيد المرن',
			color: 'text-purple-600',
			bgColor: 'bg-purple-50',
			demo: true
		},
		{
			icon: MessageCircle,
			title: 'إشعارات واتساب الذكية',
			description: 'تأكيد الحجوزات وتذكيرات المواعيد عبر واتساب مع رسائل مخصصة',
			color: 'text-green-600',
			bgColor: 'bg-green-50',
			demo: false
		},
		{
			icon: Star,
			title: 'نظام تقييم شامل',
			description: 'تقييمات موثوقة من العملاء الحقيقيين مع تحليلات تفصيلية للجودة',
			color: 'text-yellow-600',
			bgColor: 'bg-yellow-50',
			demo: false
		},
		{
			icon: Shield,
			title: 'أمان وخصوصية متقدمة',
			description: 'حماية بياناتك مع أعلى معايير الأمان والخصوصية في السوق السعودي',
			color: 'text-red-600',
			bgColor: 'bg-red-50',
			demo: false
		}
	];

	// Stats with enhanced animation
	const stats = [
		{ number: '2500+', label: 'مقدم خدمة مميز', icon: Verified },
		{ number: '150K+', label: 'حجز ناجح شهرياً', icon: Calendar },
		{ number: '4.9/5', label: 'متوسط تقييم العملاء', icon: Star },
		{ number: '99.9%', label: 'معدل الموثوقية', icon: Shield }
	];
</script>

<svelte:head>
	<title>Wagtee - أفضل منصة حجوزات في السعودية | بحث ذكي وخدمات متميزة</title>
	<meta name="description" content="اكتشف وأحجز أفضل الخدمات في السعودية مع Wagtee. بحث ذكي، تصفية متقدمة، وحجز فوري لأكثر من 2500 مقدم خدمة موثوق." />
	<meta name="keywords" content="حجوزات السعودية, بحث خدمات, حلاقة الرياض, صالونات جدة, حجز فوري, تقييمات موثوقة" />
	<meta property="og:title" content="Wagtee - أفضل منصة حجوزات في السعودية" />
	<meta property="og:description" content="اكتشف وأحجز أفضل الخدمات مع البحث الذكي والتصفية المتقدمة" />
</svelte:head>

<div class="min-h-screen bg-background">
	<main class="">
		<!-- Premium Hero Section with Advanced Search -->
		<section class="pt-16 relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900">
			<!-- Premium Animated Background -->
			<div class="absolute inset-0">
				<!-- Floating Geometric Shapes -->
				<div class="absolute top-20 right-20 w-96 h-96 bg-gradient-to-br from-blue-400/10 to-purple-600/10 rounded-full blur-3xl animate-float"></div>
				<div class="absolute bottom-20 left-20 w-80 h-80 bg-gradient-to-br from-purple-400/10 to-pink-600/10 rounded-full blur-3xl animate-float animation-delay-2000"></div>
				<div class="absolute top-1/2 left-1/4 w-64 h-64 bg-gradient-to-br from-cyan-400/8 to-blue-600/8 rounded-full blur-2xl animate-pulse"></div>
				
				<!-- Premium Grid Pattern -->
				<div class="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>
				
				<!-- Gradient Overlay -->
				<div class="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-background/40"></div>
			</div>

			<div class="container mx-auto px-4 relative z-10">
				<div class="max-w-7xl mx-auto">
					<!-- Main Hero Content -->
					<div class="text-center mb-16 animate-fade-in-up">
						<!-- Premium Badge -->
						<Badge variant="glow" size="lg" class="mb-8 px-6 py-3 text-base font-bold">
							{#snippet leftIcon()}
								<Crown class="w-5 h-5 text-yellow-400" />
							{/snippet}
							<span class="gradient-text-brand">
								المنصة الأولى للحجوزات في السعودية
							</span>
						</Badge>

						<!-- Main Headline with Advanced Typography -->
						<div class="space-y-6 mb-12">
							<h1 class="text-6xl md:text-4xl lg:text-6xl font-black leading-none tracking-tight">
				<span class="block text-slate-900 dark:text-white mb-4 hover:scale-105 transition-transform duration-500">
					اكتشف أفضل
				</span>
				<span class="block gradient-text-brand text-7xl md:text-9xl lg:text-10xl animate-gradient hover:scale-110 transition-transform duration-500">
					الخدمات
				</span>
				<span class="block text-slate-900 dark:text-white mt-4 hover:scale-105 transition-transform duration-500">
					بذكاء
				</span>
			</h1>
						</div>

						<!-- Enhanced Description -->
						<p class="text-2xl md:text-3xl text-slate-600 dark:text-slate-300 max-w-4xl mx-auto leading-relaxed mb-16 font-medium">
							ابحث واحجز من أكثر من <span class="font-bold text-primary">2500 مقدم خدمة موثوق</span> في السعودية
							<br class="hidden md:block">
							مع أدوات البحث الذكية والتصفية المتقدمة
						</p>
					</div>

					<!-- Advanced Search Interface -->
					<div class="max-w-5xl mx-auto mb-20 animate-fade-in-up animation-delay-400">
						<!-- Main Search Card -->
						<Card variant="glass" class="p-8 shadow-premium border-0 backdrop-blur-xl bg-white/80 dark:bg-slate-900/80">
							<CardContent class="space-y-8">
								<!-- Primary Search Bar -->
								<div class="relative">
									<div class="absolute inset-y-0 right-4 flex items-center">
										<Search class="w-6 h-6 text-slate-400" />
									</div>
									<Input 
										bind:value={searchQuery}
										placeholder="ابحث عن خدمة، مدينة، أو مقدم خدمة..."
										class="h-16 text-xl pr-14 pl-6 border-2 border-slate-200/50 focus:border-primary/50 bg-white/50 dark:bg-slate-800/50 rounded-2xl"
									/>
								</div>

								<!-- Quick Filters Row -->
								<div class="flex flex-wrap items-center justify-between gap-4">
									<!-- Category Filter -->
									<div class="flex items-center gap-3">
										<label class="text-sm font-semibold text-slate-600 dark:text-slate-300">التصنيف:</label>
										<select 
											bind:value={selectedCategory}
											class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium focus:ring-2 focus:ring-primary/50"
										>
											<option value="all">جميع الخدمات</option>
											{#each serviceCategories as category}
												<option value={category.id}>{category.name}</option>
											{/each}
										</select>
									</div>

									<!-- City Filter -->
									<div class="flex items-center gap-3">
										<label class="text-sm font-semibold text-slate-600 dark:text-slate-300">المدينة:</label>
										<select 
											bind:value={selectedCity}
											class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium focus:ring-2 focus:ring-primary/50"
										>
											<option value="all">جميع المدن</option>
											{#each saudiCities as city}
												<option value={city.id}>{city.name} ({city.count})</option>
											{/each}
										</select>
									</div>

									<!-- Rating Filter -->
									<div class="flex items-center gap-3">
										<label class="text-sm font-semibold text-slate-600 dark:text-slate-300">التقييم:</label>
										<select 
											bind:value={selectedRating}
											class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium focus:ring-2 focus:ring-primary/50"
										>
											<option value="all">جميع التقييمات</option>
											<option value="4.5">4.5+ نجوم</option>
											<option value="4.0">4.0+ نجوم</option>
											<option value="3.5">3.5+ نجوم</option>
										</select>
									</div>

									<!-- Advanced Filters Toggle -->
									<Button 
										variant="outline" 
										size="sm"
										onclick={() => showFilters = !showFilters}
										class="flex items-center gap-2"
									>
										<SlidersHorizontal class="w-4 h-4" />
										فلاتر متقدمة
									</Button>
								</div>

								<!-- Advanced Filters Panel -->
								{#if showFilters}
									<div class="p-6 bg-slate-50/50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/50 dark:border-slate-700/50 animate-fade-in-up">
										<div class="flex items-center justify-between mb-6">
											<h4 class="text-lg font-bold text-slate-800 dark:text-slate-200">تصفية متقدمة</h4>
											<Button variant="ghost" size="sm" onclick={() => showFilters = false}>
												<X class="w-4 h-4" />
											</Button>
										</div>

										<!-- Popular Tags -->
										<div class="space-y-4">
											<h5 class="text-sm font-semibold text-slate-600 dark:text-slate-400">الفلاتر الشائعة:</h5>
											<div class="flex flex-wrap gap-3">
												{#each popularTags as tag}
													<Button
														variant={selectedTags.includes(tag) ? "premium" : "outline"}
														size="sm"
														onclick={() => toggleTag(tag)}
														class="transition-all duration-300"
													>
														{tag}
													</Button>
												{/each}
											</div>
										</div>

										<!-- Clear Filters -->
										{#if searchQuery || selectedCity !== 'all' || selectedCategory !== 'all' || selectedRating !== 'all' || selectedTags.length > 0}
											<div class="pt-4 border-t border-slate-200 dark:border-slate-700">
												<Button variant="ghost" size="sm" onclick={clearAllFilters}>
													<X class="w-4 h-4 ml-2" />
													مسح جميع الفلاتر
												</Button>
											</div>
										{/if}
									</div>
								{/if}

								<!-- Search Actions -->
								<div class="flex flex-col sm:flex-row gap-4 justify-center">
									<Button variant="premium" size="xl" class="px-10 py-4 h-14 text-lg font-bold shadow-premium">
										{#snippet rightIcon()}
											<Search class="w-6 h-6" />
										{/snippet}
										ابحث الآن ({filteredBusinesses.length} نتيجة)
									</Button>
									<Button variant="glass" size="xl" class="px-10 py-4 h-14 text-lg font-semibold">
										{#snippet leftIcon()}
											<MapPin class="w-6 h-6" />
										{/snippet}
										اعرض على الخريطة
									</Button>
								</div>
							</CardContent>
						</Card>
					</div>

					<!-- Service Categories Grid -->
					<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-20 animate-fade-in-up animation-delay-600">
						{#each serviceCategories as category, i}
							{@const IconComponent = category.icon}
							<Card 
								variant="interactive" 
								class="text-center p-6 hover-lift group cursor-pointer animate-fade-in-up border-0 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm" 
								style="animation-delay: {600 + i * 100}ms"
								onclick={() => selectedCategory = category.id}
							>
								<div class="relative mb-4">
									<div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br {category.gradient} flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg">
										<IconComponent class="w-8 h-8 text-white group-hover:scale-125 transition-transform duration-300" />
									</div>
									{#if category.trending}
										<Badge variant="glow" size="xs" class="absolute -top-2 -right-2">
											<TrendingUp class="w-3 h-3" />
										</Badge>
									{/if}
								</div>
								<h4 class="text-sm font-bold group-hover:text-primary transition-colors duration-300 mb-2">
									{category.name}
								</h4>
								<p class="text-xs text-slate-500 dark:text-slate-400">{category.count} متاح</p>
							</Card>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<!-- Premium Stats Section -->
		<section class="py-20 bg-gradient-to-r from-slate-900 via-blue-900 to-purple-900 text-white relative overflow-hidden">
			<div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px]"></div>
			
			<div class="container mx-auto px-4 relative z-10">
				<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
					{#each stats as stat, i}
						{@const IconComponent = stat.icon}
						<div class="text-center group animate-fade-in-up" style="animation-delay: {i * 150}ms">
							<div class="relative mb-6">
								<div class="w-16 h-16 mx-auto rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-all duration-500">
									<IconComponent class="w-8 h-8 text-white group-hover:scale-125 transition-transform duration-300" />
								</div>
								<div class="text-4xl md:text-5xl font-black text-white mb-2 group-hover:scale-110 transition-all duration-500">
									{stat.number}
								</div>
								<div class="text-lg font-semibold text-white/80 group-hover:text-white transition-colors duration-300">
									{stat.label}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Featured Businesses Showcase -->
		<section class="py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900">
			<div class="container mx-auto px-4">
				<div class="text-center mb-16">
					<Badge variant="gradient" size="lg" class="mb-8">
						<span class="text-white font-semibold">مقدمو الخدمات المميزون</span>
					</Badge>
					<h3 class="text-4xl md:text-6xl font-black mb-8">
						<span class="gradient-text-brand">اكتشف الأفضل</span>
					</h3>
					<p class="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
						مجموعة مختارة من أفضل مقدمي الخدمات المعتمدين والموثوقين في السعودية
					</p>
				</div>

				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
					{#each filteredBusinesses as business, i}
						{@const categoryData = serviceCategories.find(c => c.id === business.category)}
						<Card variant="premium" class="overflow-hidden hover-lift group animate-fade-in-up" style="animation-delay: {i * 200}ms">
							<!-- Business Image/Preview -->
							<div class="h-64 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 dark:from-blue-900/50 dark:via-purple-900/50 dark:to-pink-900/50 relative overflow-hidden">
								<div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
								<div class="absolute top-4 right-4 flex gap-2">
									{#each business.badges as badge}
										{#if badge === 'verified'}
											<Badge variant="glow" size="sm">
												<Verified class="w-3 h-3 ml-1" />
												موثق
											</Badge>
										{:else if badge === 'trending'}
											<Badge variant="pulse" size="sm">
												<TrendingUp class="w-3 h-3 ml-1" />
												رائج
											</Badge>
										{:else if badge === 'top_rated'}
											<Badge variant="gradient" size="sm">
												<Crown class="w-3 h-3 ml-1" />
												الأعلى تقييماً
											</Badge>
										{/if}
									{/each}
								</div>
								<div class="absolute bottom-4 right-4">
									<Badge variant="glass" class="text-white font-bold">
										متاح {business.next_available}
									</Badge>
								</div>
								<!-- Category Icon -->
								{#if categoryData}
									{@const IconComponent = categoryData.icon}
									<div class="absolute inset-0 flex items-center justify-center">
										<div class="w-20 h-20 rounded-3xl bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center group-hover:scale-110 transition-all duration-500">
											<IconComponent class="w-10 h-10 text-white" />
										</div>
									</div>
								{/if}
							</div>

							<CardContent class="p-6 space-y-6">
								<!-- Business Header -->
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<h4 class="text-xl font-bold group-hover:text-primary transition-colors duration-300 mb-2">
											{business.name}
										</h4>
										<p class="text-slate-600 dark:text-slate-400 text-sm mb-3">
											{business.description}
										</p>
									</div>
								</div>

								<!-- Rating and Reviews -->
								<div class="flex items-center justify-between">
									<div class="flex items-center gap-3">
										<div class="flex items-center gap-1 px-3 py-1 rounded-full bg-yellow-100 dark:bg-yellow-900/30">
											<Star class="w-4 h-4 fill-yellow-500 text-yellow-500" />
											<span class="text-sm font-bold text-yellow-700 dark:text-yellow-300">{business.rating}</span>
										</div>
										<span class="text-sm text-slate-500">({business.reviews} تقييم)</span>
									</div>
									<div class="text-sm font-semibold text-primary">
										{business.price_range} ريال
									</div>
								</div>

								<!-- Services -->
								<div class="space-y-2">
									<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">الخدمات المتاحة:</p>
									<div class="flex flex-wrap gap-2">
										{#each business.services.slice(0, 3) as service}
											<Badge variant="outline" size="sm">{service}</Badge>
										{/each}
										{#if business.services.length > 3}
											<Badge variant="ghost" size="sm">+{business.services.length - 3} أخرى</Badge>
										{/if}
									</div>
								</div>

								<!-- Features -->
								<div class="space-y-2">
									<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">المميزات:</p>
									<div class="flex flex-wrap gap-2">
										{#each business.features.slice(0, 2) as feature}
											<Badge variant="minimal" size="sm">
												<CheckCircle class="w-3 h-3 ml-1" />
												{feature}
											</Badge>
										{/each}
									</div>
								</div>

								<!-- Action Buttons -->
								<div class="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
									<Button variant="premium" size="sm" class="flex-1">
										<Calendar class="w-4 h-4 ml-2" />
										احجز الآن
									</Button>
									<Button variant="outline" size="sm">
										<Eye class="w-4 h-4" />
									</Button>
									<Button variant="outline" size="sm">
										<Heart class="w-4 h-4" />
									</Button>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>

				<!-- Load More Button -->
				{#if filteredBusinesses.length > 0}
					<div class="text-center mt-12">
						<Button variant="outline" size="lg" class="px-10">
							عرض المزيد من النتائج
							<ChevronDown class="w-5 h-5 mr-2" />
						</Button>
					</div>
				{:else}
					<div class="text-center py-12">
						<div class="w-16 h-16 mx-auto rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
							<Search class="w-8 h-8 text-slate-400" />
						</div>
						<h4 class="text-xl font-bold text-slate-600 dark:text-slate-400 mb-2">لا توجد نتائج</h4>
						<p class="text-slate-500 dark:text-slate-500 mb-6">جرب تعديل معايير البحث أو الفلاتر</p>
						<Button variant="outline" onclick={clearAllFilters}>
							مسح جميع الفلاتر
						</Button>
					</div>
				{/if}
			</div>
		</section>

		<!-- Premium Features Section -->
		<section class="py-24 bg-white dark:bg-slate-900">
			<div class="container mx-auto px-4">
				<div class="text-center mb-20">
					<Badge variant="glow" size="lg" class="mb-8">
						<span class="text-white font-semibold">الميزات المتقدمة</span>
					</Badge>
					<h3 class="text-4xl md:text-6xl font-black mb-8">
						<span class="gradient-text-brand">تقنيات حديثة</span>
					</h3>
					<p class="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
						أدوات متطورة وميزات ذكية لتجربة حجز استثنائية
					</p>
				</div>

				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
					{#each premiumFeatures as feature, i}
						{@const IconComponent = feature.icon}
						<Card variant="glass" class="hover-lift group animate-fade-in-up p-8 border-0" style="animation-delay: {i * 200}ms">
							<CardContent class="space-y-6">
								<div class="relative">
									<div class="w-16 h-16 {feature.bgColor} rounded-3xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-lg">
										<IconComponent class="w-8 h-8 {feature.color} group-hover:scale-125 transition-transform duration-300" />
									</div>
									{#if feature.demo}
										<Badge variant="pulse" size="xs" class="absolute -top-2 -right-2">
											<Play class="w-3 h-3" />
										</Badge>
									{/if}
								</div>
								<div class="space-y-4">
									<h4 class="text-xl font-bold group-hover:text-primary transition-colors duration-300">
										{feature.title}
									</h4>
									<p class="text-slate-600 dark:text-slate-400 leading-relaxed group-hover:text-slate-800 dark:group-hover:text-slate-300 transition-colors duration-300">
										{feature.description}
									</p>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Enhanced CTA Section -->
		<section class="py-32 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 text-white relative overflow-hidden">
			<div class="absolute inset-0">
				<div class="absolute top-20 left-20 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-float"></div>
				<div class="absolute bottom-20 right-20 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-float animation-delay-2000"></div>
			</div>
			
			<div class="container mx-auto px-4 text-center relative z-10">
				<div class="animate-fade-in-up">
					<div class="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
						<Zap class="w-12 h-12 text-yellow-300" />
					</div>
					<h3 class="text-5xl md:text-7xl font-black mb-8 animate-fade-in-up animation-delay-200">
						ابدأ رحلتك اليوم
					</h3>
					<p class="text-2xl opacity-90 mb-12 max-w-4xl mx-auto leading-relaxed animate-fade-in-up animation-delay-400">
						انضم لآلاف المستخدمين واكتشف عالماً من الخدمات المميزة
					</p>
					<div class="flex flex-col sm:flex-row gap-6 justify-center animate-fade-in-up animation-delay-600">
						<Button variant="floating" size="xl" class="px-12 py-6 h-16 text-xl font-bold bg-white text-primary hover:bg-white/90 shadow-premium" href="/auth/register">
							{#snippet rightIcon()}
								<ArrowRight class="w-6 h-6 rtl-flip" />
							{/snippet}
							سجل كمقدم خدمة
						</Button>
						<Button variant="glass" size="xl" class="px-12 py-6 h-16 text-xl font-bold border-white/30 text-white hover:bg-white/10" href="/book/public">
							{#snippet leftIcon()}
								<QrCode class="w-6 h-6" />
							{/snippet}
							احجز كعميل
						</Button>
					</div>
				</div>
			</div>
		</section>
	</main>

	<!-- Enhanced Footer -->
	<footer class="bg-slate-900 text-slate-300 py-16">
		<div class="container mx-auto px-4">
			<div class="grid md:grid-cols-4 gap-8 mb-12">
				<div class="space-y-4">
					<div class="flex items-center gap-3 mb-6">
						<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
							<Crown class="w-6 h-6 text-white" />
						</div>
						<h4 class="font-bold text-white text-xl">Wagtee</h4>
					</div>
					<p class="text-sm leading-relaxed">
						منصة الحجوزات الرائدة في السوق السعودي مع أحدث التقنيات
					</p>
				</div>
				<div>
					<h5 class="font-bold text-white mb-4">المنتج</h5>
					<ul class="space-y-3 text-sm">
						<li><a href="/features" class="hover:text-white transition-colors">الميزات</a></li>
						<li><a href="/subscription" class="hover:text-white transition-colors">الأسعار</a></li>
						<li><a href="/demo" class="hover:text-white transition-colors">عرض توضيحي</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-bold text-white mb-4">الدعم</h5>
					<ul class="space-y-3 text-sm">
						<li><a href="/help" class="hover:text-white transition-colors">مركز المساعدة</a></li>
						<li><a href="/contact" class="hover:text-white transition-colors">تواصل معنا</a></li>
						<li><a href="/api" class="hover:text-white transition-colors">وثائق API</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-bold text-white mb-4">الشركة</h5>
					<ul class="space-y-3 text-sm">
						<li><a href="/about" class="hover:text-white transition-colors">من نحن</a></li>
						<li><a href="/privacy" class="hover:text-white transition-colors">سياسة الخصوصية</a></li>
						<li><a href="/terms" class="hover:text-white transition-colors">شروط الاستخدام</a></li>
					</ul>
				</div>
			</div>
			<div class="border-t border-slate-800 pt-8 text-center text-sm">
				<p>&copy; 2025 Wagtee. جميع الحقوق محفوظة.</p>
			</div>
		</div>
	</footer>
</div>

<style>
	/* Premium animations */
	@keyframes fade-in-up {
		0% {
			opacity: 0;
			transform: translateY(30px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	@keyframes float {
		0%, 100% { transform: translateY(0px); }
		50% { transform: translateY(-20px); }
	}
	
	@keyframes gradient {
		0% { background-position: 0% 50%; }
		50% { background-position: 100% 50%; }
		100% { background-position: 0% 50%; }
	}
	
	.animate-fade-in-up {
		animation: fade-in-up 0.8s ease-out forwards;
		opacity: 0;
	}
	
	.animate-float {
		animation: float 3s ease-in-out infinite;
	}
	
	.animate-gradient {
		background-size: 200% 200%;
		animation: gradient 3s ease infinite;
	}
	
	.animation-delay-200 { animation-delay: 200ms; }
	.animation-delay-400 { animation-delay: 400ms; }
	.animation-delay-600 { animation-delay: 600ms; }
	.animation-delay-800 { animation-delay: 800ms; }
	.animation-delay-2000 { animation-delay: 2s; }
	
	.hover-lift {
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	.hover-lift:hover {
		transform: translateY(-8px);
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
	}
	
	.gradient-text-brand {
		background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		background-size: 200% 200%;
	}
</style>