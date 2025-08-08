<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	
	import { 
		Check, 
		Crown, 
		Star, 
		Zap,
		Users,
		Calendar,
		FileText,
		Shield,
		HeadphonesIcon
	} from '@lucide/svelte';

	// Subscription tiers data based on backend models
	const subscriptionTiers = [
		{
			id: 'basic',
			name: 'الأساسية',
			nameEn: 'Basic',
			price: 30,
			period: 'شهرياً',
			description: 'مثالية للأعمال الصغيرة والناشئة',
			icon: Users,
			color: 'text-blue-600',
			bgColor: 'bg-blue-50',
			borderColor: 'border-blue-200',
			features: [
				'حتى 3 خدمات',
				'50 حجز شهرياً',
				'100 عميل',
				'دعم فني أساسي',
				'تقارير أساسية',
				'واتساب للإشعارات'
			],
			limits: {
				services: 3,
				bookings: 50,
				customers: 100
			}
		},
		{
			id: 'standard',
			name: 'المتقدمة',
			nameEn: 'Standard', 
			price: 45,
			period: 'شهرياً',
			description: 'الخيار الأمثل للأعمال المتنامية',
			icon: Star,
			color: 'text-purple-600',
			bgColor: 'bg-purple-50',
			borderColor: 'border-purple-200',
			popular: true,
			features: [
				'حتى 7 خدمات',
				'150 حجز شهرياً', 
				'300 عميل',
				'دعم فني ذو أولوية',
				'تقارير متقدمة',
				'واتساب للإشعارات',
				'رموز QR للحجز',
				'تذكيرات تلقائية'
			],
			limits: {
				services: 7,
				bookings: 150,
				customers: 300
			}
		},
		{
			id: 'premium',
			name: 'الاحترافية',
			nameEn: 'Premium',
			price: 60,
			period: 'شهرياً',
			description: 'للأعمال الكبيرة والاحترافية',
			icon: Crown,
			color: 'text-gold-600',
			bgColor: 'bg-yellow-50',
			borderColor: 'border-yellow-200',
			features: [
				'خدمات غير محدودة',
				'حجوزات غير محدودة',
				'عملاء غير محدودون',
				'دعم فني VIP',
				'تقارير احترافية',
				'واتساب للإشعارات',
				'رموز QR للحجز',
				'تذكيرات تلقائية',
				'API متقدم',
				'تخصيص كامل'
			],
			limits: {
				services: -1, // unlimited
				bookings: -1, // unlimited  
				customers: -1 // unlimited
			}
		}
	];

	// Current user subscription (from store in real app)
	let currentTier = 'basic';
	let isSubscriptionActive = true;

	const handleUpgrade = (tierId: string) => {
		console.log(`Upgrading to ${tierId}`);
		// Payment gateway integration removed for testing mode
		alert(`تم طلب الترقية إلى خطة ${subscriptionTiers.find(t => t.id === tierId)?.name}. سيتم تفعيلها قريباً لأغراض الاختبار.`);
	};

	const handleManageSubscription = () => {
		console.log('Managing subscription');
		// Payment gateway integration removed for testing mode
		alert('إدارة الاشتراك متاحة بعد إعداد نظام الدفع في الإنتاج.');
	};
</script>

<svelte:head>
	<title>خطط الاشتراك - Wagtee</title>
	<meta name="description" content="اختر خطة الاشتراك المناسبة لعملك في منصة Wagtee" />
</svelte:head>

