<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Textarea } from '$lib/components/ui/textarea/index.js';
	
	import { 
		MessageCircle,
		Phone,
		Mail,
		MapPin,
		Clock,
		Send,
		CheckCircle,
		Globe,
		Users,
		Headphones,
		Calendar,
		Star,
		Award,
		Shield,
		Zap,
		ArrowRight
	} from '@lucide/svelte';

	// Contact methods
	const contactMethods = [
		{
			icon: MessageCircle,
			title: 'الدعم المباشر',
			subtitle: 'أسرع طريقة للحصول على المساعدة',
			description: 'تحدث مع فريق الدعم الفني المتخصص فوراً عبر الدردشة المباشرة',
			action: 'بدء محادثة',
			availability: 'متاح 24/7',
			color: 'bg-blue-500',
			hoverColor: 'hover:bg-blue-600',
			link: '#chat'
		},
		{
			icon: Phone,
			title: 'الهاتف',
			subtitle: 'للاستفسارات العاجلة والدعم المباشر',
			description: 'اتصل بنا مباشرة للحصول على دعم فوري ومساعدة مخصصة',
			action: '+966 11 123 4567',
			availability: 'الأحد - الخميس، 9 صباحاً - 6 مساءً',
			color: 'bg-green-500',
			hoverColor: 'hover:bg-green-600',
			link: 'tel:+966111234567'
		},
		{
			icon: Mail,
			title: 'البريد الإلكتروني',
			subtitle: 'للاستفسارات التفصيلية والمراسلات الرسمية',
			description: 'راسلنا وسنرد عليك خلال 24 ساعة بحلول مفصلة ومخصصة',
			action: 'support@wagtee.sa',
			availability: 'رد مضمون خلال 24 ساعة',
			color: 'bg-purple-500',
			hoverColor: 'hover:bg-purple-600',
			link: 'mailto:support@wagtee.sa'
		}
	];

	// Office information
	const officeInfo = {
		address: 'مركز الملك عبدالله المالي، الرياض 11564، المملكة العربية السعودية',
		phone: '+966 11 123 4567',
		email: 'info@wagtee.sa',
		workingHours: {
			weekdays: 'الأحد - الخميس: 9:00 ص - 6:00 م',
			weekend: 'الجمعة - السبت: مغلق (دعم فني متاح)'
		}
	};

	// Support categories
	const supportCategories = [
		{
			icon: Users,
			title: 'دعم العملاء',
			description: 'مساعدة في استخدام المنصة وحل المشاكل',
			email: 'support@wagtee.sa'
		},
		{
			icon: Globe,
			title: 'المبيعات والشراكات',
			description: 'استفسارات الخطط والأسعار والشراكات التجارية',
			email: 'sales@wagtee.sa'
		},
		{
			icon: Shield,
			title: 'الأمان والخصوصية',
			description: 'قضايا الأمان وحماية البيانات والخصوصية',
			email: 'security@wagtee.sa'
		},
		{
			icon: Headphones,
			title: 'الدعم التقني',
			description: 'مشاكل تقنية ومتطلبات تطوير خاصة',
			email: 'tech@wagtee.sa'
		}
	];

	// Why contact us reasons
	const whyContactUs = [
		{
			icon: CheckCircle,
			title: 'فريق متخصص',
			description: 'خبراء في الأعمال السعودية ومتطلبات السوق المحلي'
		},
		{
			icon: Clock,
			title: 'استجابة سريعة',
			description: 'نرد على جميع الاستفسارات خلال ساعات قليلة'
		},
		{
			icon: Star,
			title: 'حلول مخصصة',
			description: 'نقدم حلول مناسبة لاحتياجات عملك الخاصة'
		},
		{
			icon: Award,
			title: 'خبرة موثوقة',
			description: 'سنوات من الخبرة في خدمة الأعمال السعودية'
		}
	];

	// FAQ quick answers
	const quickFAQ = [
		{
			question: 'كم تستغرق مدة الرد على الاستفسارات؟',
			answer: 'نرد على الدردشة المباشرة فوراً، والبريد الإلكتروني خلال 24 ساعة.'
		},
		{
			question: 'هل يمكنني طلب عرض توضيحي مخصص؟',
			answer: 'نعم، يمكنك حجز جلسة عرض توضيحي مخصصة مجاناً مع فريقنا.'
		},
		{
			question: 'هل تقدمون دعم باللغة العربية؟',
			answer: 'نعم، جميع فرق الدعم تتحدث العربية والإنجليزية بطلاقة.'
		},
		{
			question: 'كيف يمكنني الإبلاغ عن مشكلة تقنية؟',
			answer: 'يمكنك الإبلاغ عبر الدردشة المباشرة أو البريد الإلكتروني مع تفاصيل المشكلة.'
		}
	];

	// Form state
	let formData = {
		name: '',
		email: '',
		phone: '',
		company: '',
		subject: '',
		category: '',
		message: ''
	};

	let isSubmitting = false;
	let submitted = false;

	const handleSubmit = async (event: Event) => {
		event.preventDefault();
		isSubmitting = true;
		
		// Simulate form submission
		setTimeout(() => {
			isSubmitting = false;
			submitted = true;
		}, 2000);
	};
