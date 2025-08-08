<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import Navbar from '$lib/components/navbar.svelte';
	
	import { 
		Crown,
		CheckCircle,
		X,
		ArrowRight,
		Calculator,
		TrendingUp,
		Shield,
		Clock,
		Users,
		Calendar,
		MessageCircle,
		QrCode,
		BarChart3,
		Settings,
		CreditCard,
		Zap,
		Award,
		Globe,
		Phone,
		Mail
	} from '@lucide/svelte';

	// Detailed pricing plans
	const pricingPlans = [
		{
			name: 'الأساسية',
			nameEn: 'Basic',
			price: 30,
			yearlyPrice: 300, // 10 months price
			period: 'شهرياً',
			yearlyPeriod: 'سنوياً',
			description: 'مثالية للأعمال الصغيرة الناشئة',
			popular: false,
			color: 'blue',
			limits: {
				services: 3,
				bookings: 50,
				customers: 100,
				staff: 1,
				qrCodes: 1,
				whatsappMessages: 200,
				reports: 'أساسية',
				support: 'بريد إلكتروني'
			},
			features: [
				{ name: 'نظام حجوزات ذكي', included: true },
				{ name: 'إشعارات واتساب', included: true, limit: '200 رسالة/شهر' },
				{ name: 'رمز QR واحد', included: true },
				{ name: 'إدارة العملاء', included: true, limit: 'حتى 100 عميل' },
				{ name: 'تقارير أساسية', included: true },
				{ name: 'دعم بريد إلكتروني', included: true },
				{ name: 'تطبيق موبايل', included: true },
				{ name: 'لوحة تحكم ويب', included: true },
				{ name: 'إدارة متعددة المستخدمين', included: false },
				{ name: 'تقارير متقدمة', included: false },
				{ name: 'API متقدم', included: false },
				{ name: 'دعم هاتفي', included: false }
			],
			bestFor: ['الأعمال الناشئة', 'صالونات صغيرة', 'حلاقين مستقلين'],
			savings: null
		},
		{
			name: 'المتقدمة',
			nameEn: 'Standard',
			price: 45,
			yearlyPrice: 450, // 10 months price
			period: 'شهرياً',
			yearlyPeriod: 'سنوياً',
			description: 'الأمثل للأعمال المتنامية',
			popular: true,
			color: 'purple',
			limits: {
				services: 7,
				bookings: 150,
				customers: 300,
				staff: 3,
				qrCodes: 3,
				whatsappMessages: 600,
				reports: 'متقدمة',
				support: 'دردشة + بريد'
			},
			features: [
				{ name: 'نظام حجوزات ذكي', included: true },
				{ name: 'إشعارات واتساب', included: true, limit: '600 رسالة/شهر' },
				{ name: '3 رموز QR', included: true },
				{ name: 'إدارة العملاء', included: true, limit: 'حتى 300 عميل' },
				{ name: 'تقارير متقدمة', included: true },
				{ name: 'دعم دردشة مباشرة', included: true },
				{ name: 'تطبيق موبايل', included: true },
				{ name: 'لوحة تحكم ويب', included: true },
				{ name: 'إدارة متعددة المستخدمين', included: true, limit: 'حتى 3 مستخدمين' },
				{ name: 'حملات تسويقية', included: true },
				{ name: 'تحليلات العملاء', included: true },
				{ name: 'دعم هاتفي', included: false }
			],
			bestFor: ['الصالونات المتوسطة', 'مراكز غسيل السيارات', 'النوادي الرياضية'],
			savings: 'وفر 90 ريال سنوياً'
		},
		{
			name: 'الاحترافية',
			nameEn: 'Premium',
			price: 60,
			yearlyPrice: 600, // 10 months price
			period: 'شهرياً',
			yearlyPeriod: 'سنوياً',
			description: 'للأعمال الكبيرة والسلاسل التجارية',
			popular: false,
			color: 'gold',
			limits: {
				services: 'غير محدودة',
				bookings: 'غير محدودة',
				customers: 'غير محدودة',
				staff: 'غير محدود',
				qrCodes: 'غير محدودة',
				whatsappMessages: 'غير محدودة',
				reports: 'متقدمة + مخصصة',
				support: 'VIP 24/7'
			},
			features: [
				{ name: 'نظام حجوزات ذكي', included: true },
				{ name: 'إشعارات واتساب غير محدودة', included: true },
				{ name: 'رموز QR غير محدودة', included: true },
				{ name: 'إدارة عملاء غير محدودة', included: true },
				{ name: 'تقارير مخصصة', included: true },
				{ name: 'دعم VIP 24/7', included: true },
				{ name: 'تطبيق موبايل', included: true },
				{ name: 'لوحة تحكم ويب', included: true },
				{ name: 'إدارة متعددة المستخدمين', included: true },
				{ name: 'API متقدم', included: true },
				{ name: 'تكامل مخصص', included: true },
				{ name: 'استشارات مجانية', included: true }
			],
			bestFor: ['السلاسل التجارية', 'الأعمال الكبيرة', 'المراكز المتعددة الفروع'],
			savings: 'وفر 120 ريال سنوياً'
		}
	];

	// Feature comparison
	const comparisonFeatures = [
		{
			category: 'الميزات الأساسية',
			features: [
				{ name: 'نظام حجوزات ذكي', basic: true, standard: true, premium: true },
				{ name: 'منع تعارض المواعيد', basic: true, standard: true, premium: true },
				{ name: 'إدارة ساعات العمل', basic: true, standard: true, premium: true },
				{ name: 'تطبيق موبايل', basic: true, standard: true, premium: true },
				{ name: 'لوحة تحكم ويب', basic: true, standard: true, premium: true }
			]
		},
		{
			category: 'إشعارات واتساب',
			features: [
				{ name: 'تذكيرات تلقائية', basic: '200/شهر', standard: '600/شهر', premium: 'غير محدودة' },
				{ name: 'إشعارات الحجز', basic: true, standard: true, premium: true },
				{ name: 'رسائل ترويجية', basic: false, standard: true, premium: true },
				{ name: 'رسائل مخصصة', basic: false, standard: true, premium: true }
			]
		},
		{
			category: 'إدارة العملاء والخدمات',
			features: [
				{ name: 'عدد الخدمات', basic: '3', standard: '7', premium: 'غير محدودة' },
				{ name: 'عدد العملاء', basic: '100', standard: '300', premium: 'غير محدودة' },
				{ name: 'قاعدة بيانات العملاء', basic: true, standard: true, premium: true },
				{ name: 'تاريخ العملاء', basic: true, standard: true, premium: true }
			]
		},
		{
			category: 'التقارير والتحليلات',
			features: [
				{ name: 'تقارير المبيعات', basic: 'أساسية', standard: 'متقدمة', premium: 'مخصصة' },
				{ name: 'تحليلات العملاء', basic: false, standard: true, premium: true },
				{ name: 'إحصائيات الأداء', basic: 'أساسية', standard: 'متقدمة', premium: 'شاملة' },
				{ name: 'تصدير التقارير', basic: false, standard: true, premium: true }
			]
		},
		{
			category: 'الدعم والمساعدة',
			features: [
				{ name: 'دعم بريد إلكتروني', basic: true, standard: true, premium: true },
				{ name: 'دردشة مباشرة', basic: false, standard: true, premium: true },
				{ name: 'دعم هاتفي', basic: false, standard: false, premium: true },
				{ name: 'استشارات مجانية', basic: false, standard: false, premium: true }
			]
		}
	];

	// ROI Calculator sample data
	const roiSamples = [
		{
			businessType: 'صالون حلاقة',
			currentBookings: 120,
			expectedIncrease: 40,
			averageServicePrice: 25,
			plan: 'المتقدمة',
			planCost: 45,
			monthlyIncrease: 1200,
			yearlyIncrease: 14400,
			roi: 2567
		},
		{
			businessType: 'مركز غسيل سيارات',
			currentBookings: 80,
			expectedIncrease: 35,
			averageServicePrice: 40,
			plan: 'الأساسية',
			planCost: 30,
			monthlyIncrease: 1120,
			yearlyIncrease: 13440,
			roi: 3740
		},
		{
			businessType: 'نادي رياضي',
			currentBookings: 200,
			expectedIncrease: 30,
			averageServicePrice: 15,
			plan: 'الاحترافية',
			planCost: 60,
			monthlyIncrease: 900,
			yearlyIncrease: 10800,
			roi: 1400
		}
	];

	// FAQ specific to pricing
	const pricingFAQ = [
		{
			question: 'هل يمكنني تجربة المنصة مجاناً؟',
			answer: 'نعم، نوفر تجربة مجانية لمدة 14 يوم بجميع الميزات بدون الحاجة لبطاقة ائتمانية.'
		},
		{
			question: 'هل يمكنني تغيير خطتي في أي وقت؟',
			answer: 'نعم، يمكنك ترقية أو تخفيض خطتك في أي وقت. الترقية فورية والتخفيض يطبق في دورة الفوترة التالية.'
		},
		{
			question: 'ماذا يحدث إذا تجاوزت حدود خطتي؟',
			answer: 'سنرسل لك تنبيه قبل الوصول للحد. يمكنك الترقية أو سندير الحجوزات الإضافية برسوم صغيرة.'
		},
		{
			question: 'هل توجد رسوم إضافية أو مخفية؟',
			answer: 'لا، السعر المعلن يشمل جميع الميزات. لا توجد رسوم إعداد أو رسوم إضافية مخفية.'
		},
		{
			question: 'كيف يتم الدفع؟',
			answer: 'نقبل البطاقات الائتمانية، مدى، STC Pay، وجميع طرق الدفع الإلكتروني المتاحة في السعودية.'
		},
		{
			question: 'هل يمكنني إلغاء الاشتراك؟',
			answer: 'نعم، يمكنك إلغاء الاشتراك في أي وقت بدون غرامات. البيانات محفوظة لمدة 30 يوم بعد الإلغاء.'
		}
	];

	let selectedPlan = $state('monthly');
	let showComparison = $state(false);
