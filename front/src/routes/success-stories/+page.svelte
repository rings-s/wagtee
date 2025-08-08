<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	
	import { 
		Star,
		Quote,
		TrendingUp,
		Users,
		Clock,
		Calendar,
		Award,
		Target,
		Zap,
		ArrowRight,
		Scissors,
		Car,
		Dumbbell,
		Camera,
		Sparkles,
		CheckCircle,
		BarChart3,
		MessageCircle,
		Crown,
		Globe
	} from '@lucide/svelte';

	// Success stories with detailed metrics
	const successStories = [
		{
			id: 1,
			businessName: 'صالون النخبة للرجال',
			ownerName: 'أحمد الرشيد',
			businessType: 'حلاقة رجالية',
			icon: Scissors,
			location: 'الرياض',
			image: '/images/testimonials/elite-salon.jpg',
			rating: 4.9,
			testimonial: 'Wagtee غيّر طريقة إدارة صالوني تماماً. الآن أستطيع التركيز على تقديم أفضل خدمة لعملائي بدلاً من القلق بشأن المواعيد والحجوزات. إشعارات واتساب وحدها وفرت علي ساعات من العمل الإداري يومياً.',
			metrics: {
				revenueIncrease: '45%',
				clientIncrease: '60%',
				timesSaved: '3 ساعات يومياً',
				bookingsPerMonth: '450+ حجز'
			},
			challenges: [
				'تعارض المواعيد المستمر',
				'عدم حضور العملاء للمواعيد',
				'إدارة قوائم الانتظار يدوياً',
				'صعوبة تتبع الإيرادات'
			],
			solutions: [
				'نظام حجوزات ذكي يمنع التعارض',
				'تذكيرات واتساب تلقائية',
				'نظام انتظار إلكتروني',
				'تقارير مالية تفصيلية'
			],
			results: [
				'زيادة 45% في الإيرادات الشهرية',
				'تحسن 80% في معدل حضور العملاء',
				'توفير 3 ساعات عمل إداري يومياً',
				'نمو قاعدة العملاء بنسبة 60%'
			],
			color: 'text-blue-600',
			bgColor: 'bg-blue-50 dark:bg-blue-950/20'
		},
		{
			id: 2,
			businessName: 'مركز غسيل السيارات المتقدم',
			ownerName: 'محمد العتيبي',
			businessType: 'غسيل سيارات',
			icon: Car,
			location: 'جدة',
			image: '/images/testimonials/car-wash.jpg',
			rating: 4.8,
			testimonial: 'كنت أعاني من صعوبة في تنظيم المواعيد خاصة في أوقات الذروة. بعد استخدام Wagtee، أصبح بإمكان العملاء حجز مواعيدهم بسهولة عبر رمز QR، والآن أحقق إيرادات أكثر مع عمل أقل.',
			metrics: {
				revenueIncrease: '35%',
				clientIncrease: '40%',
				timesSaved: '2.5 ساعة يومياً',
				bookingsPerMonth: '320+ حجز'
			},
			challenges: [
				'إدارة صفوف الانتظار الطويلة',
				'عدم القدرة على التنبؤ بالإقبال',
				'فقدان عملاء بسبب الانتظار',
				'صعوبة التواصل مع العملاء'
			],
			solutions: [
				'حجز مواعيد مسبقة عبر QR',
				'تحليلات الإقبال والذروة',
				'نظام تنبيهات للعملاء',
				'إشعارات واتساب المتقدمة'
			],
			results: [
				'تقليل 70% في أوقات الانتظار',
				'زيادة 35% في الإيرادات',
				'تحسن 90% في رضا العملاء',
				'نمو 40% في عدد العملاء الجدد'
			],
			color: 'text-green-600',
			bgColor: 'bg-green-50 dark:bg-green-950/20'
		},
		{
			id: 3,
			businessName: 'استوديو اللؤلؤة للتصوير',
			ownerName: 'سارة المنصور',
			businessType: 'تصوير فوتوغرافي',
			icon: Camera,
			location: 'الدمام',
			image: '/images/testimonials/photography-studio.jpg',
			rating: 5.0,
			testimonial: 'كوني مصورة محترفة، أحتاج للتركيز على الإبداع وليس الإدارة. Wagtee منحني الحرية الكاملة لإدارة جلسات التصوير بكفاءة، وساعدني في بناء علاقات أقوى مع عملائي من خلال التواصل المنتظم.',
			metrics: {
				revenueIncrease: '55%',
				clientIncrease: '80%',
				timesSaved: '4 ساعات يومياً',
				bookingsPerMonth: '180+ جلسة'
			},
			challenges: [
				'تنسيق جلسات التصوير المعقدة',
				'إدارة العقود والمدفوعات',
				'متابعة العملاء بعد الجلسات',
				'تنظيم معرض الأعمال'
			],
			solutions: [
				'حجوزات مفصلة بتفاصيل الجلسة',
				'نظام إدارة المدفوعات',
				'متابعة تلقائية للعملاء',
				'ربط مع معرض الأعمال'
			],
			results: [
				'زيادة 55% في الإيرادات السنوية',
				'نمو 80% في قاعدة العملاء',
				'تحسن 95% في تقييمات العملاء',
				'توفير 4 ساعات إدارية يومياً'
			],
			color: 'text-purple-600',
			bgColor: 'bg-purple-50 dark:bg-purple-950/20'
		},
		{
			id: 4,
			businessName: 'نادي اللياقة الذهبي',
			ownerName: 'خالد البقمي',
			businessType: 'نادي رياضي',
			icon: Dumbbell,
			location: 'الرياض',
			image: '/images/testimonials/fitness-club.jpg',
			rating: 4.9,
			testimonial: 'إدارة النادي الرياضي تتطلب تنظيم مئات الحصص والأعضاء يومياً. Wagtee جعل هذا الأمر بسيطاً جداً. الآن أعضاؤنا يحجزون حصصهم بسهولة، ونحن نقدم خدمة أفضل مع تحكم كامل في السعة.',
			metrics: {
				revenueIncrease: '30%',
				clientIncrease: '50%',
				timesSaved: '5 ساعات يومياً',
				bookingsPerMonth: '800+ حصة'
			},
			challenges: [
				'إدارة حصص متعددة وسعات محدودة',
				'تنظيم اشتراكات الأعضاء',
				'تتبع حضور الأعضاء',
				'إدارة المدربين والجدولة'
			],
			solutions: [
				'حجز الحصص بسعات محددة',
				'إدارة شاملة للاشتراكات',
				'تتبع تلقائي للحضور',
				'جدولة متقدمة للمدربين'
			],
			results: [
				'تحسن 85% في استغلال السعة',
				'زيادة 30% في إيرادات الاشتراكات',
				'نمو 50% في الأعضاء النشطين',
				'تقليل 90% في التعارضات'
			],
			color: 'text-red-600',
			bgColor: 'bg-red-50 dark:bg-red-950/20'
		},
		{
			id: 5,
			businessName: 'صالون ملكة الجمال',
			ownerName: 'نورا الزهراني',
			businessType: 'صالون نسائي',
			icon: Sparkles,
			location: 'مكة المكرمة',
			image: '/images/testimonials/beauty-salon.jpg',
			rating: 4.9,
			testimonial: 'صالوني يقدم خدمات متنوعة للعرائس والمناسبات الخاصة. كانت إدارة المواعيد معقدة جداً، خاصة في مواسم الأعراس. Wagtee نظم كل شيء بشكل مثالي وساعدني في تقديم خدمة استثنائية.',
			metrics: {
				revenueIncrease: '50%',
				clientIncrease: '70%',
				timesSaved: '3.5 ساعة يومياً',
				bookingsPerMonth: '280+ موعد'
			},
			challenges: [
				'تنسيق مواعيد العرائس المعقدة',
				'إدارة فريق العمل المتعدد',
				'حجوزات طويلة ومتداخلة',
				'التواصل مع العرائس'
			],
			solutions: [
				'حجوزات مرنة متعددة الساعات',
				'إدارة جدولة فريق العمل',
				'نظام حجز خدمات متعددة',
				'تواصل مخصص للعرائس'
			],
			results: [
				'زيادة 50% في حجوزات العرائس',
				'تحسن 95% في تنظيم الفريق',
				'نمو 70% في العملاء المنتظمين',
				'تقليل 80% في الأخطاء الإدارية'
			],
			color: 'text-pink-600',
			bgColor: 'bg-pink-50 dark:bg-pink-950/20'
		}
	];

	// Overall platform statistics
	const platformStats = [
		{
			number: '1,200+',
			label: 'عمل ناجح',
			description: 'يستخدم منصتنا بثقة',
			icon: Users
		},
		{
			number: '45%',
			label: 'متوسط زيادة الإيرادات',
			description: 'خلال 6 أشهر من الاستخدام',
			icon: TrendingUp
		},
		{
			number: '60%',
			label: 'نمو في العملاء الجدد',
			description: 'بفضل الأدوات التسويقية',
			icon: Target
		},
		{
			number: '80%',
			label: 'تحسن في معدل الحضور',
			description: 'مع التذكيرات التلقائية',
			icon: CheckCircle
		}
	];

	// Industry breakdown
	const industryBreakdown = [
		{ type: 'حلاقة رجالية', count: '480+', growth: '+25%', icon: Scissors, color: 'text-blue-600' },
		{ type: 'صالونات نسائية', count: '320+', growth: '+30%', icon: Sparkles, color: 'text-pink-600' },
		{ type: 'غسيل سيارات', count: '180+', growth: '+40%', icon: Car, color: 'text-green-600' },
		{ type: 'نوادي رياضية', count: '140+', growth: '+35%', icon: Dumbbell, color: 'text-red-600' },
		{ type: 'استوديوهات تصوير', count: '80+', growth: '+50%', icon: Camera, color: 'text-purple-600' }
	];

	// Quick testimonials
	const quickTestimonials = [
		{
			text: 'أفضل استثمار قمت به لعملي. النتائج ظهرت من الأسبوع الأول.',
			author: 'عبدالله السعيد',
			business: 'صالون الملكي'
		},
		{
			text: 'عملائي أصبحوا أكثر رضا والعمل أصبح أكثر تنظيماً وربحية.',
			author: 'فاطمة أحمد',
			business: 'مركز العناية'
		},
		{
			text: 'لا أستطيع تخيل إدارة عملي بدون Wagtee. حقاً غير حياتي المهنية.',
			author: 'محمد الغامدي',
			business: 'مغسلة الأحلام'
		}
	];
