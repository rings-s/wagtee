<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	
	import { 
		Search,
		BookOpen,
		MessageCircle,
		Phone,
		Mail,
		FileText,
		Settings,
		Users,
		Calendar,
		CreditCard,
		Shield,
		ChevronRight,
		HelpCircle,
		Clock,
		CheckCircle,
		Play,
		Download,
		ExternalLink
	} from '@lucide/svelte';

	let searchQuery = $state('');

	// FAQ categories
	const faqCategories = [
		{
			id: 'getting-started',
			title: 'البدء مع Wagtee',
			icon: Play,
			color: 'text-blue-600',
			bgColor: 'bg-blue-50 dark:bg-blue-950/20',
			questions: [
				{
					question: 'كيف أقوم بإنشاء حساب جديد؟',
					answer: 'يمكنك إنشاء حساب جديد بسهولة عبر الضغط على "ابدأ عملك" في الصفحة الرئيسية، ثم ملء المعلومات المطلوبة في خطوتين بسيطتين.'
				},
				{
					question: 'ما هي الخطط المتاحة وأسعارها؟',
					answer: 'نوفر ثلاث خطط: الأساسية (30 ريال/شهر)، المتقدمة (45 ريال/شهر)، والاحترافية (60 ريال/شهر). كل خطة تتضمن ميزات مختلفة لتناسب احتياجات عملك.'
				},
				{
					question: 'هل يمكنني تجربة المنصة مجاناً؟',
					answer: 'نعم، نوفر تجربة مجانية لمدة 14 يوم لجميع الميزات بدون الحاجة لبطاقة ائتمانية.'
				}
			]
		},
		{
			id: 'bookings',
			title: 'إدارة الحجوزات',
			icon: Calendar,
			color: 'text-green-600',
			bgColor: 'bg-green-50 dark:bg-green-950/20',
			questions: [
				{
					question: 'كيف يحجز العملاء المواعيد؟',
					answer: 'العملاء يمكنهم الحجز عبر رابط عملك المخصص، رمز QR، أو يمكنك إدخال الحجوزات يدوياً من لوحة التحكم.'
				},
				{
					question: 'كيف أتعامل مع تعارض المواعيد؟',
					answer: 'النظام يمنع تعارض المواعيد تلقائياً ويعرض فقط الأوقات المتاحة للعملاء عند الحجز.'
				},
				{
					question: 'هل يمكنني تعديل أو إلغاء الحجوزات؟',
					answer: 'نعم، يمكنك تعديل أو إلغاء أي حجز من لوحة التحكم، وسيتم إرسال إشعار تلقائي للعميل.'
				}
			]
		},
		{
			id: 'customers',
			title: 'إدارة العملاء',
			icon: Users,
			color: 'text-purple-600',
			bgColor: 'bg-purple-50 dark:bg-purple-950/20',
			questions: [
				{
					question: 'كيف أدير قاعدة بيانات العملاء؟',
					answer: 'يمكنك عرض وإدارة جميع عملائك من قسم "العملاء" في لوحة التحكم، مع إمكانية البحث والتصفية.'
				},
				{
					question: 'هل يمكن للعملاء الحجز بدون إنشاء حساب؟',
					answer: 'نعم، العملاء يمكنهم الحجز باستخدام رقم الهاتف والاسم فقط بدون الحاجة لإنشاء حساب.'
				},
				{
					question: 'كيف أرسل رسائل للعملاء؟',
					answer: 'يمكنك إرسال رسائل واتساب تلقائية للتذكير بالمواعيد أو إشعارات هامة من خلال النظام.'
				}
			]
		},
		{
			id: 'payments',
			title: 'المدفوعات والاشتراكات',
			icon: CreditCard,
			color: 'text-orange-600',
			bgColor: 'bg-orange-50 dark:bg-orange-950/20',
			questions: [
				{
					question: 'ما هي طرق الدفع المتاحة؟',
					answer: 'ندعم الدفع بالبطاقات الائتمانية، مدى، STC Pay، وطرق الدفع الإلكتروني الأخرى المتاحة في السعودية.'
				},
				{
					question: 'متى يتم خصم رسوم الاشتراك؟',
					answer: 'يتم الخصم شهرياً أو سنوياً حسب الخطة المختارة، مع إمكانية الإلغاء في أي وقت.'
				},
				{
					question: 'هل يمكنني تغيير خطة الاشتراك؟',
					answer: 'نعم، يمكنك ترقية أو تخفيض خطتك في أي وقت من إعدادات الحساب.'
				},
				{
					question: 'هل المنصة متوافقة مع المعايير السعودية؟',
					answer: 'نعم، المنصة مصممة خصيصاً للسوق السعودي مع دعم أرقام الهواتف السعودية (+966) والتوقيت المحلي والتقويم الهجري.'
				},
				{
					question: 'هل يمكن استخدام المنصة في رمضان والمناسبات الدينية؟',
					answer: 'نعم، المنصة تدعم تعديل ساعات العمل للمناسبات الخاصة وإجازات رمضان مع إشعارات مخصصة للعملاء.'
				}
			]
		}
	];

	// Help resources
	const helpResources = [
		{
			title: 'دليل المستخدم الشامل',
			description: 'دليل تفصيلي لجميع ميزات المنصة',
			icon: BookOpen,
			type: 'PDF',
			action: 'تحميل',
			link: '/guides/user-manual.pdf'
		},
		{
			title: 'فيديوهات تعليمية',
			description: 'شروحات مرئية لأهم الميزات',
			icon: Play,
			type: 'فيديو',
			action: 'مشاهدة',
			link: '/tutorials'
		},
		{
			title: 'أسئلة شائعة',
			description: 'إجابات للأسئلة الأكثر شيوعاً',
			icon: HelpCircle,
			type: 'مقال',
			action: 'قراءة',
			link: '#faq'
		}
	];

	// Contact options
	const contactOptions = [
		{
			title: 'الدعم المباشر',
			description: 'تحدث مع فريق الدعم فوراً',
			icon: MessageCircle,
			action: 'بدء محادثة',
			available: 'متاح 24/7',
			color: 'bg-blue-500',
			link: '#chat'
		},
		{
			title: 'الهاتف',
			description: 'اتصل بنا مباشرة',
			icon: Phone,
			action: '+966 11 123 4567',
			available: 'الأحد - الخميس، 9ص - 6م',
			color: 'bg-green-500',
			link: 'tel:+966111234567'
		},
		{
			title: 'البريد الإلكتروني',
			description: 'راسلنا وسنرد خلال 24 ساعة',
			icon: Mail,
			action: 'support@wagtee.sa',
			available: 'رد خلال 24 ساعة',
			color: 'bg-purple-500',
			link: 'mailto:support@wagtee.sa'
		}
	];

	let openQuestion = $state<number | null>(null);

	const toggleQuestion = (index: number) => {
		openQuestion = openQuestion === index ? null : index;
	};

	const filteredFAQs = faqCategories.map(category => ({
		...category,
		questions: category.questions.filter(q => 
			searchQuery === '' || 
			q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
			q.answer.toLowerCase().includes(searchQuery.toLowerCase())
		)
	})).filter(category => category.questions.length > 0);
