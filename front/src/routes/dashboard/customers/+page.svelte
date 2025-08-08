<script lang="ts">
	import { onMount } from 'svelte';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Dialog, DialogContent, DialogHeader, DialogTitle } from '$lib/components/ui/dialog';
	import { Avatar, AvatarFallback, AvatarImage } from '$lib/components/ui/avatar';
	
	import { DataTable } from '$lib/components/ui/data-table';
	import { EnhancedForm } from '$lib/components/ui/form';
	
	import type { DataTableColumn, DataTableAction, DataTableBulkAction } from '$lib/components/ui/data-table';
	import type { FormSchema } from '$lib/components/ui/form';
	
	import { customersService, bookingsService } from '$lib/services/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	
	import {
		Users,
		Plus,
		Filter,
		Download,
		RefreshCw,
		Edit,
		Trash2,
		Eye,
		Phone,
		Mail,
		MapPin,
		Calendar,
		DollarSign,
		TrendingUp,
		Star,
		Grid,
		List,
		Search,
		FileText,
		BarChart3,
		UserPlus,
		MessageCircle,
		Gift,
		Crown,
		Target
	} from '@lucide/svelte';

	// State
	let customers = $state<any[]>([]);
	let isLoading = $state(true);
	let selectedCustomers = $state<any[]>([]);
	let currentTab = $state('list');
	let viewMode = $state<'list' | 'grid'>('list');
	let showNewCustomerDialog = $state(false);
	let showEditCustomerDialog = $state(false);
	let showCustomerDetailDialog = $state(false);
	let editingCustomer = $state<any>(null);
	let selectedCustomer = $state<any>(null);
	let showFiltersDialog = $state(false);
	
	// Pagination & Filtering
	let currentPage = $state(1);
	let pageSize = $state(25);
	let totalCount = $state(0);
	let searchQuery = $state('');
	let segmentFilter = $state('');
	let registrationFromFilter = $state('');
	let registrationToFilter = $state('');
	let lastBookingFromFilter = $state('');
	let lastBookingToFilter = $state('');
	let sortBy = $state('-created_at');

	// Reactive
	const user = $derived(authStore.user);
	const totalPages = $derived(Math.ceil(totalCount / pageSize));
	
	// Customer segments
	const customerSegments = [
		{ value: 'new', label: 'عملاء جدد', description: 'أقل من 30 يوم' },
		{ value: 'regular', label: 'عملاء منتظمون', description: '2-5 حجوزات' },
		{ value: 'vip', label: 'عملاء VIP', description: 'أكثر من 5 حجوزات' },
		{ value: 'inactive', label: 'عملاء غير نشطين', description: 'لم يحجزوا منذ 60 يوم' }
	];

	// Form schemas
	const customerFormSchema: FormSchema = {
		title: 'معلومات العميل',
		fields: [
			{
				name: 'name',
				type: 'text',
				label: 'الاسم الكامل',
				required: true,
				placeholder: 'أدخل الاسم الكامل'
			},
			{
				name: 'phone_number',
				type: 'tel',
				label: 'رقم الهاتف',
				required: true,
				placeholder: '+966xxxxxxxxx'
			},
			{
				name: 'email',
				type: 'email',
				label: 'البريد الإلكتروني',
				placeholder: 'البريد الإلكتروني (اختياري)'
			},
			{
				name: 'date_of_birth',
				type: 'date',
				label: 'تاريخ الميلاد',
				placeholder: 'تاريخ الميلاد (اختياري)'
			},
			{
				name: 'gender',
				type: 'select',
				label: 'الجنس',
				options: [
					{ value: '', label: 'غير محدد' },
					{ value: 'male', label: 'ذكر' },
					{ value: 'female', label: 'أنثى' }
				]
			},
			{
				name: 'address',
				type: 'textarea',
				label: 'العنوان',
				placeholder: 'العنوان (اختياري)',
				rows: 2
			},
			{
				name: 'notes',
				type: 'textarea',
				label: 'ملاحظات',
				placeholder: 'ملاحظات عن العميل (اختياري)',
				rows: 3
			}
		]
	};

	// Table configuration
	const columns: DataTableColumn[] = [
		{ key: 'name', title: 'الاسم', sortable: true, searchable: true },
		{ key: 'phone_number', title: 'رقم الهاتف', sortable: true, searchable: true },
		{ key: 'email', title: 'البريد الإلكتروني', sortable: true, searchable: true },
		{ key: 'total_bookings', title: 'عدد الحجوزات', sortable: true, type: 'number' },
		{ key: 'total_spent', title: 'إجمالي الإنفاق', sortable: true, type: 'currency' },
		{ key: 'last_booking_date', title: 'آخر حجز', sortable: true, type: 'date' },
		{ key: 'customer_segment', title: 'الفئة', sortable: true, type: 'badge' },
		{ key: 'created_at', title: 'تاريخ التسجيل', sortable: true, type: 'date' }
	];

	const actions: DataTableAction[] = [
		{
			key: 'view',
			label: 'عرض التفاصيل',
			icon: Eye,
			variant: 'outline',
			onClick: handleViewCustomer
		},
		{
			key: 'edit',
			label: 'تعديل',
			icon: Edit,
			variant: 'outline',
			onClick: handleEditCustomer
		},
		{
			key: 'book',
			label: 'حجز جديد',
			icon: Calendar,
			variant: 'default',
			onClick: handleNewBooking
		},
		{
			key: 'message',
			label: 'إرسال رسالة',
			icon: MessageCircle,
			variant: 'outline',
			onClick: handleSendMessage
		}
	];

	const bulkActions: DataTableBulkAction[] = [
		{
			key: 'export',
			label: 'تصدير المحدد',
			icon: Download,
			variant: 'outline',
			onClick: handleBulkExport
		},
		{
			key: 'message',
			label: 'إرسال رسالة جماعية',
			icon: MessageCircle,
			variant: 'default',
			onClick: handleBulkMessage
		},
		{
			key: 'segment',
			label: 'تصنيف المحدد',
			icon: Target,
			variant: 'outline',
			onClick: handleBulkSegment
		}
	];

	// Functions
	async function loadCustomers() {
		isLoading = true;
		try {
			const params = {
				page: currentPage,
				page_size: pageSize,
				search: searchQuery || undefined,
				segment: segmentFilter || undefined,
				created_at__gte: registrationFromFilter || undefined,
				created_at__lte: registrationToFilter || undefined,
				last_booking_date__gte: lastBookingFromFilter || undefined,
				last_booking_date__lte: lastBookingToFilter || undefined,
				ordering: sortBy
			};

			const response = await customersService.getAll(params);
			
			if (response.success) {
				customers = response.data.results || [];
				totalCount = response.data.count || 0;
			}
		} catch (error) {
			console.error('Error loading customers:', error);
		} finally {
			isLoading = false;
		}
	}

	function handleViewCustomer(customer: any) {
		selectedCustomer = customer;
		showCustomerDetailDialog = true;
	}

	function handleEditCustomer(customer: any) {
		editingCustomer = customer;
		showEditCustomerDialog = true;
	}

	function handleNewBooking(customer: any) {
		// Navigate to new booking page with customer pre-selected
		window.location.href = `/dashboard/bookings/new?customer=${customer.id}`;
	}

	function handleSendMessage(customer: any) {
		// Open message dialog
		console.log('Send message to:', customer);
	}

	async function handleBulkExport(selectedCustomers: any[]) {
		// Implement export functionality
		console.log('Exporting customers:', selectedCustomers);
	}

	async function handleBulkMessage(selectedCustomers: any[]) {
		// Implement bulk messaging
		console.log('Send bulk message to:', selectedCustomers);
	}

	async function handleBulkSegment(selectedCustomers: any[]) {
		// Implement bulk segmentation
		console.log('Segment customers:', selectedCustomers);
	}

	async function handleNewCustomer(formData: any) {
		try {
			const response = await customersService.create(formData);
			if (response.success) {
				showNewCustomerDialog = false;
				await loadCustomers();
			}
		} catch (error) {
			console.error('Error creating customer:', error);
		}
	}

	async function handleUpdateCustomer(formData: any) {
		try {
			const response = await customersService.update(editingCustomer.id, formData);
			if (response.success) {
				showEditCustomerDialog = false;
				editingCustomer = null;
				await loadCustomers();
			}
		} catch (error) {
			console.error('Error updating customer:', error);
		}
	}

	function handleTabChange(tab: string) {
		currentTab = tab;
	}

	function getSegmentInfo(segment: string) {
		const seg = customerSegments.find(s => s.value === segment);
		return seg || { value: segment, label: segment, description: '' };
	}

	function getSegmentColor(segment: string) {
		const colors = {
			new: 'bg-blue-100 text-blue-800',
			regular: 'bg-green-100 text-green-800',
			vip: 'bg-purple-100 text-purple-800',
			inactive: 'bg-gray-100 text-gray-800'
		};
		return colors[segment] || 'bg-gray-100 text-gray-800';
	}

	function getInitials(name: string) {
		return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
	}

	// Watchers
	$effect(() => {
		if (currentPage || pageSize || searchQuery || segmentFilter || registrationFromFilter || registrationToFilter || lastBookingFromFilter || lastBookingToFilter || sortBy) {
			loadCustomers();
		}
	});

	onMount(() => {
		loadCustomers();
	});
