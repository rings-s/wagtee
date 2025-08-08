<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import Navbar from '$lib/components/navbar.svelte';
	
	import { 
		Target,
		Users,
		Shield,
		Zap,
		Heart,
		Globe,
		TrendingUp,
		Award,
		CheckCircle,
		Star,
		MessageCircle,
		Clock
	} from '@lucide/svelte';

	// Team members
	const teamMembers = [
		{
			name: 'أحمد محمد',
			role: 'المؤسس والرئيس التنفيذي',
			description: 'خبرة 10 سنوات في تطوير منصات الأعمال',
			image: '/images/team/ahmed.jpg',
			linkedin: '#'
		},
		{
			name: 'فاطمة العلي',
			role: 'مديرة التطوير التقني',
			description: 'متخصصة في تطوير التطبيقات وتجربة المستخدم',
			image: '/images/team/fatima.jpg',
			linkedin: '#'
		},
		{
			name: 'محمد الرشيد',
			role: 'مدير العمليات',
			description: 'خبير في إدارة الأعمال والعمليات التشغيلية',
			image: '/images/team/mohammed.jpg',
			linkedin: '#'
		}
	];

	// Company values
	const values = [
		{
			icon: Target,
			title: 'التركيز على العميل',
			description: 'نضع احتياجات عملائنا في المقدمة ونسعى لتقديم أفضل تجربة ممكنة',
			color: 'text-blue-600',
			bgColor: 'bg-blue-50 dark:bg-blue-950/20'
		},
		{
			icon: Shield,
			title: 'الأمان والثقة',
			description: 'نحمي بيانات عملائنا بأعلى معايير الأمان والخصوصية',
			color: 'text-green-600',
			bgColor: 'bg-green-50 dark:bg-green-950/20'
		},
		{
			icon: Zap,
			title: 'الابتكار المستمر',
			description: 'نطور حلولاً متقدمة تواكب احتياجات السوق المتغيرة',
			color: 'text-purple-600',
			bgColor: 'bg-purple-50 dark:bg-purple-950/20'
		},
		{
			icon: Heart,
			title: 'الشراكة الحقيقية',
			description: 'نؤمن بأن نجاح عملائنا هو نجاحنا ونعمل كشركاء حقيقيين',
			color: 'text-red-600',
			bgColor: 'bg-red-50 dark:bg-red-950/20'
		}
	];

	// Statistics
	const stats = [
		{ number: '1000+', label: 'عمل تجاري يثق بنا', icon: Users },
		{ number: '50K+', label: 'حجز شهرياً', icon: TrendingUp },
		{ number: '98%', label: 'معدل رضا العملاء', icon: Star },
		{ number: '24/7', label: 'دعم فني متواصل', icon: Clock }
	];
</script>

<svelte:head>
	<title>من نحن - Wagtee</title>
	<meta name="description" content="تعرف على Wagtee، منصة الحجوزات الرائدة في السوق السعودي. رؤيتنا، رسالتنا، وفريق العمل." />
</svelte:head>

