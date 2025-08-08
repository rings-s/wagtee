<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs/index.js';
	import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '$lib/components/ui/table/index.js';
	import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '$lib/components/ui/dialog/index.js';
	import ModeToggle from '$lib/components/mode-toggle.svelte';
	
	import { 
		dashboardStats, 
		bookings, 
		services, 
		customers,
		getServiceById,
		getCustomerById 
	} from '$lib/data/dummy.js';
	import { formatCurrency, formatDate, formatTime } from '$lib/utils/index.js';
	import type { Service, Booking, Customer, ServiceForm } from '$lib/types/index.js';
	
	import { 
		Calendar, 
		Users, 
		DollarSign, 
		TrendingUp, 
		Clock, 
		Star,
		Settings,
		LogOut,
		Plus,
		Search,
		Filter,
		Edit,
		Trash2,
		Eye,
		ChevronLeft,
		ChevronRight,
		MoreHorizontal,
		Download,
		Upload
	} from '@lucide/svelte';

	// State management
	let activeTab = $state('overview');
	let searchQuery = $state('');
	let statusFilter = $state('all');
	let dateFilter = $state('all');
	let serviceFilter = $state('all');
	let sortField = $state('');
	let sortDirection = $state<'asc' | 'desc' | null>(null);
	let currentPage = $state(1);
	let itemsPerPage = 10;

	// Dialog states
	let serviceDialogOpen = $state(false);
	let bookingDialogOpen = $state(false);
	let customerDialogOpen = $state(false);
	let editingService = $state<Service | null>(null);
	let editingBooking = $state<Booking | null>(null);
	let editingCustomer = $state<Customer | null>(null);

	// Form data
	let serviceForm = $state<ServiceForm>({
		name: '',
		name_ar: '',
		description: '',
		description_ar: '',
		price: 0,
		duration: 'PT30M',
		is_active: true
	});

	// Computed filtered data
	const filteredBookings = $derived(() => {
		let filtered = bookings;

		// Search filter
		if (searchQuery) {
			filtered = filtered.filter(booking => {
				const service = getServiceById(booking.service as number);
				const customer = getCustomerById(booking.customer as number);
				return (
					booking.booking_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
					service?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
					customer?.name.toLowerCase().includes(searchQuery.toLowerCase())
				);
			});
		}

		// Status filter
		if (statusFilter !== 'all') {
			filtered = filtered.filter(booking => booking.status === statusFilter);
		}

		// Date filter
		if (dateFilter !== 'all') {
			const today = new Date();
			const todayStr = today.toISOString().split('T')[0];
			
			filtered = filtered.filter(booking => {
				const bookingDate = new Date(booking.appointment_date);
				switch (dateFilter) {
					case 'today':
						return booking.appointment_date === todayStr;
					case 'week':
						const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
						return bookingDate >= today && bookingDate <= weekFromNow;
					case 'month':
						const monthFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
						return bookingDate >= today && bookingDate <= monthFromNow;
					default:
						return true;
				}
			});
		}

		// Service filter
		if (serviceFilter !== 'all') {
			filtered = filtered.filter(booking => booking.service.toString() === serviceFilter);
		}

		return filtered;
	});

	const filteredServices = $derived(() => {
		return services.filter(service => {
			if (searchQuery) {
				return service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
					   service.description?.toLowerCase().includes(searchQuery.toLowerCase());
			}
			return true;
		});
	});

	const filteredCustomers = $derived(() => {
		return customers.filter(customer => {
			if (searchQuery) {
				return customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
					   customer.phone_number.includes(searchQuery);
			}
			return true;
		});
	});

	// Pagination
	const paginatedBookings = $derived(() => {
		const start = (currentPage - 1) * itemsPerPage;
		const end = start + itemsPerPage;
		return filteredBookings.slice(start, end);
	});

	const totalPages = $derived(() => Math.ceil(filteredBookings.length / itemsPerPage));

	// Actions
	const handleSort = (field: string) => {
		if (sortField === field) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortField = field;
			sortDirection = 'asc';
		}
	};

	const openServiceDialog = (service?: Service) => {
		if (service) {
			editingService = service;
			serviceForm = {
				name: service.name,
				name_ar: service.name_ar || '',
				description: service.description || '',
				description_ar: service.description_ar || '',
				price: service.price,
				duration: service.duration,
				is_active: service.is_active
			};
		} else {
			editingService = null;
			serviceForm = {
				name: '',
				name_ar: '',
				description: '',
				description_ar: '',
				price: 0,
				duration: 'PT30M',
				is_active: true
			};
		}
		serviceDialogOpen = true;
	};

	const handleServiceSubmit = () => {
		console.log('Saving service:', serviceForm);
		// In real app, call API here
		serviceDialogOpen = false;
	};

	const deleteService = (id: number) => {
		if (confirm('هل أنت متأكد من حذف هذه الخدمة؟')) {
			console.log('Deleting service:', id);
			// In real app, call API here
		}
	};

	const updateBookingStatus = (booking: Booking, newStatus: string) => {
		console.log('Updating booking status:', booking.id, newStatus);
		// In real app, call API here
	};

	const exportData = (type: string) => {
		console.log('Exporting data:', type);
		// In real app, generate and download CSV/Excel
		const timestamp = new Date().toISOString().split('T')[0];
		const filename = `${type}_${timestamp}.csv`;
		
		// Create mock CSV data based on type
		let csvData = '';
		if (type === 'bookings') {
			csvData = 'رقم الحجز,العميل,الخدمة,التاريخ,الوقت,الحالة,السعر\n';
			filteredBookings.forEach(booking => {
				const service = getServiceById(booking.service as number);
				const customer = getCustomerById(booking.customer as number);
				csvData += `${booking.booking_id},${customer?.name || ''},${service?.name || ''},${booking.appointment_date},${booking.appointment_time},${booking.status},${booking.total_price}\n`;
			});
		} else if (type === 'customers') {
			csvData = 'الاسم,الهاتف,البريد الإلكتروني,تاريخ التسجيل,عدد الحجوزات\n';
			filteredCustomers.forEach(customer => {
				const customerBookings = bookings.filter(b => b.customer === customer.id);
				csvData += `${customer.name},${customer.phone_number},${customer.email || ''},${customer.created_at},${customerBookings.length}\n`;
			});
		}
		
		// Create and trigger download
		const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
		const link = document.createElement('a');
		link.href = URL.createObjectURL(blob);
		link.download = filename;
		link.click();
	};

	const openCustomerDialog = (customer: Customer) => {
		editingCustomer = customer;
		customerDialogOpen = true;
	};

	const formatDuration = (duration: string) => {
		const match = duration.match(/PT(\d+)M/);
		if (match) {
			return `${match[1]} دقيقة`;
		}
		return duration;
	};

	// Customer statistics computed values
	const getCustomerStats = (customerId: number) => {
		const customerBookings = bookings.filter(b => b.customer === customerId);
		const totalSpent = customerBookings.reduce((sum, b) => sum + b.total_price, 0);
		const completedBookings = customerBookings.filter(b => b.status === 'completed');
		return { customerBookings, totalSpent, completedBookings };
	};

	const statCards = [
		{
			title: 'إجمالي الحجوزات',
			value: dashboardStats.total_bookings,
			change: '+12%',
			icon: Calendar,
			color: 'text-blue-600'
		},
		{
			title: 'الحجوزات المعلقة',
			value: dashboardStats.pending_bookings,
			change: '-3%',
			icon: Clock,
			color: 'text-orange-600'
		},
		{
			title: 'إجمالي العملاء',
			value: dashboardStats.total_customers,
			change: '+8%',
			icon: Users,
			color: 'text-green-600'
		},
		{
			title: 'الإيرادات الشهرية',
			value: formatCurrency(dashboardStats.monthly_revenue),
			change: '+15%',
			icon: DollarSign,
			color: 'text-purple-600'
		}
	];

	const statusBadgeVariant = (status: string) => {
		switch (status) {
			case 'confirmed': return 'success';
			case 'pending': return 'warning';
			case 'completed': return 'default';
			case 'cancelled': return 'destructive';
			default: return 'secondary';
		}
	};

	const statusLabel = (status: string) => {
		switch (status) {
			case 'confirmed': return 'مؤكد';
			case 'pending': return 'معلق';
			case 'completed': return 'مكتمل';
			case 'cancelled': return 'ملغي';
			case 'no_show': return 'لم يحضر';
			default: return status;
		}
	};
