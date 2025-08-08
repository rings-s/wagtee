<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import Navbar from '$lib/components/navbar.svelte';
	
	import { 
		Calendar,
		MessageCircle,
		QrCode,
		BarChart3,
		Shield,
		Users,
		Clock,
		Star,
		Globe,
		Smartphone,
		Bell,
		CreditCard,
		CheckCircle,
		ArrowRight,
		Zap,
		Target,
		TrendingUp,
		Award,
		Settings,
		FileText,
		Download,
		Languages,
		MapPin,
		Phone,
		RefreshCw,
		Eye,
		Lock,
		Scissors,
		Car,
		Dumbbell,
		Camera,
		Sparkles
	} from '@lucide/svelte';

	// Main features with detailed benefits
	const mainFeatures = [
		{
			icon: Calendar,
			title: 'نظام حجوزات ذكي ومتطور',
			subtitle: 'إدارة احترافية للمواعيد والجدولة',
			description: 'نظام حجوزات متطور يمنع التعارض تلقائياً ويدير المواعيد بكفاءة عالية مع إمكانية الحجز المسبق والتكرار',
			benefits: [
				'منع تعارض المواعيد تلقائياً',
				'حجوزات متكررة للعملاء المنتظمين',
				'إدارة أوقات الراحة والإجازات',
				'حجز متعدد الخدمات في موعد واحد',
				'نظام انتظار ذكي للمواعيد المكتملة'
			],
			color: 'text-blue-600',
			bgColor: 'bg-blue-50 dark:bg-blue-950/20',
			borderColor: 'border-blue-200 dark:border-blue-800'
		},
		{
			icon: MessageCircle,
			title: 'إشعارات واتساب التلقائية',
			subtitle: 'تواصل مباشر مع عملائك عبر WhatsApp',
			description: 'نظام إشعارات متكامل عبر واتساب للتذكير بالمواعيد وإرسال التحديثات والعروض للعملاء باللغة العربية والإنجليزية',
			benefits: [
				'تذكيرات تلقائية قبل الموعد (24 ساعة، 2 ساعة)',
				'إشعارات تأكيد الحجز الفورية',
				'رسائل ترويجية للعروض والخدمات الجديدة',
				'إشعارات تغيير الموعد أو الإلغاء',
				'رسائل المتابعة وطلب التقييم'
			],
			color: 'text-green-600',
			bgColor: 'bg-green-50 dark:bg-green-950/20',
			borderColor: 'border-green-200 dark:border-green-800'
		},
		{
			icon: QrCode,
			title: 'حجز فوري برمز QR',
			subtitle: 'حجوزات سريعة بدون تطبيق أو تسجيل',
			description: 'رموز QR مخصصة لكل عمل تمكن العملاء من الحجز المباشر بمسح بسيط دون الحاجة لتسجيل أو تحميل تطبيق',
			benefits: [
				'حجز فوري بمسح الرمز فقط',
				'لا يحتاج تسجيل أو إنشاء حساب',
				'يعمل على جميع الهواتف الذكية',
				'رموز قابلة للطباعة والمشاركة',
				'إحصائيات مفصلة لاستخدام الرموز'
			],
			color: 'text-purple-600',
			bgColor: 'bg-purple-50 dark:bg-purple-950/20',
			borderColor: 'border-purple-200 dark:border-purple-800'
		},
		{
			icon: BarChart3,
			title: 'تقارير وتحليلات متقدمة',
			subtitle: 'فهم عميق لأداء عملك وسلوك العملاء',
			description: 'تقارير شاملة ورؤى تحليلية عميقة لمساعدتك في اتخاذ قرارات مدروسة لنمو عملك وتحسين الأداء',
			benefits: [
				'تقارير الإيرادات والأرباح الشهرية',
				'تحليل سلوك العملاء وأوقات الذروة',
				'إحصائيات الخدمات الأكثر طلباً',
				'معدلات الحضور والغياب',
				'تقارير قابلة للتصدير (PDF, Excel)'
			],
			color: 'text-orange-600',
			bgColor: 'bg-orange-50 dark:bg-orange-950/20',
			borderColor: 'border-orange-200 dark:border-orange-800'
		}
	];

	// Additional features
	const additionalFeatures = [
		{
			icon: Shield,
			title: 'إدارة الأدوار والصلاحيات',
			description: 'تحكم كامل في صلاحيات المستخدمين وأدوار الفريق'
		},
		{
			icon: Users,
			title: 'إدارة قاعدة بيانات العملاء',
			description: 'تنظيم معلومات العملاء وتاريخ الحجوزات والتفضيلات'
		},
		{
			icon: Globe,
			title: 'دعم متعدد اللغات',
			description: 'واجهة باللغتين العربية والإنجليزية لراحة جميع المستخدمين'
		},
		{
			icon: Smartphone,
			title: 'متوافق مع الجوال',
			description: 'تصميم متجاوب يعمل بسلاسة على جميع الأجهزة والشاشات'
		},
		{
			icon: Clock,
			title: 'إدارة ساعات العمل',
			description: 'تحديد أوقات العمل والإجازات والمناسبات الخاصة'
		},
		{
			icon: CreditCard,
			title: 'نظام دفع متكامل',
			description: 'قبول المدفوعات الإلكترونية وإدارة الفواتير والاشتراكات'
		},
		{
			icon: Bell,
			title: 'تنبيهات في الوقت الفعلي',
			description: 'إشعارات فورية للحجوزات الجديدة والتغييرات الهامة'
		},
		{
			icon: FileText,
			title: 'إدارة الخدمات والأسعار',
			description: 'إضافة وتعديل الخدمات والأسعار بمرونة كاملة'
		},
		{
			icon: Target,
			title: 'حملات تسويقية',
			description: 'أدوات تسويقية لجذب عملاء جدد والاحتفاظ بالحاليين'
		},
		{
			icon: Award,
			title: 'نظام تقييم العملاء',
			description: 'جمع آراء العملاء وتقييماتهم لتحسين جودة الخدمة'
		},
		{
			icon: RefreshCw,
			title: 'نسخ احتياطية تلقائية',
			description: 'حماية بياناتك بنسخ احتياطية يومية آمنة'
		},
		{
			icon: Eye,
			title: 'شفافية كاملة في العمليات',
			description: 'تتبع جميع الأنشطة والتغييرات في النظام'
		}
	];

	// Business types supported
	const businessTypes = [
		{ icon: Scissors, name: 'حلاقة رجالية', count: '1200+' },
		{ icon: Sparkles, name: 'صالونات نسائية', count: '800+' },
		{ icon: Car, name: 'غسيل سيارات', count: '450+' },
		{ icon: Dumbbell, name: 'نوادي رياضية', count: '320+' },
		{ icon: Camera, name: 'استوديوهات تصوير', count: '180+' },
		{ icon: Settings, name: 'خدمات تقنية', count: '160+' }
	];

	// Success metrics
	const metrics = [
		{
			number: '95%',
			label: 'تحسن في تنظيم المواعيد',
			description: 'من الأعمال المستخدمة للمنصة'
		},
		{
			number: '40%',
			label: 'زيادة في معدل الحضور',
			description: 'بفضل التذكيرات التلقائية'
		},
		{
			number: '60%',
			label: 'توفير في الوقت الإداري',
			description: 'عبر الأتمتة الذكية'
		},
		{
			number: '25%',
			label: 'نمو في عدد العملاء الجدد',
			description: 'من خلال أدوات التسويق المدمجة'
		}
	];