</script>

<svelte:head>
	<title>إدارة العملاء - Wagtee</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-3xl font-bold">إدارة العملاء</h1>
			<p class="text-muted-foreground">عرض وإدارة قاعدة عملائك</p>
		</div>

		<div class="flex items-center gap-2">
			<Button variant="outline" onclick={() => showFiltersDialog = true}>
				<Filter class="h-4 w-4 mr-2" />
				فلترة
			</Button>
			
			<div class="flex border rounded-lg">
				<Button 
					variant={viewMode === 'list' ? 'default' : 'ghost'} 
					size="sm"
					onclick={() => viewMode = 'list'}
				>
					<List class="h-4 w-4" />
				</Button>
				<Button 
					variant={viewMode === 'grid' ? 'default' : 'ghost'} 
					size="sm"
					onclick={() => viewMode = 'grid'}
				>
					<Grid class="h-4 w-4" />
				</Button>
			</div>
			
			<Button variant="outline" onclick={() => loadCustomers()}>
				<RefreshCw class="h-4 w-4 mr-2" />
				تحديث
			</Button>
			
			<Button onclick={() => goto('/dashboard/customers/new')}>
				<Plus class="h-4 w-4 mr-2" />
				عميل جديد
			</Button>
		</div>
	</div>

	<!-- Tabs -->
	<Tabs value={currentTab} onValueChange={handleTabChange}>
		<TabsList class="grid w-full grid-cols-3">
			<TabsTrigger value="list" class="flex items-center gap-2">
				<FileText class="h-4 w-4" />
				قائمة العملاء
			</TabsTrigger>
			<TabsTrigger value="segments" class="flex items-center gap-2">
				<Target class="h-4 w-4" />
				الفئات
			</TabsTrigger>
			<TabsTrigger value="analytics" class="flex items-center gap-2">
				<BarChart3 class="h-4 w-4" />
				الإحصائيات
			</TabsTrigger>
		</TabsList>

		<!-- Customers List -->
		<TabsContent value="list" class="space-y-6">
			<!-- Quick Stats -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">إجمالي العملاء</p>
								<p class="text-2xl font-bold">{totalCount}</p>
							</div>
							<Users class="h-8 w-8 text-blue-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">عملاء VIP</p>
								<p class="text-2xl font-bold text-purple-600">
									{customers.filter(c => c.customer_segment === 'vip').length}
								</p>
							</div>
							<Crown class="h-8 w-8 text-purple-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">عملاء جدد</p>
								<p class="text-2xl font-bold text-green-600">
									{customers.filter(c => c.customer_segment === 'new').length}
								</p>
							</div>
							<UserPlus class="h-8 w-8 text-green-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">متوسط الإنفاق</p>
								<p class="text-2xl font-bold">
									{customers.length > 0 ? 
										Math.round(customers.reduce((sum, c) => sum + (c.total_spent || 0), 0) / customers.length) + ' ر.س' : 
										'0 ر.س'
									}
								</p>
							</div>
							<DollarSign class="h-8 w-8 text-orange-600" />
						</div>
					</CardContent>
				</Card>
			</div>

			<!-- Customers Data -->
			{#if viewMode === 'list'}
				<DataTable
					data={customers}
					columns={columns}
					loading={isLoading}
					searchable={true}
					exportable={true}
					selectable={true}
					actions={actions}
					bulkActions={bulkActions}
					bind:selectedRows={selectedCustomers}
					pagination={{
						currentPage,
						pageSize,
						totalCount,
						onPageChange: (page) => currentPage = page,
						onPageSizeChange: (size) => pageSize = size
					}}
				/>
			{:else}
				<!-- Grid View -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each customers as customer}
						<Card class="hover:shadow-lg transition-shadow">
							<CardHeader class="pb-3">
								<div class="flex items-start gap-3">
									<Avatar 
										size="default" 
										variant={customer.customer_segment === 'vip' ? 'vip' : customer.customer_segment === 'regular' ? 'premium' : 'default'}
										status={customer.last_booking_date && new Date(customer.last_booking_date) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) ? 'online' : 'offline'}
										clickable={true}
									>
										<AvatarImage 
											src={customer.avatar} 
											alt={customer.name}
											onError={() => console.log(`Failed to load avatar for ${customer.name}`)}
										/>
										<AvatarFallback 
											name={customer.name}
											email={customer.email}
											userId={customer.id}
											variant={customer.customer_segment === 'vip' ? 'vip' : customer.customer_segment === 'regular' ? 'premium' : 'default'}
											type="pattern"
											showIcon={customer.customer_segment === 'vip'}
										/>
									</Avatar>
									<div class="flex-1 min-w-0">
										<CardTitle class="text-lg truncate">{customer.name}</CardTitle>
										<div class="flex items-center gap-2 mt-1">
											<Badge class={getSegmentColor(customer.customer_segment)}>
												{getSegmentInfo(customer.customer_segment).label}
											</Badge>
										</div>
									</div>
								</div>
							</CardHeader>
							<CardContent class="space-y-3">
								<div class="space-y-2 text-sm">
									<div class="flex items-center">
										<Phone class="h-4 w-4 mr-2 text-muted-foreground" />
										{customer.phone_number}
									</div>
									{#if customer.email}
										<div class="flex items-center">
											<Mail class="h-4 w-4 mr-2 text-muted-foreground" />
											<span class="truncate">{customer.email}</span>
										</div>
									{/if}
								</div>

								<div class="grid grid-cols-2 gap-4 text-sm">
									<div class="text-center p-2 bg-muted/20 rounded">
										<div class="font-bold text-lg">{customer.total_bookings || 0}</div>
										<div class="text-muted-foreground">حجز</div>
									</div>
									<div class="text-center p-2 bg-muted/20 rounded">
										<div class="font-bold text-lg">
											{customer.total_spent ? customer.total_spent + ' ر.س' : '0 ر.س'}
										</div>
										<div class="text-muted-foreground">إنفاق</div>
									</div>
								</div>

								{#if customer.last_booking_date}
									<div class="flex items-center text-sm text-muted-foreground">
										<Calendar class="h-4 w-4 mr-2" />
										آخر حجز: {new Date(customer.last_booking_date).toLocaleDateString('ar-SA')}
									</div>
								{/if}

								<div class="flex items-center gap-2 pt-2">
									<Button size="sm" variant="outline" onclick={() => handleViewCustomer(customer)}>
										<Eye class="h-3 w-3 mr-1" />
										عرض
									</Button>
									<Button size="sm" onclick={() => handleNewBooking(customer)}>
										<Calendar class="h-3 w-3 mr-1" />
										حجز
									</Button>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>

				<!-- Grid Pagination -->
				{#if totalPages > 1}
					<div class="flex items-center justify-center gap-2 mt-6">
						<Button 
							variant="outline" 
							size="sm" 
							disabled={currentPage === 1}
							onclick={() => currentPage = currentPage - 1}
						>
							السابق
						</Button>
						
						<span class="text-sm text-muted-foreground">
							صفحة {currentPage} من {totalPages}
						</span>
						
						<Button 
							variant="outline" 
							size="sm" 
							disabled={currentPage === totalPages}
							onclick={() => currentPage = currentPage + 1}
						>
							التالي
						</Button>
					</div>
				{/if}
			{/if}
		</TabsContent>

		<!-- Segments View -->
		<TabsContent value="segments" class="space-y-6">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				{#each customerSegments as segment}
					{@const segmentCustomers = customers.filter(c => c.customer_segment === segment.value)}
					<Card>
						<CardHeader>
							<div class="flex items-center justify-between">
								<div>
									<CardTitle>{segment.label}</CardTitle>
									<CardDescription>{segment.description}</CardDescription>
								</div>
								<Badge class={getSegmentColor(segment.value)}>
									{segmentCustomers.length}
								</Badge>
							</div>
						</CardHeader>
						<CardContent>
							{#if segmentCustomers.length > 0}
								<div class="space-y-2">
									<div class="flex items-center justify-between text-sm">
										<span>متوسط الحجوزات:</span>
										<span class="font-medium">
											{Math.round(segmentCustomers.reduce((sum, c) => sum + (c.total_bookings || 0), 0) / segmentCustomers.length)}
										</span>
									</div>
									<div class="flex items-center justify-between text-sm">
										<span>متوسط الإنفاق:</span>
										<span class="font-medium">
											{Math.round(segmentCustomers.reduce((sum, c) => sum + (c.total_spent || 0), 0) / segmentCustomers.length)} ر.س
										</span>
									</div>
									<div class="flex items-center justify-between text-sm">
										<span>النسبة:</span>
										<span class="font-medium">
											{Math.round((segmentCustomers.length / customers.length) * 100)}%
										</span>
									</div>
								</div>
								
								<Button 
									variant="outline" 
									size="sm" 
									class="w-full mt-4"
									onclick={() => {
										segmentFilter = segment.value;
										currentTab = 'list';
									}}
								>
									عرض العملاء
								</Button>
							{:else}
								<p class="text-sm text-muted-foreground">لا توجد عملاء في هذه الفئة</p>
							{/if}
						</CardContent>
					</Card>
				{/each}
			</div>
		</TabsContent>

		<!-- Analytics View -->
		<TabsContent value="analytics" class="space-y-6">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<Card>
					<CardHeader>
						<CardTitle>إحصائيات العملاء</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">قريباً...</p>
					</CardContent>
				</Card>
			</div>
		</TabsContent>
	</Tabs>
</div>

<!-- New Customer Dialog -->
<Dialog bind:open={showNewCustomerDialog}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>إضافة عميل جديد</DialogTitle>
		</DialogHeader>
		
		<EnhancedForm
			schema={customerFormSchema}
			on:submit={(e) => handleNewCustomer(e.detail)}
			on:cancel={() => showNewCustomerDialog = false}
			submitText="إضافة العميل"
		/>
	</DialogContent>
</Dialog>

<!-- Edit Customer Dialog -->
<Dialog bind:open={showEditCustomerDialog}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>تعديل بيانات العميل</DialogTitle>
		</DialogHeader>
		
		{#if editingCustomer}
			<EnhancedForm
				schema={customerFormSchema}
				values={{
					name: editingCustomer.name,
					phone_number: editingCustomer.phone_number,
					email: editingCustomer.email,
					date_of_birth: editingCustomer.date_of_birth,
					gender: editingCustomer.gender,
					address: editingCustomer.address,
					notes: editingCustomer.notes
				}}
				on:submit={(e) => handleUpdateCustomer(e.detail)}
				on:cancel={() => {
					showEditCustomerDialog = false;
					editingCustomer = null;
				}}
				submitText="حفظ التغييرات"
			/>
		{/if}
	</DialogContent>
</Dialog>

<!-- Customer Detail Dialog -->
<Dialog bind:open={showCustomerDetailDialog}>
	<DialogContent class="max-w-3xl">
		<DialogHeader>
			<DialogTitle>تفاصيل العميل</DialogTitle>
		</DialogHeader>
		
		{#if selectedCustomer}
			<div class="space-y-6">
				<!-- Customer Header -->
				<div class="flex items-start gap-4">
					<Avatar 
						size="xl" 
						variant={selectedCustomer.customer_segment === 'vip' ? 'vip' : selectedCustomer.customer_segment === 'regular' ? 'premium' : 'default'}
						status={selectedCustomer.last_booking_date && new Date(selectedCustomer.last_booking_date) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) ? 'online' : 'offline'}
						clickable={true}
					>
						<AvatarImage 
							src={selectedCustomer.avatar} 
							alt={selectedCustomer.name}
						/>
						<AvatarFallback 
							name={selectedCustomer.name}
							email={selectedCustomer.email}
							userId={selectedCustomer.id}
							variant={selectedCustomer.customer_segment === 'vip' ? 'vip' : selectedCustomer.customer_segment === 'regular' ? 'premium' : 'default'}
							type="gradient"
							showIcon={selectedCustomer.customer_segment === 'vip'}
						/>
					</Avatar>
					<div class="flex-1">
						<h3 class="text-xl font-bold">{selectedCustomer.name}</h3>
						<div class="flex items-center gap-2 mt-2">
							<Badge class={getSegmentColor(selectedCustomer.customer_segment)}>
								{getSegmentInfo(selectedCustomer.customer_segment).label}
							</Badge>
						</div>
						<div class="grid grid-cols-2 gap-4 mt-4 text-sm">
							<div>
								<div class="font-medium">رقم الهاتف</div>
								<div class="text-muted-foreground">{selectedCustomer.phone_number}</div>
							</div>
							{#if selectedCustomer.email}
								<div>
									<div class="font-medium">البريد الإلكتروني</div>
									<div class="text-muted-foreground">{selectedCustomer.email}</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Customer Stats -->
				<div class="grid grid-cols-3 gap-4">
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">{selectedCustomer.total_bookings || 0}</div>
							<div class="text-sm text-muted-foreground">إجمالي الحجوزات</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">
								{selectedCustomer.total_spent ? selectedCustomer.total_spent + ' ر.س' : '0 ر.س'}
							</div>
							<div class="text-sm text-muted-foreground">إجمالي الإنفاق</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">
								{selectedCustomer.avg_rating || '-'}
							</div>
							<div class="text-sm text-muted-foreground">متوسط التقييم</div>
						</CardContent>
					</Card>
				</div>

				<!-- Additional Information -->
				<div class="space-y-4">
					{#if selectedCustomer.last_booking_date}
						<div>
							<Label class="font-medium">آخر حجز</Label>
							<p class="text-sm text-muted-foreground">
								{new Date(selectedCustomer.last_booking_date).toLocaleDateString('ar-SA')}
							</p>
						</div>
					{/if}
					
					{#if selectedCustomer.address}
						<div>
							<Label class="font-medium">العنوان</Label>
							<p class="text-sm text-muted-foreground">{selectedCustomer.address}</p>
						</div>
					{/if}
					
					{#if selectedCustomer.notes}
						<div>
							<Label class="font-medium">ملاحظات</Label>
							<p class="text-sm text-muted-foreground">{selectedCustomer.notes}</p>
						</div>
					{/if}
				</div>

				<!-- Actions -->
				<div class="flex justify-end gap-2 pt-4 border-t">
					<Button variant="outline" onclick={() => handleEditCustomer(selectedCustomer)}>
						<Edit class="h-4 w-4 mr-2" />
						تعديل
					</Button>
					<Button onclick={() => handleNewBooking(selectedCustomer)}>
						<Calendar class="h-4 w-4 mr-2" />
						حجز جديد
					</Button>
				</div>
			</div>
		{/if}
	</DialogContent>
</Dialog>

<!-- Filters Dialog -->
<Dialog bind:open={showFiltersDialog}>
	<DialogContent class="max-w-md">
		<DialogHeader>
			<DialogTitle>فلترة العملاء</DialogTitle>
		</DialogHeader>
		
		<div class="space-y-4">
			<div>
				<Label for="segment-filter">الفئة</Label>
				<select
					id="segment-filter"
					bind:value={segmentFilter}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
				>
					<option value="">جميع الفئات</option>
					{#each customerSegments as segment}
						<option value={segment.value}>{segment.label}</option>
					{/each}
				</select>
			</div>

			<div>
				<Label>تاريخ التسجيل</Label>
				<div class="grid grid-cols-2 gap-2">
					<Input
						type="date"
						placeholder="من"
						bind:value={registrationFromFilter}
					/>
					<Input
						type="date"
						placeholder="إلى"
						bind:value={registrationToFilter}
					/>
				</div>
			</div>

			<div>
				<Label>آخر حجز</Label>
				<div class="grid grid-cols-2 gap-2">
					<Input
						type="date"
						placeholder="من"
						bind:value={lastBookingFromFilter}
					/>
					<Input
						type="date"
						placeholder="إلى"
						bind:value={lastBookingToFilter}
					/>
				</div>
			</div>

			<div class="flex justify-end gap-2 pt-4 border-t">
				<Button variant="outline" onclick={() => {
					segmentFilter = '';
					registrationFromFilter = '';
					registrationToFilter = '';
					lastBookingFromFilter = '';
					lastBookingToFilter = '';
				}}>
					مسح الفلاتر
				</Button>
				<Button onclick={() => showFiltersDialog = false}>
					تطبيق
				</Button>
			</div>
		</div>
	</DialogContent>
</Dialog>