</script>

<svelte:head>
	<title>لوحة التحكم المتقدمة - Wagtee</title>
	<meta name="description" content="لوحة تحكم متقدمة لإدارة الأعمال في منصة Wagtee" />
</svelte:head>

<div class="min-h-screen bg-background">
	<!-- Header -->
	<header class="border-b bg-card">
		<div class="container mx-auto px-4 py-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<h1 class="text-2xl font-bold text-primary">Wagtee</h1>
					<span class="text-sm text-muted-foreground">لوحة التحكم المتقدمة</span>
				</div>
				<div class="flex items-center space-x-4">
					<ModeToggle />
					<Button variant="outline" size="sm">
						<Settings class="w-4 h-4 mr-2" />
						الإعدادات
					</Button>
					<Button variant="ghost" size="sm">
						<LogOut class="w-4 h-4 mr-2" />
						تسجيل الخروج
					</Button>
				</div>
			</div>
		</div>
	</header>

	<div class="container mx-auto px-4 py-8">
		<!-- Welcome Section -->
		<div class="mb-8">
			<h2 class="text-3xl font-bold mb-2">مرحباً، أحمد! 👋</h2>
			<p class="text-muted-foreground">لوحة تحكم شاملة لإدارة عملك بكفاءة</p>
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
			{#each statCards as stat}
				<Card>
					<CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle class="text-sm font-medium">{stat.title}</CardTitle>
						{@const IconComponent = stat.icon}
						<IconComponent class="h-4 w-4 {stat.color}" />
					</CardHeader>
					<CardContent>
						<div class="text-2xl font-bold">{stat.value}</div>
						<p class="text-xs text-muted-foreground flex items-center">
							<TrendingUp class="h-3 w-3 mr-1" />
							{stat.change} من الشهر الماضي
						</p>
					</CardContent>
				</Card>
			{/each}
		</div>

		<!-- Main Content Tabs -->
		<Tabs bind:value={activeTab}>
			<TabsList class="grid w-full grid-cols-4">
				<TabsTrigger value="overview">نظرة عامة</TabsTrigger>
				<TabsTrigger value="bookings">الحجوزات</TabsTrigger>
				<TabsTrigger value="services">الخدمات</TabsTrigger>
				<TabsTrigger value="customers">العملاء</TabsTrigger>
			</TabsList>

			<!-- Overview Tab -->
			<TabsContent value="overview">
				<div class="grid lg:grid-cols-3 gap-8">
					<!-- Recent Activity -->
					<div class="lg:col-span-2">
						<Card>
							<CardHeader>
								<CardTitle>النشاط الأخير</CardTitle>
								<CardDescription>آخر الأنشطة في عملك</CardDescription>
							</CardHeader>
							<CardContent>
								<div class="space-y-4">
									{#each bookings.slice(0, 5) as booking}
										<div class="flex items-center justify-between p-4 border rounded-lg">
											<div class="flex-1">
												<div class="flex items-center gap-2 mb-1">
													<h4 class="font-medium">الحجز #{booking.booking_id}</h4>
													<Badge variant={statusBadgeVariant(booking.status)}>
														{statusLabel(booking.status)}
													</Badge>
												</div>
												<p class="text-sm text-muted-foreground">
													{formatDate(booking.appointment_date)} - {formatTime(booking.appointment_time)}
												</p>
											</div>
											<div class="text-right">
												<p class="font-medium">{formatCurrency(booking.total_price)}</p>
											</div>
										</div>
									{/each}
								</div>
							</CardContent>
						</Card>
					</div>

					<!-- Quick Stats -->
					<div class="space-y-6">
						<Card>
							<CardHeader>
								<CardTitle>إحصائيات سريعة</CardTitle>
							</CardHeader>
							<CardContent>
								<div class="space-y-4">
									<div class="flex justify-between">
										<span class="text-sm">معدل الإشغال</span>
										<span class="font-medium">78%</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm">متوسط قيمة الحجز</span>
										<span class="font-medium">{formatCurrency(45)}</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm">عملاء جدد</span>
										<span class="font-medium">12</span>
									</div>
									<div class="flex justify-between">
										<span class="text-sm">معدل الإلغاء</span>
										<span class="font-medium">5%</span>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card>
							<CardHeader>
								<CardTitle>الأداء</CardTitle>
							</CardHeader>
							<CardContent>
								<div class="flex items-center justify-center py-6">
									<div class="text-center">
										<div class="flex items-center justify-center mb-2">
											<Star class="w-8 h-8 fill-yellow-400 text-yellow-400" />
											<span class="text-3xl font-bold ml-2">{dashboardStats.average_rating}</span>
										</div>
										<p class="text-sm text-muted-foreground">متوسط التقييم</p>
									</div>
								</div>
							</CardContent>
						</Card>
					</div>
				</div>
			</TabsContent>

			<!-- Bookings Tab -->
			<TabsContent value="bookings">
				<Card>
					<CardHeader>
						<div class="flex items-center justify-between">
							<div>
								<CardTitle>إدارة الحجوزات</CardTitle>
								<CardDescription>عرض وإدارة جميع حجوزات العملاء</CardDescription>
							</div>
							<div class="flex items-center gap-2">
								<Button variant="outline" size="sm" onclick={() => exportData('bookings')}>
									<Download class="w-4 h-4 mr-2" />
									تصدير
								</Button>
							</div>
						</div>
					</CardHeader>
					<CardContent>
						<!-- Search and Filters -->
						<div class="space-y-4 mb-6">
							<div class="flex items-center gap-4">
								<div class="relative flex-1 max-w-sm">
									<Search class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
									<Input
										placeholder="البحث في الحجوزات..."
										bind:value={searchQuery}
										class="pl-10"
									/>
								</div>
								<Button variant="outline" size="sm">
									<Filter class="w-4 h-4 mr-2" />
									تصفية متقدمة
								</Button>
							</div>
							
							<div class="flex items-center gap-4">
								<select
									bind:value={statusFilter}
									class="px-3 py-2 border border-input rounded-md bg-background"
								>
									<option value="all">جميع الحالات</option>
									<option value="pending">معلق</option>
									<option value="confirmed">مؤكد</option>
									<option value="completed">مكتمل</option>
									<option value="cancelled">ملغي</option>
								</select>
								
								<select
									bind:value={dateFilter}
									class="px-3 py-2 border border-input rounded-md bg-background"
								>
									<option value="all">جميع التواريخ</option>
									<option value="today">اليوم</option>
									<option value="week">هذا الأسبوع</option>
									<option value="month">هذا الشهر</option>
								</select>
								
								<select
									bind:value={serviceFilter}
									class="px-3 py-2 border border-input rounded-md bg-background"
								>
									<option value="all">جميع الخدمات</option>
									{#each services as service}
										<option value={service.id.toString()}>{service.name}</option>
									{/each}
								</select>
							</div>
							
							{#if searchQuery || statusFilter !== 'all' || dateFilter !== 'all' || serviceFilter !== 'all'}
								<div class="flex items-center gap-2">
									<span class="text-sm text-muted-foreground">المرشحات النشطة:</span>
									{#if searchQuery}
										<Badge variant="secondary">بحث: {searchQuery}</Badge>
									{/if}
									{#if statusFilter !== 'all'}
										<Badge variant="secondary">الحالة: {statusFilter}</Badge>
									{/if}
									{#if dateFilter !== 'all'}
										<Badge variant="secondary">التاريخ: {dateFilter}</Badge>
									{/if}
									{#if serviceFilter !== 'all'}
										<Badge variant="secondary">الخدمة: {services.find(s => s.id.toString() === serviceFilter)?.name}</Badge>
									{/if}
									<Button 
										variant="ghost" 
										size="sm" 
										onclick={() => {
											searchQuery = '';
											statusFilter = 'all';
											dateFilter = 'all';
											serviceFilter = 'all';
										}}
									>
										مسح الكل
									</Button>
								</div>
							{/if}
						</div>

						<!-- Bookings Table -->
						<Table>
							<TableHeader>
								<TableRow>
									<TableHead sortable={true} sortDirection={sortField === 'booking_id' ? sortDirection : null} onSort={() => handleSort('booking_id')}>
										رقم الحجز
									</TableHead>
									<TableHead>العميل</TableHead>
									<TableHead>الخدمة</TableHead>
									<TableHead sortable={true} sortDirection={sortField === 'appointment_date' ? sortDirection : null} onSort={() => handleSort('appointment_date')}>
										التاريخ والوقت
									</TableHead>
									<TableHead>الحالة</TableHead>
									<TableHead sortable={true} sortDirection={sortField === 'total_price' ? sortDirection : null} onSort={() => handleSort('total_price')}>
										السعر
									</TableHead>
									<TableHead>الإجراءات</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{#each paginatedBookings as booking}
									{@const service = getServiceById(booking.service as number)}
									{@const customer = getCustomerById(booking.customer as number)}
									<TableRow>
										<TableCell class="font-medium">#{booking.booking_id}</TableCell>
										<TableCell>{customer?.name || 'غير معروف'}</TableCell>
										<TableCell>{service?.name || 'غير معروف'}</TableCell>
										<TableCell>
											<div class="text-sm">
												<div>{formatDate(booking.appointment_date)}</div>
												<div class="text-muted-foreground">{formatTime(booking.appointment_time)}</div>
											</div>
										</TableCell>
										<TableCell>
											<Badge variant={statusBadgeVariant(booking.status)}>
												{statusLabel(booking.status)}
											</Badge>
										</TableCell>
										<TableCell class="font-medium">{formatCurrency(booking.total_price)}</TableCell>
										<TableCell>
											<div class="flex items-center gap-2">
												{#if booking.status === 'pending'}
													<Button size="sm" onclick={() => updateBookingStatus(booking, 'confirmed')}>
														تأكيد
													</Button>
												{/if}
												<Button variant="outline" size="sm">
													<Eye class="w-4 h-4" />
												</Button>
											</div>
										</TableCell>
									</TableRow>
								{/each}
							</TableBody>
						</Table>

						<!-- Pagination -->
						<div class="flex items-center justify-between mt-4">
							<div class="text-sm text-muted-foreground">
								عرض {((currentPage - 1) * itemsPerPage) + 1} إلى {Math.min(currentPage * itemsPerPage, filteredBookings.length)} من {filteredBookings.length} حجز
							</div>
							<div class="flex items-center gap-2">
								<Button 
									variant="outline" 
									size="sm" 
									disabled={currentPage === 1}
									onclick={() => currentPage--}
								>
									<ChevronLeft class="w-4 h-4" />
								</Button>
								<span class="text-sm">{currentPage} من {totalPages}</span>
								<Button 
									variant="outline" 
									size="sm" 
									disabled={currentPage === totalPages}
									onclick={() => currentPage++}
								>
									<ChevronRight class="w-4 h-4" />
								</Button>
							</div>
						</div>
					</CardContent>
				</Card>
			</TabsContent>

			<!-- Services Tab -->
			<TabsContent value="services">
				<Card>
					<CardHeader>
						<div class="flex items-center justify-between">
							<div>
								<CardTitle>إدارة الخدمات</CardTitle>
								<CardDescription>إضافة وتعديل خدمات العمل</CardDescription>
							</div>
							<Dialog bind:open={serviceDialogOpen}>
								<DialogTrigger asChild>
									{#snippet children({ onClick })}
										<Button onclick={() => { onClick(); openServiceDialog(); }}>
											<Plus class="w-4 h-4 mr-2" />
											إضافة خدمة
										</Button>
									{/snippet}
								</DialogTrigger>
								<DialogContent class="max-w-md">
									<DialogHeader>
										<DialogTitle>{editingService ? 'تعديل الخدمة' : 'إضافة خدمة جديدة'}</DialogTitle>
										<DialogDescription>
											{editingService ? 'تعديل تفاصيل الخدمة' : 'أدخل تفاصيل الخدمة الجديدة'}
										</DialogDescription>
									</DialogHeader>
									<div class="space-y-4">
										<div class="grid grid-cols-2 gap-4">
											<div class="space-y-2">
												<Label for="name">اسم الخدمة</Label>
												<Input id="name" bind:value={serviceForm.name} placeholder="قص الشعر" />
											</div>
											<div class="space-y-2">
												<Label for="name_ar">الاسم بالعربية</Label>
												<Input id="name_ar" bind:value={serviceForm.name_ar} placeholder="قص الشعر" />
											</div>
										</div>
										<div class="space-y-2">
											<Label for="description">الوصف</Label>
											<Input id="description" bind:value={serviceForm.description} placeholder="وصف الخدمة" />
										</div>
										<div class="grid grid-cols-2 gap-4">
											<div class="space-y-2">
												<Label for="price">السعر (ريال)</Label>
												<Input id="price" type="number" bind:value={serviceForm.price} placeholder="25" />
											</div>
											<div class="space-y-2">
												<Label for="duration">المدة</Label>
												<select bind:value={serviceForm.duration} class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
													<option value="PT15M">15 دقيقة</option>
													<option value="PT30M">30 دقيقة</option>
													<option value="PT45M">45 دقيقة</option>
													<option value="PT60M">60 دقيقة</option>
													<option value="PT90M">90 دقيقة</option>
													<option value="PT120M">120 دقيقة</option>
												</select>
											</div>
										</div>
										<div class="flex items-center space-x-2">
											<input type="checkbox" bind:checked={serviceForm.is_active} id="is_active" />
											<Label for="is_active">خدمة نشطة</Label>
										</div>
									</div>
									<DialogFooter>
										<Button variant="outline" onclick={() => serviceDialogOpen = false}>إلغاء</Button>
										<Button onclick={handleServiceSubmit}>
											{editingService ? 'حفظ التغييرات' : 'إضافة الخدمة'}
										</Button>
									</DialogFooter>
								</DialogContent>
							</Dialog>
						</div>
					</CardHeader>
					<CardContent>
						<!-- Search -->
						<div class="relative max-w-sm mb-6">
							<Search class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
							<Input
								placeholder="البحث في الخدمات..."
								bind:value={searchQuery}
								class="pl-10"
							/>
						</div>

						<!-- Services Grid -->
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
							{#each filteredServices as service}
								<Card>
									<CardHeader>
										<div class="flex items-start justify-between">
											<div>
												<CardTitle class="text-lg">{service.name}</CardTitle>
												<CardDescription>{service.description}</CardDescription>
											</div>
											<Badge variant={service.is_active ? 'success' : 'secondary'}>
												{service.is_active ? 'نشط' : 'غير نشط'}
											</Badge>
										</div>
									</CardHeader>
									<CardContent>
										<div class="space-y-2">
											<div class="flex justify-between">
												<span class="text-sm text-muted-foreground">السعر:</span>
												<span class="font-medium">{formatCurrency(service.price)}</span>
											</div>
											<div class="flex justify-between">
												<span class="text-sm text-muted-foreground">المدة:</span>
												<span class="font-medium">{formatDuration(service.duration)}</span>
											</div>
										</div>
										<div class="flex items-center gap-2 mt-4">
											<Button variant="outline" size="sm" onclick={() => openServiceDialog(service)}>
												<Edit class="w-4 h-4 mr-1" />
												تعديل
											</Button>
											<Button variant="outline" size="sm" onclick={() => deleteService(service.id)}>
												<Trash2 class="w-4 h-4 mr-1" />
												حذف
											</Button>
										</div>
									</CardContent>
								</Card>
							{/each}
						</div>
					</CardContent>
				</Card>
			</TabsContent>

			<!-- Customers Tab -->
			<TabsContent value="customers">
				<Card>
					<CardHeader>
						<div class="flex items-center justify-between">
							<div>
								<CardTitle>إدارة العملاء</CardTitle>
								<CardDescription>عرض وإدارة قاعدة بيانات العملاء</CardDescription>
							</div>
							<Button variant="outline" size="sm" onclick={() => exportData('customers')}>
								<Download class="w-4 h-4 mr-2" />
								تصدير العملاء
							</Button>
						</div>
					</CardHeader>
					<CardContent>
						<!-- Search -->
						<div class="relative max-w-sm mb-6">
							<Search class="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
							<Input
								placeholder="البحث في العملاء..."
								bind:value={searchQuery}
								class="pl-10"
							/>
						</div>

						<!-- Customers Table -->
						<Table>
							<TableHeader>
								<TableRow>
									<TableHead>اسم العميل</TableHead>
									<TableHead>رقم الهاتف</TableHead>
									<TableHead>البريد الإلكتروني</TableHead>
									<TableHead>تاريخ التسجيل</TableHead>
									<TableHead>عدد الحجوزات</TableHead>
									<TableHead>الإجراءات</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{#each filteredCustomers as customer}
									{@const customerBookings = bookings.filter(b => b.customer === customer.id)}
									<TableRow>
										<TableCell class="font-medium">{customer.name}</TableCell>
										<TableCell>{customer.phone_number}</TableCell>
										<TableCell>{customer.email || '-'}</TableCell>
										<TableCell>{formatDate(customer.created_at)}</TableCell>
										<TableCell>{customerBookings.length}</TableCell>
										<TableCell>
											<Button variant="outline" size="sm" onclick={() => openCustomerDialog(customer)}>
												<Eye class="w-4 h-4 mr-1" />
												عرض التفاصيل
											</Button>
										</TableCell>
									</TableRow>
								{/each}
							</TableBody>
						</Table>
					</CardContent>
				</Card>
			</TabsContent>
		</Tabs>
	</div>
</div>

<!-- Customer Details Dialog -->
<Dialog bind:open={customerDialogOpen}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>تفاصيل العميل</DialogTitle>
			<DialogDescription>معلومات مفصلة عن العميل وحجوزاته</DialogDescription>
		</DialogHeader>
		{#if editingCustomer}
			{@const stats = getCustomerStats(editingCustomer.id)}
			<div class="space-y-6">
				<!-- Customer Info -->
				<div class="grid grid-cols-2 gap-4">
					<div class="space-y-2">
						<Label>اسم العميل</Label>
						<div class="p-2 border rounded bg-muted">{editingCustomer.name}</div>
					</div>
					<div class="space-y-2">
						<Label>رقم الهاتف</Label>
						<div class="p-2 border rounded bg-muted">{editingCustomer.phone_number}</div>
					</div>
					<div class="space-y-2">
						<Label>البريد الإلكتروني</Label>
						<div class="p-2 border rounded bg-muted">{editingCustomer.email || 'غير متوفر'}</div>
					</div>
					<div class="space-y-2">
						<Label>تاريخ التسجيل</Label>
						<div class="p-2 border rounded bg-muted">{formatDate(editingCustomer.created_at)}</div>
					</div>
				</div>

				<!-- Customer Statistics -->
				<div class="grid grid-cols-3 gap-4">
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold text-blue-600">{stats.customerBookings.length}</div>
							<p class="text-sm text-muted-foreground">إجمالي الحجوزات</p>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold text-green-600">{stats.completedBookings.length}</div>
							<p class="text-sm text-muted-foreground">حجوزات مكتملة</p>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold text-purple-600">{formatCurrency(stats.totalSpent)}</div>
							<p class="text-sm text-muted-foreground">إجمالي المبالغ</p>
						</CardContent>
					</Card>
				</div>

				<!-- Recent Bookings -->
				<div class="space-y-4">
					<h4 class="font-medium">آخر الحجوزات</h4>
					<div class="space-y-3 max-h-64 overflow-y-auto">
						{#each stats.customerBookings.slice(0, 5) as booking}
							{@const service = getServiceById(booking.service as number)}
							<div class="flex items-center justify-between p-3 border rounded">
								<div class="flex-1">
									<div class="flex items-center gap-2 mb-1">
										<span class="font-medium">#{booking.booking_id}</span>
										<Badge variant={statusBadgeVariant(booking.status)}>
											{statusLabel(booking.status)}
										</Badge>
									</div>
									<p class="text-sm text-muted-foreground">
										{service?.name} - {formatDate(booking.appointment_date)} {formatTime(booking.appointment_time)}
									</p>
								</div>
								<div class="text-right">
									<p class="font-medium">{formatCurrency(booking.total_price)}</p>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
		<DialogFooter>
			<Button variant="outline" onclick={() => customerDialogOpen = false}>إغلاق</Button>
		</DialogFooter>
	</DialogContent>
</Dialog>