</script>

<svelte:head>
	<title>مركز المساعدة - Wagtee</title>
	<meta name="description" content="احصل على المساعدة والدعم لمنصة Wagtee. أسئلة شائعة، أدلة المستخدم، والتواصل مع فريق الدعم." />
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
						<HelpCircle class="w-4 h-4 mr-2" />
						مركز المساعدة
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						كيف يمكننا <span class="gradient-text">مساعدتك</span>؟
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
						ابحث عن إجابات لأسئلتك، تصفح أدلة المساعدة، أو تواصل مع فريق الدعم المتخصص في الأعمال السعودية. نحن هنا لمساعدتك في تحقيق أقصى استفادة من منصة Wagtee
					</p>
					
					<!-- Search Bar -->
					<div class="max-w-2xl mx-auto">
						<div class="relative">
							<Search class="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
							<Input
								type="text"
								placeholder="ابحث عن سؤالك..."
								bind:value={searchQuery}
								class="pl-12 h-14 text-lg rounded-2xl glass-effect focus-enhanced"
							/>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Quick Help Resources -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">مصادر المساعدة السريعة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						احصل على المساعدة التي تحتاجها بأسرع وقت ممكن
					</p>
				</div>
				<div class="grid md:grid-cols-3 gap-8">
					{#each helpResources as resource}
						{@const IconComponent = resource.icon}
						<Card class="card-premium hover-lift text-center group">
							<CardContent class="p-6">
								<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
									<IconComponent class="w-8 h-8 text-white" />
								</div>
								<h3 class="font-bold text-lg mb-2">{resource.title}</h3>
								<p class="text-muted-foreground text-sm mb-4">{resource.description}</p>
								<Badge variant="secondary" class="mb-4">{resource.type}</Badge>
								<div>
									<Button variant="outline" size="sm" href={resource.link} class="hover-lift">
										{resource.action}
										<ExternalLink class="w-4 h-4 mr-2" />
									</Button>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- FAQ Section -->
		<section id="faq" class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">الأسئلة الشائعة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						إجابات للأسئلة الأكثر شيوعاً من مستخدمي Wagtee
					</p>
				</div>

				{#each filteredFAQs as category, categoryIndex}
					{@const IconComponent = category.icon}
					<div class="mb-12">
						<div class="flex items-center mb-6">
							<div class="w-12 h-12 {category.bgColor} rounded-xl flex items-center justify-center mr-4">
								<IconComponent class="w-6 h-6 {category.color}" />
							</div>
							<h3 class="text-2xl font-bold">{category.title}</h3>
						</div>
						
						<div class="space-y-4">
							{#each category.questions as question, questionIndex}
								{@const globalIndex = categoryIndex * 100 + questionIndex}
								<Card class="card-premium">
									<button
										class="w-full text-left p-6 focus:outline-none focus:ring-2 focus:ring-ring"
										onclick={() => toggleQuestion(globalIndex)}
									>
										<div class="flex items-center justify-between">
											<h4 class="font-medium text-lg pr-6">{question.question}</h4>
											<ChevronRight class="w-5 h-5 text-muted-foreground transition-transform duration-200 {openQuestion === globalIndex ? 'rotate-90' : ''}" />
										</div>
									</button>
									{#if openQuestion === globalIndex}
										<div class="px-6 pb-6">
											<div class="border-t border-border pt-4">
												<p class="text-muted-foreground leading-relaxed">{question.answer}</p>
											</div>
										</div>
									{/if}
								</Card>
							{/each}
						</div>
					</div>
				{/each}

				{#if searchQuery && filteredFAQs.length === 0}
					<div class="text-center py-12">
						<HelpCircle class="w-16 h-16 text-muted-foreground mx-auto mb-4" />
						<h3 class="text-xl font-medium mb-2">لم نجد نتائج لبحثك</h3>
						<p class="text-muted-foreground mb-6">جرب كلمات أخرى أو تواصل مع فريق الدعم</p>
						<Button href="#contact">تواصل مع الدعم</Button>
					</div>
				{/if}
			</div>
		</section>

		<!-- Contact Support -->
		<section id="contact" class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">تواصل مع فريق الدعم</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						لم تجد ما تبحث عنه؟ فريق الدعم جاهز لمساعدتك
					</p>
				</div>
				<div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
					{#each contactOptions as option}
						{@const IconComponent = option.icon}
						<Card class="card-premium hover-lift text-center group">
							<CardContent class="p-6">
								<div class="w-16 h-16 {option.color} rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
									<IconComponent class="w-8 h-8 text-white" />
								</div>
								<h3 class="font-bold text-lg mb-2">{option.title}</h3>
								<p class="text-muted-foreground text-sm mb-4">{option.description}</p>
								<div class="space-y-2 mb-6">
									<div class="font-medium">{option.action}</div>
									<div class="text-sm text-muted-foreground flex items-center justify-center">
										<Clock class="w-4 h-4 mr-1" />
										{option.available}
									</div>
								</div>
								<Button variant="outline" size="sm" href={option.link} class="hover-lift">
									تواصل الآن
								</Button>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Status Updates -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-8">
						<h2 class="text-2xl font-bold mb-4">حالة الخدمة</h2>
						<p class="text-muted-foreground">تحديثات حول حالة منصة Wagtee</p>
					</div>
					<Card class="card-premium">
						<CardContent class="p-6">
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-3">
									<CheckCircle class="w-6 h-6 text-green-600" />
									<div>
										<h3 class="font-medium">جميع الأنظمة تعمل بشكل طبيعي</h3>
										<p class="text-sm text-muted-foreground">آخر تحديث: اليوم، 10:30 ص</p>
									</div>
								</div>
								<Button variant="outline" size="sm" href="/status">
									عرض التفاصيل
									<ExternalLink class="w-4 h-4 mr-2" />
								</Button>
							</div>
						</CardContent>
					</Card>
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">ما زلت بحاجة للمساعدة؟</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
					فريق الدعم المتخصص جاهز لمساعدتك في أي وقت
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="#contact" class="btn-premium hover-lift">
						تواصل مع الدعم
					</Button>
					<Button size="lg" variant="outline" class="border-white text-white hover:bg-white hover:text-purple-600" href="/about">
						تعرف على Wagtee
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
					<h5 class="font-medium text-foreground mb-3">المساعدة</h5>
					<ul class="space-y-2 text-sm">
						<li><a href="/help" class="text-muted-foreground hover:text-foreground transition-colors">مركز المساعدة</a></li>
						<li><a href="/help#faq" class="text-muted-foreground hover:text-foreground transition-colors">أسئلة شائعة</a></li>
						<li><a href="/tutorials" class="text-muted-foreground hover:text-foreground transition-colors">فيديوهات تعليمية</a></li>
					</ul>
				</div>
				<div>
					<h5 class="font-medium text-foreground mb-3">الدعم</h5>
					<ul class="space-y-2 text-sm">
						<li><a href="#contact" class="text-muted-foreground hover:text-foreground transition-colors">تواصل معنا</a></li>
						<li><a href="/status" class="text-muted-foreground hover:text-foreground transition-colors">حالة الخدمة</a></li>
						<li><a href="/about" class="text-muted-foreground hover:text-foreground transition-colors">من نحن</a></li>
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