</script>

<svelte:head>
	<title>الميزات - Wagtee | أدوات احترافية لإدارة الحجوزات</title>
	<meta name="description" content="اكتشف جميع ميزات منصة Wagtee المتطورة: إشعارات واتساب، رموز QR، تقارير شاملة، وأدوات احترافية لنمو عملك." />
	<meta name="keywords" content="ميزات Wagtee, إشعارات واتساب, رموز QR, تقارير, إدارة حجوزات, أعمال سعودية" />
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
						<Zap class="w-4 h-4 mr-2" />
						ميزات متطورة
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						أدوات <span class="gradient-text">احترافية</span> لإدارة عملك
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
						اكتشف مجموعة شاملة من الأدوات والميزات المصممة خصيصاً لتمكين الأعمال السعودية من النمو والازدهار
					</p>
					<div class="flex gap-4 justify-center flex-wrap">
						<Button size="lg" variant="default" href="/auth/register" class="btn-premium hover-lift px-8">
							ابدأ تجربتك المجانية
							<ArrowRight class="w-4 h-4 mr-2" />
						</Button>
						<Button size="lg" variant="outline" href="/book/public">
							احجز كعميل
							<QrCode class="w-4 h-4 mr-2" />
						</Button>
					</div>
				</div>
			</div>
		</section>

		<!-- Main Features -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="space-y-20">
					{#each mainFeatures as feature, index}
						{@const IconComponent = feature.icon}
						<div class="grid lg:grid-cols-2 gap-12 items-center {index % 2 === 1 ? 'lg:grid-flow-col-dense' : ''}">
							<!-- Content -->
							<div class="space-y-6 {index % 2 === 1 ? 'lg:col-start-2' : ''}">
								<div class="flex items-center gap-4 mb-6">
									<div class="w-16 h-16 {feature.bgColor} rounded-2xl flex items-center justify-center">
										<IconComponent class="w-8 h-8 {feature.color}" />
									</div>
									<div>
										<h2 class="text-3xl font-bold mb-2">{feature.title}</h2>
										<p class="text-lg text-muted-foreground">{feature.subtitle}</p>
									</div>
								</div>
								
								<p class="text-lg text-muted-foreground leading-relaxed mb-6">
									{feature.description}
								</p>
								
								<div class="space-y-3">
									{#each feature.benefits as benefit}
										<div class="flex items-start gap-3">
											<CheckCircle class="w-5 h-5 text-green-600 flex-shrink-0 mt-1" />
											<span class="text-base">{benefit}</span>
										</div>
									{/each}
								</div>
							</div>

							<!-- Visual -->
							<div class="relative {index % 2 === 1 ? 'lg:col-start-1 lg:row-start-1' : ''}">
								<Card class="card-premium hover-lift border-2 {feature.borderColor}">
									<CardContent class="p-8">
										<div class="text-center space-y-6">
											<div class="w-24 h-24 {feature.bgColor} rounded-3xl flex items-center justify-center mx-auto">
												<IconComponent class="w-12 h-12 {feature.color}" />
											</div>
											<div class="space-y-4">
												<div class="h-2 {feature.bgColor} rounded-full"></div>
												<div class="h-2 {feature.bgColor} rounded-full w-3/4 mx-auto opacity-70"></div>
												<div class="h-2 {feature.bgColor} rounded-full w-1/2 mx-auto opacity-50"></div>
											</div>
											<Badge variant="outline" class="text-xs">
												{feature.subtitle}
											</Badge>
										</div>
									</CardContent>
								</Card>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Success Metrics -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">نتائج مُثبتة بالأرقام</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						الأعمال التي تستخدم Wagtee تحقق نتائج استثنائية ونمو ملحوظ
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{#each metrics as metric}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="text-4xl font-bold text-primary mb-2">{metric.number}</div>
								<div class="font-semibold mb-2">{metric.label}</div>
								<div class="text-sm text-muted-foreground">{metric.description}</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Additional Features Grid -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">المزيد من الميزات المتطورة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						مجموعة شاملة من الأدوات لتلبية جميع احتياجات إدارة عملك
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
					{#each additionalFeatures as feature}
						{@const IconComponent = feature.icon}
						<Card class="card-premium hover-lift">
							<CardContent class="p-6">
								<div class="w-12 h-12 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-xl flex items-center justify-center mb-4">
									<IconComponent class="w-6 h-6 text-primary" />
								</div>
								<h3 class="font-bold mb-3">{feature.title}</h3>
								<p class="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Supported Business Types -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">أنواع الأعمال المدعومة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						Wagtee يدعم جميع أنواع الأعمال الخدمية في السوق السعودي
					</p>
				</div>
				<div class="grid md:grid-cols-3 lg:grid-cols-6 gap-6">
					{#each businessTypes as business}
						{@const IconComponent = business.icon}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<IconComponent class="w-8 h-8 text-white" />
								</div>
								<h3 class="font-semibold mb-2">{business.name}</h3>
								<Badge variant="secondary" class="text-xs">
									{business.count} عمل
								</Badge>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Integration & Compatibility -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">متوافق مع النظام البيئي السعودي</h2>
						<p class="text-muted-foreground max-w-2xl mx-auto">
							مُصمم خصيصاً للسوق السعودي مع دعم كامل للمعايير المحلية
						</p>
					</div>
					<div class="grid md:grid-cols-2 gap-8">
						<Card class="card-premium hover-lift">
							<CardContent class="p-8">
								<div class="flex items-center gap-4 mb-6">
									<div class="w-12 h-12 bg-green-50 dark:bg-green-950/20 rounded-xl flex items-center justify-center">
										<Languages class="w-6 h-6 text-green-600" />
									</div>
									<h3 class="text-xl font-bold">الدعم اللغوي</h3>
								</div>
								<ul class="space-y-2 text-muted-foreground">
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										واجهة باللغة العربية والإنجليزية
									</li>
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										رسائل واتساب بالعربية والإنجليزية
									</li>
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										دعم الكتابة من اليمين إلى اليسار
									</li>
								</ul>
							</CardContent>
						</Card>

						<Card class="card-premium hover-lift">
							<CardContent class="p-8">
								<div class="flex items-center gap-4 mb-6">
									<div class="w-12 h-12 bg-blue-50 dark:bg-blue-950/20 rounded-xl flex items-center justify-center">
										<MapPin class="w-6 h-6 text-blue-600" />
									</div>
									<h3 class="text-xl font-bold">المعايير المحلية</h3>
								</div>
								<ul class="space-y-2 text-muted-foreground">
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										التوقيت الزمني لمنطقة الرياض
									</li>
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										دعم أرقام الهواتف السعودية
									</li>
									<li class="flex items-center gap-2">
										<CheckCircle class="w-4 h-4 text-green-600" />
										التقويم الهجري والميلادي
									</li>
								</ul>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">جرب جميع هذه الميزات مجاناً</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
					ابدأ تجربتك المجانية لمدة 14 يوم واكتشف كيف يمكن لهذه الميزات أن تحول عملك
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="/auth/register" class="btn-premium hover-lift">
						ابدأ تجربتك المجانية الآن
					</Button>
					<Button size="lg" variant="outline" class="border-white text-white hover:bg-white hover:text-purple-600" href="/help">
						تعرف على المزيد
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
						<li><a href="/book/public" class="text-muted-foreground hover:text-foreground transition-colors">احجز الآن</a></li>
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