<div class="min-h-screen bg-background">
	<Navbar variant="landing" />

	<main>
		<!-- Hero Section -->
		<section class="relative py-20 overflow-hidden">
			<!-- Background gradient -->
			<div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-purple-50/50 dark:from-blue-950/20 dark:via-background dark:to-purple-950/20"></div>
			
			<div class="container mx-auto px-4 relative z-10">
				<div class="max-w-4xl mx-auto text-center">
					<Badge variant="secondary" class="mb-6">
						<Globe class="w-4 h-4 mr-2" />
						رواد في تقنية الحجوزات
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						نحن <span class="gradient-text">Wagtee</span>
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
						منصة تقنية سعودية رائدة تهدف إلى تمكين الأعمال التجارية في السوق المحلي من خلال حلول الحجوزات الذكية والإدارة المتطورة. نؤمن بأن كل عمل سعودي يستحق أدوات تقنية متقدمة تساعده على النمو والازدهار في عصر التحول الرقمي.
					</p>
				</div>
			</div>
		</section>

		<!-- Mission & Vision -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="grid md:grid-cols-2 gap-8">
					<Card class="card-premium hover-lift">
						<CardHeader>
							<div class="w-12 h-12 bg-blue-50 dark:bg-blue-950/20 rounded-xl flex items-center justify-center mb-4">
								<Target class="w-6 h-6 text-blue-600" />
							</div>
							<CardTitle class="text-2xl">رسالتنا</CardTitle>
						</CardHeader>
						<CardContent>
							<p class="text-muted-foreground leading-relaxed">
								تمكين أصحاب الأعمال في السوق السعودي من إدارة حجوزاتهم وعملائهم بكفاءة عالية من خلال منصة تقنية متطورة، سهلة الاستخدام، ومصممة خصيصاً لاحتياجات السوق المحلي. نسعى لدعم رؤية السعودية 2030 من خلال رقمنة الأعمال الصغيرة والمتوسطة وتعزيز ريادة الأعمال في المملكة.
							</p>
						</CardContent>
					</Card>

					<Card class="card-premium hover-lift">
						<CardHeader>
							<div class="w-12 h-12 bg-purple-50 dark:bg-purple-950/20 rounded-xl flex items-center justify-center mb-4">
								<Award class="w-6 h-6 text-purple-600" />
							</div>
							<CardTitle class="text-2xl">رؤيتنا</CardTitle>
						</CardHeader>
						<CardContent>
							<p class="text-muted-foreground leading-relaxed">
								أن نكون المنصة الأولى لإدارة الحجوزات في المملكة العربية السعودية والشرق الأوسط، ونساهم في تطوير قطاع الأعمال الصغيرة والمتوسطة من خلال التقنيات الحديثة والحلول المبتكرة. نطمح لأن نكون جزءاً لا يتجزأ من رحلة التحول الرقمي للاقتصاد السعودي.
							</p>
						</CardContent>
					</Card>
				</div>
			</div>
		</section>

		<!-- Statistics -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">أرقام تتحدث عن نفسها</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						نفخر بالثقة التي يضعها عملاؤنا فينا والنتائج التي نحققها معاً
					</p>
				</div>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
					{#each stats as stat}
						{@const IconComponent = stat.icon}
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
								<IconComponent class="w-8 h-8 text-white" />
							</div>
							<div class="text-3xl font-bold text-primary mb-2">{stat.number}</div>
							<div class="text-sm text-muted-foreground">{stat.label}</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Values -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">قيمنا الأساسية</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						المبادئ التي توجه عملنا وتحدد طريقة تعاملنا مع عملائنا وشركائنا
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{#each values as value}
						{@const IconComponent = value.icon}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="w-16 h-16 {value.bgColor} rounded-2xl flex items-center justify-center mx-auto mb-4">
									<IconComponent class="w-8 h-8 {value.color}" />
								</div>
								<h3 class="font-bold mb-3">{value.title}</h3>
								<p class="text-muted-foreground text-sm leading-relaxed">{value.description}</p>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Team Section -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">فريق العمل</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						مجموعة من المحترفين المتخصصين في التقنية والأعمال يعملون بشغف لتحقيق رؤيتنا
					</p>
				</div>
				<div class="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
					{#each teamMembers as member}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
									<Users class="w-10 h-10 text-white" />
								</div>
								<h3 class="font-bold text-lg mb-1">{member.name}</h3>
								<p class="text-primary font-medium mb-3">{member.role}</p>
								<p class="text-muted-foreground text-sm mb-4">{member.description}</p>
								<Button variant="outline" size="sm" class="hover-lift">
									<MessageCircle class="w-4 h-4 mr-2" />
									تواصل
								</Button>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Why Choose Us -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">لماذا نحن؟</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						الأسباب التي تجعل آلاف الأعمال التجارية تختار Wagtee كشريك في النجاح
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
					<div class="space-y-4">
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">مصمم للسوق السعودي</h4>
								<p class="text-muted-foreground text-sm">مطور خصيصاً لاحتياجات وثقافة السوق المحلي</p>
							</div>
						</div>
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">سهولة الاستخدام</h4>
								<p class="text-muted-foreground text-sm">واجهة بديهية تجعل الإدارة أمراً بسيطاً</p>
							</div>
						</div>
					</div>
					<div class="space-y-4">
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">دعم فني متميز</h4>
								<p class="text-muted-foreground text-sm">فريق دعم محترف متاح 24/7 باللغة العربية</p>
							</div>
						</div>
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">تحديثات مستمرة</h4>
								<p class="text-muted-foreground text-sm">ميزات جديدة وتحسينات بناءً على ملاحظات العملاء</p>
							</div>
						</div>
					</div>
					<div class="space-y-4">
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">أسعار تنافسية</h4>
								<p class="text-muted-foreground text-sm">خطط مرنة تناسب جميع أحجام الأعمال</p>
							</div>
						</div>
						<div class="flex items-start space-x-3">
							<CheckCircle class="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
							<div>
								<h4 class="font-medium mb-1">أمان وموثوقية</h4>
								<p class="text-muted-foreground text-sm">حماية عالية للبيانات وضمان استمرارية الخدمة</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">جاهز للانضمام إلى عائلة Wagtee؟</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
					ابدأ رحلتك معنا اليوم واكتشف كيف يمكن لمنصتنا أن تغير طريقة إدارة عملك
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="/auth/register" class="btn-premium hover-lift">
						ابدأ تجربتك المجانية
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
						<li><a href="/" class="text-muted-foreground hover:text-foreground transition-colors">الميزات</a></li>
						<li><a href="/subscription" class="text-muted-foreground hover:text-foreground transition-colors">الأسعار</a></li>
						<li><a href="/book/public" class="text-muted-foreground hover:text-foreground transition-colors">احجز الآن</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-medium text-foreground mb-3">الدعم</h5>
					<ul class="space-y-2 text-sm">
						<li><a href="/help" class="text-muted-foreground hover:text-foreground transition-colors">مركز المساعدة</a></li>
						<li><a href="/about" class="text-muted-foreground hover:text-foreground transition-colors">من نحن</a></li>
						<li><a href="/auth/login" class="text-muted-foreground hover:text-foreground transition-colors">تسجيل الدخول</a></li>
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