</script>

<svelte:head>
	<title>قصص النجاح - Wagtee | شهادات عملاء حقيقيين</title>
	<meta name="description" content="اكتشف قصص النجاح الحقيقية للأعمال السعودية التي تستخدم Wagtee. زيادة في الإيرادات، نمو في العملاء، وتوفير في الوقت." />
	<meta name="keywords" content="قصص نجاح Wagtee, شهادات عملاء, أعمال سعودية ناجحة, زيادة إيرادات, نمو أعمال" />
</svelte:head>

<div class="min-h-screen bg-background">

	<main>
		<!-- Hero Section -->
		<section class="relative py-20 overflow-hidden">
			<div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-purple-50/50 dark:from-blue-950/20 dark:via-background dark:to-purple-950/20"></div>
			
			<div class="container mx-auto px-4 relative z-10">
				<div class="max-w-4xl mx-auto text-center">
					<Badge variant="secondary" class="mb-6">
						<Award class="w-4 h-4 mr-2" />
						قصص نجاح حقيقية
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						أعمال <span class="gradient-text">تنمو وتزدهر</span> مع Wagtee
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
						اكتشف كيف غيّرت منصة Wagtee حياة آلاف أصحاب الأعمال في السوق السعودي وساعدتهم في تحقيق نمو استثنائي
					</p>
					<div class="flex gap-4 justify-center flex-wrap">
						<Button size="lg" variant="default" href="/auth/register" class="btn-premium hover-lift px-8">
							ابدأ قصة نجاحك
							<ArrowRight class="w-4 h-4 mr-2" />
						</Button>
					</div>
				</div>
			</div>
		</section>

		<!-- Platform Statistics -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">نتائج مُثبتة عبر آلاف الأعمال</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						أرقام حقيقية من عملائنا تظهر التأثير الإيجابي لمنصة Wagtee
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{#each platformStats as stat}
						{@const IconComponent = stat.icon}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-8">
								<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<IconComponent class="w-8 h-8 text-white" />
								</div>
								<div class="text-4xl font-bold text-primary mb-2">{stat.number}</div>
								<div class="font-semibold mb-2">{stat.label}</div>
								<div class="text-sm text-muted-foreground">{stat.description}</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Success Stories -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-16">
					<h2 class="text-3xl font-bold mb-4">قصص نجاح ملهمة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						تعرف على تجارب حقيقية لأصحاب أعمال حققوا نمواً استثنائياً مع منصتنا
					</p>
				</div>

				<div class="space-y-20">
					{#each successStories as story, index}
						{@const IconComponent = story.icon}
						<div class="grid lg:grid-cols-2 gap-12 items-center {index % 2 === 1 ? 'lg:grid-flow-col-dense' : ''}">
							<!-- Story Content -->
							<div class="space-y-8 {index % 2 === 1 ? 'lg:col-start-2' : ''}">
								<!-- Business Header -->
								<div class="flex items-center gap-4">
									<div class="w-16 h-16 {story.bgColor} rounded-2xl flex items-center justify-center">
										<IconComponent class="w-8 h-8 {story.color}" />
									</div>
									<div>
										<h3 class="text-2xl font-bold">{story.businessName}</h3>
										<p class="text-muted-foreground">{story.businessType} • {story.location}</p>
									</div>
								</div>

								<!-- Rating and Owner -->
								<div class="flex items-center gap-4">
									<div class="flex items-center gap-1">
										{#each Array(5) as _, i}
											<Star class="w-5 h-5 {i < Math.floor(story.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}" />
										{/each}
									</div>
									<span class="font-medium">{story.rating}</span>
									<span class="text-muted-foreground">•</span>
									<span class="text-muted-foreground">{story.ownerName}</span>
								</div>

								<!-- Testimonial -->
								<Card class="card-premium">
									<CardContent class="p-6">
										<Quote class="w-8 h-8 text-muted-foreground mb-4" />
										<p class="text-lg leading-relaxed italic mb-4">
											"{story.testimonial}"
										</p>
										<div class="text-right">
											<p class="font-semibold">{story.ownerName}</p>
											<p class="text-sm text-muted-foreground">{story.businessName}</p>
										</div>
									</CardContent>
								</Card>

								<!-- Key Metrics -->
								<div class="grid grid-cols-2 gap-4">
									<div class="text-center p-4 rounded-lg {story.bgColor}">
										<div class="text-2xl font-bold {story.color}">{story.metrics.revenueIncrease}</div>
										<div class="text-sm font-medium">زيادة الإيرادات</div>
									</div>
									<div class="text-center p-4 rounded-lg {story.bgColor}">
										<div class="text-2xl font-bold {story.color}">{story.metrics.clientIncrease}</div>
										<div class="text-sm font-medium">نمو العملاء</div>
									</div>
									<div class="text-center p-4 rounded-lg {story.bgColor}">
										<div class="text-2xl font-bold {story.color}">{story.metrics.timesSaved}</div>
										<div class="text-sm font-medium">توفير وقت</div>
									</div>
									<div class="text-center p-4 rounded-lg {story.bgColor}">
										<div class="text-2xl font-bold {story.color}">{story.metrics.bookingsPerMonth}</div>
										<div class="text-sm font-medium">حجوزات شهرية</div>
									</div>
								</div>
							</div>

							<!-- Challenge-Solution-Results -->
							<div class="space-y-6 {index % 2 === 1 ? 'lg:col-start-1 lg:row-start-1' : ''}">
								<!-- Challenges -->
								<Card class="card-premium">
									<CardHeader>
										<CardTitle class="flex items-center gap-3">
											<div class="w-8 h-8 bg-red-50 dark:bg-red-950/20 rounded-lg flex items-center justify-center">
												<Target class="w-4 h-4 text-red-600" />
											</div>
											التحديات قبل Wagtee
										</CardTitle>
									</CardHeader>
									<CardContent>
										<ul class="space-y-2">
											{#each story.challenges as challenge}
												<li class="flex items-start gap-2">
													<div class="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
													<span class="text-sm">{challenge}</span>
												</li>
											{/each}
										</ul>
									</CardContent>
								</Card>

								<!-- Solutions -->
								<Card class="card-premium">
									<CardHeader>
										<CardTitle class="flex items-center gap-3">
											<div class="w-8 h-8 bg-blue-50 dark:bg-blue-950/20 rounded-lg flex items-center justify-center">
												<Zap class="w-4 h-4 text-blue-600" />
											</div>
											الحلول المُطبقة
										</CardTitle>
									</CardHeader>
									<CardContent>
										<ul class="space-y-2">
											{#each story.solutions as solution}
												<li class="flex items-start gap-2">
													<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
													<span class="text-sm">{solution}</span>
												</li>
											{/each}
										</ul>
									</CardContent>
								</Card>

								<!-- Results -->
								<Card class="card-premium border-green-200 dark:border-green-800">
									<CardHeader>
										<CardTitle class="flex items-center gap-3">
											<div class="w-8 h-8 bg-green-50 dark:bg-green-950/20 rounded-lg flex items-center justify-center">
												<TrendingUp class="w-4 h-4 text-green-600" />
											</div>
											النتائج المحققة
										</CardTitle>
									</CardHeader>
									<CardContent>
										<ul class="space-y-2">
											{#each story.results as result}
												<li class="flex items-start gap-2">
													<Award class="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
													<span class="text-sm font-medium">{result}</span>
												</li>
											{/each}
										</ul>
									</CardContent>
								</Card>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Industry Breakdown -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">نمو عبر جميع القطاعات</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						منصة Wagtee تدعم جميع أنواع الأعمال الخدمية وتحقق نتائج متميزة في كل قطاع
					</p>
				</div>
				<div class="grid md:grid-cols-3 lg:grid-cols-5 gap-6">
					{#each industryBreakdown as industry}
						{@const IconComponent = industry.icon}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="w-16 h-16 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<IconComponent class="w-8 h-8 {industry.color}" />
								</div>
								<h3 class="font-semibold mb-2">{industry.type}</h3>
								<div class="text-2xl font-bold text-primary mb-1">{industry.count}</div>
								<Badge variant="secondary" class="text-xs">
									{industry.growth} نمو
								</Badge>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Quick Testimonials -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">ماذا يقول عملاؤنا</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						شهادات سريعة من أصحاب أعمال يستخدمون منصتنا يومياً
					</p>
				</div>
				<div class="grid md:grid-cols-3 gap-8">
					{#each quickTestimonials as testimonial}
						<Card class="card-premium hover-lift">
							<CardContent class="p-6">
								<Quote class="w-6 h-6 text-muted-foreground mb-4" />
								<p class="text-muted-foreground mb-4 leading-relaxed italic">
									"{testimonial.text}"
								</p>
								<div class="flex items-center gap-3">
									<div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
										<span class="text-white font-bold text-sm">{testimonial.author.charAt(0)}</span>
									</div>
									<div>
										<p class="font-semibold">{testimonial.author}</p>
										<p class="text-sm text-muted-foreground">{testimonial.business}</p>
									</div>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Achievement Badges -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">إنجازات وشهادات</h2>
						<p class="text-muted-foreground">
							تقدير من المؤسسات والعملاء لجودة خدماتنا
						</p>
					</div>
					<div class="grid md:grid-cols-4 gap-8">
						<div class="text-center">
							<div class="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Crown class="w-10 h-10 text-white" />
							</div>
							<h3 class="font-bold mb-2">أفضل منصة حجوزات</h3>
							<p class="text-sm text-muted-foreground">جوائز التقنية السعودية 2024</p>
						</div>
						<div class="text-center">
							<div class="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<CheckCircle class="w-10 h-10 text-white" />
							</div>
							<h3 class="font-bold mb-2">شهادة الجودة</h3>
							<p class="text-sm text-muted-foreground">معتمد من CITC</p>
						</div>
						<div class="text-center">
							<div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Globe class="w-10 h-10 text-white" />
							</div>
							<h3 class="font-bold mb-2">الشراكة الذهبية</h3>
							<p class="text-sm text-muted-foreground">برنامج رؤية 2030</p>
						</div>
						<div class="text-center">
							<div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-violet-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<Users class="w-10 h-10 text-white" />
							</div>
							<h3 class="font-bold mb-2">ثقة العملاء</h3>
							<p class="text-sm text-muted-foreground">تقييم 4.9/5 نجوم</p>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">ابدأ قصة نجاحك التالية</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
					انضم لآلاف أصحاب الأعمال الناجحين واكتشف كيف يمكن لـ Wagtee أن يغير مسار عملك
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="/auth/register" class="btn-premium hover-lift">
						ابدأ تجربتك المجانية الآن
					</Button>
					<Button size="lg" variant="outline" class="border-white text-white hover:bg-white hover:text-purple-600" href="/contact">
						تحدث مع خبير النمو
					</Button>
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
						<li><a href="/subscription" class="text-muted-foreground hover:text-foreground transition-colors">الأسعار</a></li>
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