</script>

<svelte:head>
	<title>تواصل معنا - Wagtee | دعم متخصص للأعمال السعودية</title>
	<meta name="description" content="تواصل مع فريق Wagtee المتخصص. دعم فني 24/7، استشارات مجانية، وحلول مخصصة للأعمال السعودية." />
	<meta name="keywords" content="دعم Wagtee, تواصل معنا, دعم فني, استشارات, الرياض, السعودية" />
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
						<MessageCircle class="w-4 h-4 mr-2" />
						دعم متخصص
					</Badge>
					<h1 class="text-4xl md:text-5xl font-bold mb-6 leading-tight">
						<span class="gradient-text">تواصل معنا</span> نحن هنا للمساعدة
					</h1>
					<p class="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
						فريق متخصص من الخبراء جاهز لمساعدتك في جميع استفساراتك وتقديم الدعم المناسب لنمو عملك
					</p>
				</div>
			</div>
		</section>

		<!-- Contact Methods -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">اختر طريقة التواصل المناسبة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						عدة طرق للتواصل معنا لضمان حصولك على أفضل دعم ممكن
					</p>
				</div>
				<div class="grid md:grid-cols-3 gap-8">
					{#each contactMethods as method}
						{@const IconComponent = method.icon}
						<Card class="card-premium hover-lift group">
							<CardContent class="p-8 text-center">
								<div class="w-16 h-16 {method.color} {method.hoverColor} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-all duration-300">
									<IconComponent class="w-8 h-8 text-white" />
								</div>
								<h3 class="text-xl font-bold mb-2">{method.title}</h3>
								<p class="text-sm font-medium text-muted-foreground mb-3">{method.subtitle}</p>
								<p class="text-muted-foreground text-sm mb-6 leading-relaxed">
									{method.description}
								</p>
								<div class="space-y-4 mb-6">
									<div class="font-medium text-lg">{method.action}</div>
									<div class="text-sm text-muted-foreground flex items-center justify-center gap-2">
										<Clock class="w-4 h-4" />
										{method.availability}
									</div>
								</div>
								<Button 
									variant="outline" 
									class="w-full hover-lift"
									href={method.link}
								>
									تواصل الآن
								</Button>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Contact Form -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">أرسل لنا رسالة</h2>
						<p class="text-muted-foreground max-w-2xl mx-auto">
							املأ النموذج أدناه وسنتواصل معك في أقرب وقت ممكن
						</p>
					</div>

					{#if submitted}
						<Card class="card-premium text-center">
							<CardContent class="p-12">
								<div class="w-16 h-16 bg-green-50 dark:bg-green-950/20 rounded-full flex items-center justify-center mx-auto mb-6">
									<CheckCircle class="w-8 h-8 text-green-600" />
								</div>
								<h3 class="text-2xl font-bold mb-4">تم إرسال رسالتك بنجاح!</h3>
								<p class="text-muted-foreground mb-8">
									شكراً لتواصلك معنا. سنرد عليك خلال 24 ساعة على البريد الإلكتروني المُدخل.
								</p>
								<Button onclick={() => submitted = false}>
									إرسال رسالة أخرى
								</Button>
							</CardContent>
						</Card>
					{:else}
						<Card class="card-premium">
							<CardContent class="p-8">
								<form on:submit={handleSubmit} class="space-y-6">
									<div class="grid md:grid-cols-2 gap-6">
										<div class="space-y-2">
											<Label for="name">الاسم الكامل *</Label>
											<Input 
												id="name" 
												type="text" 
												placeholder="أدخل اسمك الكامل"
												bind:value={formData.name}
												required 
											/>
										</div>
										<div class="space-y-2">
											<Label for="email">البريد الإلكتروني *</Label>
											<Input 
												id="email" 
												type="email" 
												placeholder="example@email.com"
												bind:value={formData.email}
												required 
											/>
										</div>
									</div>

									<div class="grid md:grid-cols-2 gap-6">
										<div class="space-y-2">
											<Label for="phone">رقم الهاتف</Label>
											<Input 
												id="phone" 
												type="tel" 
												placeholder="+966 5X XXX XXXX"
												bind:value={formData.phone}
											/>
										</div>
										<div class="space-y-2">
											<Label for="company">اسم الشركة/العمل</Label>
											<Input 
												id="company" 
												type="text" 
												placeholder="اسم شركتك أو عملك"
												bind:value={formData.company}
											/>
										</div>
									</div>

									<div class="grid md:grid-cols-2 gap-6">
										<div class="space-y-2">
											<Label for="category">نوع الاستفسار</Label>
											<select 
												id="category"
												bind:value={formData.category}
												class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
											>
												<option value="">اختر نوع الاستفسار</option>
												<option value="support">الدعم التقني</option>
												<option value="sales">المبيعات والأسعار</option>
												<option value="partnership">الشراكات التجارية</option>
												<option value="feedback">ملاحظات واقتراحات</option>
												<option value="other">أخرى</option>
											</select>
										</div>
										<div class="space-y-2">
											<Label for="subject">موضوع الرسالة *</Label>
											<Input 
												id="subject" 
												type="text" 
												placeholder="موضوع الرسالة"
												bind:value={formData.subject}
												required 
											/>
										</div>
									</div>

									<div class="space-y-2">
										<Label for="message">الرسالة *</Label>
										<Textarea 
											id="message" 
											placeholder="اكتب رسالتك هنا..."
											rows={6}
											bind:value={formData.message}
											required 
										/>
									</div>

									<Button 
										type="submit" 
										class="w-full h-12 text-lg font-semibold"
										disabled={isSubmitting}
									>
										{#if isSubmitting}
											جاري الإرسال...
										{:else}
											إرسال الرسالة
											<Send class="w-4 h-4 mr-2" />
										{/if}
									</Button>
								</form>
							</CardContent>
						</Card>
					{/if}
				</div>
			</div>
		</section>

		<!-- Support Categories -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">أقسام الدعم المتخصصة</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						فرق متخصصة للإجابة على جميع أنواع الاستفسارات
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{#each supportCategories as category}
						{@const IconComponent = category.icon}
						<Card class="card-premium hover-lift text-center">
							<CardContent class="p-6">
								<div class="w-16 h-16 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<IconComponent class="w-8 h-8 text-primary" />
								</div>
								<h3 class="font-bold mb-3">{category.title}</h3>
								<p class="text-muted-foreground text-sm mb-4 leading-relaxed">
									{category.description}
								</p>
								<Button variant="outline" size="sm" href="mailto:{category.email}">
									{category.email}
								</Button>
							</CardContent>
						</Card>
					{/each}
				</div>
			</div>
		</section>

		<!-- Office Information -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">معلومات المكتب</h2>
						<p class="text-muted-foreground">
							قم بزيارتنا أو تواصل معنا مباشرة
						</p>
					</div>
					<div class="grid md:grid-cols-2 gap-8">
						<Card class="card-premium">
							<CardContent class="p-8">
								<div class="space-y-6">
									<div class="flex items-start gap-4">
										<div class="w-12 h-12 bg-blue-50 dark:bg-blue-950/20 rounded-xl flex items-center justify-center flex-shrink-0">
											<MapPin class="w-6 h-6 text-blue-600" />
										</div>
										<div>
											<h3 class="font-semibold mb-2">العنوان</h3>
											<p class="text-muted-foreground text-sm leading-relaxed">
												{officeInfo.address}
											</p>
										</div>
									</div>

									<div class="flex items-start gap-4">
										<div class="w-12 h-12 bg-green-50 dark:bg-green-950/20 rounded-xl flex items-center justify-center flex-shrink-0">
											<Phone class="w-6 h-6 text-green-600" />
										</div>
										<div>
											<h3 class="font-semibold mb-2">الهاتف</h3>
											<p class="text-muted-foreground text-sm">
												{officeInfo.phone}
											</p>
										</div>
									</div>

									<div class="flex items-start gap-4">
										<div class="w-12 h-12 bg-purple-50 dark:bg-purple-950/20 rounded-xl flex items-center justify-center flex-shrink-0">
											<Mail class="w-6 h-6 text-purple-600" />
										</div>
										<div>
											<h3 class="font-semibold mb-2">البريد الإلكتروني</h3>
											<p class="text-muted-foreground text-sm">
												{officeInfo.email}
											</p>
										</div>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card class="card-premium">
							<CardContent class="p-8">
								<div class="space-y-6">
									<div class="flex items-start gap-4">
										<div class="w-12 h-12 bg-orange-50 dark:bg-orange-950/20 rounded-xl flex items-center justify-center flex-shrink-0">
											<Clock class="w-6 h-6 text-orange-600" />
										</div>
										<div>
											<h3 class="font-semibold mb-2">ساعات العمل</h3>
											<div class="space-y-2 text-muted-foreground text-sm">
												<p>{officeInfo.workingHours.weekdays}</p>
												<p>{officeInfo.workingHours.weekend}</p>
											</div>
										</div>
									</div>

									<div class="flex items-start gap-4">
										<div class="w-12 h-12 bg-red-50 dark:bg-red-950/20 rounded-xl flex items-center justify-center flex-shrink-0">
											<Calendar class="w-6 h-6 text-red-600" />
										</div>
										<div>
											<h3 class="font-semibold mb-2">حجز موعد</h3>
											<p class="text-muted-foreground text-sm mb-4">
												احجز موعد مع فريق المبيعات لعرض توضيحي مخصص
											</p>
											<Button variant="outline" size="sm">
												احجز موعد
											</Button>
										</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>
		</section>

		<!-- Why Contact Us -->
		<section class="py-16">
			<div class="container mx-auto px-4">
				<div class="text-center mb-12">
					<h2 class="text-3xl font-bold mb-4">لماذا تتواصل معنا؟</h2>
					<p class="text-muted-foreground max-w-2xl mx-auto">
						الأسباب التي تجعل عملاءنا يثقون في دعمنا وخبرتنا
					</p>
				</div>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
					{#each whyContactUs as reason}
						{@const IconComponent = reason.icon}
						<div class="text-center">
							<div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
								<IconComponent class="w-8 h-8 text-white" />
							</div>
							<h3 class="font-bold mb-3">{reason.title}</h3>
							<p class="text-muted-foreground text-sm leading-relaxed">{reason.description}</p>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Quick FAQ -->
		<section class="py-16 bg-muted/30">
			<div class="container mx-auto px-4">
				<div class="max-w-4xl mx-auto">
					<div class="text-center mb-12">
						<h2 class="text-3xl font-bold mb-4">أسئلة سريعة</h2>
						<p class="text-muted-foreground">
							إجابات فورية للأسئلة الأكثر شيوعاً
						</p>
					</div>
					<div class="space-y-6">
						{#each quickFAQ as faq}
							<Card class="card-premium">
								<CardContent class="p-6">
									<h3 class="font-semibold mb-3">{faq.question}</h3>
									<p class="text-muted-foreground leading-relaxed">{faq.answer}</p>
								</CardContent>
							</Card>
						{/each}
					</div>
					<div class="text-center mt-8">
						<Button variant="outline" href="/help">
							المزيد من الأسئلة الشائعة
							<ArrowRight class="w-4 h-4 mr-2" />
						</Button>
					</div>
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
			<div class="container mx-auto px-4 text-center">
				<h2 class="text-3xl font-bold mb-4">جاهز لبدء رحلتك مع Wagtee؟</h2>
				<p class="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
					تواصل معنا الآن وابدأ تجربتك المجانية لمدة 14 يوم
				</p>
				<div class="flex gap-4 justify-center flex-wrap">
					<Button size="lg" variant="secondary" href="/auth/register" class="btn-premium hover-lift">
						ابدأ تجربتك المجانية
					</Button>
					<Button size="lg" variant="outline" class="border-white text-white hover:bg-white hover:text-purple-600" href="#chat">
						تحدث مع فريق المبيعات
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