</script>

<svelte:head>
	<title>الأسعار - Wagtee | خطط مرنة لجميع أحجام الأعمال</title>
	<meta name="description" content="اختر الخطة المناسبة لعملك مع Wagtee. خطط مرنة بأسعار تنافسية وبدون التزامات طويلة المدى. تجربة مجانية 14 يوم." />
	<meta name="keywords" content="أسعار Wagtee, خطط اشتراك, تسعير مرن, تجربة مجانية, أعمال سعودية" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />

	<main>
		<!-- Hero Section -->
		<section class="relative py-20 overflow-hidden">
			<div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-purple-50/50 dark:from-blue-950/20 dark:via-background dark:to-purple-950/20"></div>
			
			<div class="container mx-auto px-4 relative z-10">
				<div class="max-w-4xl mx-auto text-center">
					<Badge variant="secondary" class="mb-6">
						<Calculator class="w-4 h-4 mr-2" />
						خطط مرنة وشفافة
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						اختر الخطة <span class="gradient-text">المناسبة</span> لعملك
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
						خطط تسعير واضحة ومرنة تناسب جميع أحجام الأعمال. ابدأ مجاناً لمدة 14 يوم بدون التزامات
					</p>
					
					<!-- Billing Toggle -->
					<div class="flex items-center justify-center gap-4 mb-8">
						<span class="text-sm font-medium {selectedPlan === 'monthly' ? 'text-foreground' : 'text-muted-foreground'}">شهرياً</span>
						<button
							class="relative w-16 h-8 bg-muted rounded-full transition-colors duration-200 {selectedPlan === 'yearly' ? 'bg-primary' : ''}"
							onclick={() => selectedPlan = selectedPlan === 'monthly' ? 'yearly' : 'monthly'}
						>
							<div class="absolute top-1 w-6 h-6 bg-white rounded-full shadow-sm transition-transform duration-200 {selectedPlan === 'yearly' ? 'translate-x-8' : 'translate-x-1'}"></div>
						</button>
						<span class="text-sm font-medium {selectedPlan === 'yearly' ? 'text-foreground' : 'text-muted-foreground'}">سنوياً</span>
						<Badge variant="secondary" class="text-xs">
							وفر شهرين
						</Badge>
					</div>
				</div>
			</div>
		</section>

		<!-- Pricing Plans -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
					{#each pricingPlans as plan}
						<Card class="relative hover-lift {plan.popular ? 'ring-2 ring-primary/50 scale-105 shadow-2xl' : 'card-premium'}">
							{#if plan.popular}
								<div class="absolute -top-6 left-1/2 transform -translate-x-1/2">
									<Badge variant="default" class="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600">
										<Crown class="w-4 h-4 ml-2" />
										الأكثر شعبية
									</Badge>
								</div>
							{/if}
							<CardHeader class="text-center pb-8">
								<CardTitle class="text-2xl font-bold mb-2">{plan.name}</CardTitle>
								<CardDescription class="mb-6 text-muted-foreground">{plan.description}</CardDescription>
								<div class="relative">
									<div class="text-6xl font-black gradient-text mb-2">
										{selectedPlan === 'monthly' ? plan.price : plan.yearlyPrice}
									</div>
									<div class="text-lg text-muted-foreground">
										<span class="font-medium">ريال</span> / {selectedPlan === 'monthly' ? plan.period : plan.yearlyPeriod}
									</div>
									{#if selectedPlan === 'yearly' && plan.savings}
										<Badge variant="secondary" class="mt-2 text-xs">
											{plan.savings}
										</Badge>
									{/if}
								</div>
							</CardHeader>
							<CardContent class="space-y-8">
								<!-- Plan Limits -->
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div class="text-center p-3 bg-muted/50 rounded-lg">
										<div class="font-bold text-lg">{plan.limits.services}</div>
										<div class="text-muted-foreground">خدمة</div>
									</div>
									<div class="text-center p-3 bg-muted/50 rounded-lg">
										<div class="font-bold text-lg">{plan.limits.bookings}</div>
										<div class="text-muted-foreground">حجز/شهر</div>
									</div>
									<div class="text-center p-3 bg-muted/50 rounded-lg">
										<div class="font-bold text-lg">{plan.limits.customers}</div>
										<div class="text-muted-foreground">عميل</div>
									</div>
									<div class="text-center p-3 bg-muted/50 rounded-lg">
										<div class="font-bold text-lg">{plan.limits.staff}</div>
										<div class="text-muted-foreground">مستخدم</div>
									</div>
								</div>

								<!-- Key Features -->
								<ul class="space-y-3">
									{#each plan.features.slice(0, 8) as feature}
										<li class="flex items-start gap-3 text-sm">
											{#if feature.included}
												<CheckCircle class="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
												<div>
													<span class="text-foreground font-medium">{feature.name}</span>
													{#if feature.limit}
														<span class="text-muted-foreground"> ({feature.limit})</span>
													{/if}
												</div>
											{:else}
												<X class="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
												<span class="text-muted-foreground">{feature.name}</span>
											{/if}
										</li>
									{/each}
								</ul>

								<!-- Best For -->
								<div class="border-t pt-6">
									<h4 class="font-semibold mb-3 text-sm">مناسب لـ:</h4>
									<div class="flex flex-wrap gap-2">
										{#each plan.bestFor as category}
											<Badge variant="outline" class="text-xs">
												{category}
											</Badge>
										{/each}
									</div>
								</div>

								<Button 
									variant={plan.popular ? 'default' : 'outline'} 
									size="lg" 
									class="w-full h-12 text-lg font-bold" 
									href="/auth/register"
								>
									{plan.popular ? 'ابدأ تجربتك المجانية' : 'اختيار الخطة'}
								</Button>
							</CardContent>
						</Card>
					{/each}
				</div>

				<!-- Comparison Toggle -->
				<div class="text-center mt-12">
					<Button 
						variant="outline" 
						onclick={() => showComparison = !showComparison}
					>
						{showComparison ? 'إخفاء' : 'عرض'} جدول المقارنة التفصيلي
						{showComparison ? '↑' : '↓'}
					</Button>
				</div>
			</div>
		</section>

		<!-- Detailed Comparison Table -->
		{#if showComparison}
			<section class="py-16 bg-muted/30">
				<div class="container mx-auto px-4">
					<div class="max-w-6xl mx-auto">
						<div class="text-center mb-12">
							<h2 class="text-3xl font-bold mb-4">مقارنة تفصيلية للميزات</h2>
							<p class="text-muted-foreground">
								جدول شامل لجميع الميزات والحدود لكل خطة
							</p>
						</div>

						<div class="overflow-x-auto">
							<table class="w-full">
								<thead>
									<tr class="border-b">
										<th class="text-right p-4 font-bold">الميزة</th>
										<th class="text-center p-4 font-bold">الأساسية</th>
										<th class="text-center p-4 font-bold">المتقدمة</th>
										<th class="text-center p-4 font-bold">الاحترافية</th>
									</tr>
								</thead>
								<tbody>
									{#each comparisonFeatures as category}
										<tr class="bg-muted/50">
											<td colspan="4" class="p-4 font-bold text-primary">
												{category.category}
											</td>
										</tr>
										{#each category.features as feature}
											<tr class="border-b hover:bg-muted/20">
												<td class="p-4 font-medium">{feature.name}</td>
												<td class="p-4 text-center">
													{#if typeof feature.basic === 'boolean'}
														{#if feature.basic}
															<CheckCircle class="w-5 h-5 text-green-600 mx-auto" />
														{:else}
															<X class="w-5 h-5 text-muted-foreground mx-auto" />
														{/if}
													{:else}
														<span class="text-sm">{feature.basic}</span>
													{/if}
												</td>
												<td class="p-4 text-center">
													{#if typeof feature.standard === 'boolean'}
														{#if feature.standard}
															<CheckCircle class="w-5 h-5 text-green-600 mx-auto" />
														{:else}
															<X class="w-5 h-5 text-muted-foreground mx-auto" />
														{/if}
													{:else}
														<span class="text-sm">{feature.standard}</span>
													{/if}
												</td>
												<td class="p-4 text-center">
													{#if typeof feature.premium === 'boolean'}
														{#if feature.premium}
															<CheckCircle class="w-5 h-5 text-green-600 mx-auto" />
														{:else}
															<X class="w-5 h-5 text-muted-foreground mx-auto" />
														{/if}
													{:else}
														<span class="text-sm">{feature.premium}</span>
													{/if}
												</td>
											</tr>
										{/each}
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</section>
		{/if}

		<!-- ROI Calculator -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="max-w-6xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">احسب العائد على الاستثمار</h2>
						<p class="text-muted-foreground max-w-2xl mx-auto">
							شاهد كيف يمكن لـ Wagtee أن يزيد إيراداتك ويوفر عليك التكاليف
						</p>
					</div>

					<div class="grid md:grid-cols-3 gap-8">
						{#each roiSamples as sample}
							<Card class="card-premium hover-lift">
								<CardContent class="p-6">
									<div class="text-center mb-6">
										<h3 class="text-xl font-bold mb-2">{sample.businessType}</h3>
										<p class="text-sm text-muted-foreground">مثال حقيقي من عملائنا</p>
									</div>
									
									<div class="space-y-4 text-sm">
										<div class="flex justify-between">
											<span>الحجوزات الحالية:</span>
											<span class="font-medium">{sample.currentBookings}/شهر</span>
										</div>
										<div class="flex justify-between">
											<span>زيادة متوقعة:</span>
											<span class="font-medium text-green-600">+{sample.expectedIncrease}%</span>
										</div>
										<div class="flex justify-between">
											<span>متوسط سعر الخدمة:</span>
											<span class="font-medium">{sample.averageServicePrice} ريال</span>
										</div>
										<div class="flex justify-between">
											<span>الخطة المختارة:</span>
											<span class="font-medium">{sample.plan}</span>
										</div>
									</div>

									<div class="border-t mt-6 pt-6">
										<div class="text-center">
											<div class="text-2xl font-bold text-green-600 mb-1">
												+{sample.monthlyIncrease.toLocaleString()} ريال/شهر
											</div>
											<div class="text-sm text-muted-foreground mb-4">
												زيادة شهرية في الإيرادات
											</div>
											<Badge variant="secondary" class="text-xs">
												عائد {sample.roi}% على الاستثمار
											</Badge>
										</div>
									</div>
								</CardContent>
							</Card>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<!-- Value Proposition -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto text-center">
					<h2 class="text-3xl font-bold mb-8">لماذا تستثمر في Wagtee؟</h2>
					<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<TrendingUp class="w-8 h-8 text-white" />
							</div>
							<h3 class="font-bold mb-2">زيادة الإيرادات</h3>
							<p class="text-sm text-muted-foreground">متوسط زيادة 40% في الإيرادات خلال 6 أشهر</p>
						</div>
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Clock class="w-8 h-8 text-white" />
							</div>
							<h3 class="font-bold mb-2">توفير الوقت</h3>
							<p class="text-sm text-muted-foreground">وفر 3-4 ساعات يومياً من العمل الإداري</p>
						</div>
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-violet-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Users class="w-8 h-8 text-white" />
							</div>
							<h3 class="font-bold mb-2">المزيد من العملاء</h3>
							<p class="text-sm text-muted-foreground">نمو 50% في قاعدة العملاء مع أدوات التسويق</p>
						</div>
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Award class="w-8 h-8 text-white" />
							</div>
							<h3 class="font-bold mb-2">رضا العملاء</h3>
							<p class="text-sm text-muted-foreground">تحسن 80% في معدل الحضور ورضا العملاء</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Pricing FAQ -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">أسئلة شائعة حول الأسعار</h2>
						<p class="text-muted-foreground">
							إجابات للأسئلة الأكثر شيوعاً حول خطط التسعير
						</p>
					</div>
					
					<div class="space-y-6">
						{#each pricingFAQ as faq}
							<Card class="card-premium">
								<CardContent class="p-6">
									<h3 class="font-semibold mb-3">{faq.question}</h3>
									<p class="text-muted-foreground leading-relaxed">{faq.answer}</p>
								</CardContent>
							</Card>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<!-- Final CTA -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">جاهز لتطوير عملك؟</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto leading-relaxed">
					ابدأ تجربتك المجانية اليوم واكتشف كيف يمكن لـ Wagtee أن يحول عملك
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="/auth/register" class="btn-premium hover-lift px-12">
						ابدأ تجربتك المجانية الآن
						<ArrowRight class="w-4 h-4 mr-2" />
					</Button>
					<Button size="lg" variant="outline" class="border-white text-white hover:bg-white hover:text-purple-600" href="/contact">
						تحدث مع خبير المبيعات
						<Phone class="w-4 h-4 mr-2" />
					</Button>
				</div>
				
				<div class="flex flex-wrap items-center justify-center gap-8 mt-12 pt-8 border-t border-white/20">
					<div class="flex items-center gap-3 text-white/80">
						<CheckCircle class="w-5 h-5 text-green-300" />
						<span>تجربة مجانية 14 يوم</span>
					</div>
					<div class="flex items-center gap-3 text-white/80">
						<Shield class="w-5 h-5 text-blue-300" />
						<span>بدون التزامات</span>
					</div>
					<div class="flex items-center gap-3 text-white/80">
						<CreditCard class="w-5 h-5 text-purple-300" />
						<span>بدون بطاقة ائتمانية</span>
					</div>
				</div>
			</div>
		</section>
	</main>

	<!-- Footer -->
	<footer class="bg-muted py-12">
		<div class="container mx-auto px-4">
			<div class="grid md:grid-cols-4 gap-8">
				<div>
					<h4 class="font-bold text-foreground mb-4">Wagtee</h4>
					<p class="text-sm text-muted-foreground">
						منصة الحجوزات الرائدة في السوق السعودي
					</p>
				</div>
				<div>
					<h5 class="font-medium text-foreground mb-3">المنتج</h5>
					<ul class="space-y-2 text-sm">
						<li><a href="/features" class="text-muted-foreground hover:text-foreground transition-colors">الميزات</a></li>
						<li><a href="/pricing" class="text-muted-foreground hover:text-foreground transition-colors">الأسعار</a></li>
						<li><a href="/success-stories" class="text-muted-foreground hover:text-foreground transition-colors">قصص النجاح</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-medium text-foreground mb-3">الدعم</h5>
					<ul class="space-y-2 text-sm">
						<li><a href="/help" class="text-muted-foreground hover:text-foreground transition-colors">مركز المساعدة</a></li>
						<li><a href="/about" class="text-muted-foreground hover:text-foreground transition-colors">من نحن</a></li>
						<li><a href="/contact" class="text-muted-foreground hover:text-foreground transition-colors">تواصل معنا</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-medium text-foreground mb-3">تواصل معنا</h5>
					<ul class="space-y-2 text-sm text-muted-foreground">
						<li>الرياض، المملكة العربية السعودية</li>
						<li>support@wagtee.sa</li>
						<li>+966 11 123 4567</li>
					</ul>
				</div>
			</div>
			<div class="border-t border-border mt-8 pt-8 text-center text-sm text-muted-foreground">
				<p>&copy; 2024 Wagtee. جميع الحقوق محفوظة.</p>
			</div>
		</div>
	</footer>
</div>