<div class="min-h-screen bg-background">

	<div class="container mx-auto px-4 py-12">
		<!-- Hero Section -->
		<div class="text-center mb-16">
			<h2 class="text-4xl font-bold mb-4">اختر الخطة المناسبة لعملك</h2>
			<p class="text-xl text-muted-foreground max-w-2xl mx-auto">
				جميع الخطط تشمل ميزات أساسية قوية لإدارة حجوزات عملك بكفاءة
			</p>
		</div>

		<!-- Current Subscription Status -->
		{#if isSubscriptionActive}
			<div class="mb-8">
				<Card class="border-green-200 bg-green-50">
					<CardContent class="p-6">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-4">
								<div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
									<Check class="w-6 h-6 text-white" />
								</div>
								<div>
									<h3 class="font-semibold text-green-800">اشتراكك نشط</h3>
									<p class="text-green-600">
										الخطة الحالية: <span class="font-medium">
											{subscriptionTiers.find(tier => tier.id === currentTier)?.name}
										</span>
									</p>
								</div>
							</div>
							<Button variant="outline" onclick={handleManageSubscription}>
								إدارة الاشتراك
							</Button>
						</div>
					</CardContent>
				</Card>
			</div>
		{/if}

		<!-- Pricing Cards -->
		<div class="grid md:grid-cols-3 gap-8 mb-16">
			{#each subscriptionTiers as tier}
				{@const IconComponent = tier.icon}
				<Card class="relative {tier.popular ? 'ring-2 ring-purple-500 scale-105' : ''} {tier.borderColor}">
					{#if tier.popular}
						<div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
							<Badge class="bg-purple-600 text-white px-4 py-1">الأكثر شعبية</Badge>
						</div>
					{/if}
					
					<CardHeader class="text-center pb-8 {tier.bgColor}">
						<div class="w-16 h-16 mx-auto mb-4 {tier.bgColor} rounded-full flex items-center justify-center">
							<IconComponent class="w-8 h-8 {tier.color}" />
						</div>
						<CardTitle class="text-2xl mb-2">{tier.name}</CardTitle>
						<CardDescription class="mb-4">{tier.description}</CardDescription>
						<div class="text-4xl font-bold {tier.color}">
							{tier.price} <span class="text-lg font-normal text-muted-foreground">ريال</span>
						</div>
						<p class="text-muted-foreground">{tier.period}</p>
					</CardHeader>

					<CardContent class="pt-6">
						<ul class="space-y-3 mb-8">
							{#each tier.features as feature}
								<li class="flex items-center gap-3">
									<Check class="w-5 h-5 text-green-600 flex-shrink-0" />
									<span class="text-sm">{feature}</span>
								</li>
							{/each}
						</ul>

						{#if currentTier === tier.id && isSubscriptionActive}
							<Button variant="outline" class="w-full" disabled>
								الخطة الحالية
							</Button>
						{:else if tier.id === 'basic' && (currentTier === 'standard' || currentTier === 'premium')}
							<Button variant="outline" class="w-full" disabled>
								إنقاص
							</Button>
						{:else}
							<Button 
								class="w-full {tier.popular ? 'bg-purple-600 hover:bg-purple-700' : ''}" 
								onclick={() => handleUpgrade(tier.id)}
							>
								{currentTier === 'basic' && tier.id !== 'basic' ? 'ترقية' : 'اختيار'} الخطة
							</Button>
						{/if}
					</CardContent>
				</Card>
			{/each}
		</div>

		<!-- Feature Comparison -->
		<div class="mb-16">
			<h3 class="text-2xl font-bold text-center mb-8">مقارنة الميزات</h3>
			<Card>
				<CardContent class="p-0">
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="border-b bg-muted/50">
								<tr>
									<th class="text-right p-4 font-medium">الميزة</th>
									<th class="text-center p-4 font-medium">الأساسية</th>
									<th class="text-center p-4 font-medium">المتقدمة</th>
									<th class="text-center p-4 font-medium">الاحترافية</th>
								</tr>
							</thead>
							<tbody>
								<tr class="border-b">
									<td class="p-4 font-medium">عدد الخدمات</td>
									<td class="text-center p-4">3</td>
									<td class="text-center p-4">7</td>
									<td class="text-center p-4">غير محدود</td>
								</tr>
								<tr class="border-b">
									<td class="p-4 font-medium">الحجوزات الشهرية</td>
									<td class="text-center p-4">50</td>
									<td class="text-center p-4">150</td>
									<td class="text-center p-4">غير محدود</td>
								</tr>
								<tr class="border-b">
									<td class="p-4 font-medium">عدد العملاء</td>
									<td class="text-center p-4">100</td>
									<td class="text-center p-4">300</td>
									<td class="text-center p-4">غير محدود</td>
								</tr>
								<tr class="border-b">
									<td class="p-4 font-medium">رموز QR للحجز</td>
									<td class="text-center p-4">❌</td>
									<td class="text-center p-4">✅</td>
									<td class="text-center p-4">✅</td>
								</tr>
								<tr class="border-b">
									<td class="p-4 font-medium">التذكيرات التلقائية</td>
									<td class="text-center p-4">❌</td>
									<td class="text-center p-4">✅</td>
									<td class="text-center p-4">✅</td>
								</tr>
								<tr class="border-b">
									<td class="p-4 font-medium">API متقدم</td>
									<td class="text-center p-4">❌</td>
									<td class="text-center p-4">❌</td>
									<td class="text-center p-4">✅</td>
								</tr>
								<tr>
									<td class="p-4 font-medium">الدعم الفني</td>
									<td class="text-center p-4">أساسي</td>
									<td class="text-center p-4">ذو أولوية</td>
									<td class="text-center p-4">VIP</td>
								</tr>
							</tbody>
						</table>
					</div>
				</CardContent>
			</Card>
		</div>

		<!-- FAQ Section -->
		<div class="mb-16">
			<h3 class="text-2xl font-bold text-center mb-8">الأسئلة الشائعة</h3>
			<div class="grid md:grid-cols-2 gap-8">
				<Card>
					<CardHeader>
						<CardTitle class="text-lg">هل يمكنني تغيير خطتي؟</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">
							نعم، يمكنك ترقية أو تخفيض خطتك في أي وقت. التغييرات ستسري مفعولها في دورة الفوترة التالية.
						</p>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle class="text-lg">هل توجد رسوم إعداد؟</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">
							لا توجد رسوم إعداد أو رسوم خفية. الأسعار المعروضة شاملة لجميع الميزات.
						</p>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle class="text-lg">ماذا يحدث عند انتهاء الاشتراك؟</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">
							ستحتفظ ببياناتك لمدة 30 يوماً بعد انتهاء الاشتراك، مع إمكانية الوصول للقراءة فقط.
						</p>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle class="text-lg">طرق الدفع المقبولة؟</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">
							نقبل جميع بطاقات الائتمان الرئيسية، مدى، STC Pay، وتحويل بنكي.
						</p>
					</CardContent>
				</Card>
			</div>
		</div>

		<!-- Contact Support -->
		<div class="text-center">
			<Card class="max-w-2xl mx-auto">
				<CardHeader>
					<div class="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
						<HeadphonesIcon class="w-8 h-8 text-blue-600" />
					</div>
					<CardTitle>هل تحتاج مساعدة في الاختيار؟</CardTitle>
					<CardDescription>
						فريق خدمة العملاء جاهز لمساعدتك في اختيار الخطة المناسبة لعملك
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div class="flex items-center justify-center gap-4">
						<Button variant="outline">
							تواصل معنا
						</Button>
						<Button>
							احجز مكالمة مجانية
						</Button>
					</div>
				</CardContent>
			</Card>
		</div>
	</div>
</div>