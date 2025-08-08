<script lang="ts">
	import { onMount } from 'svelte';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Dialog, DialogContent, DialogHeader, DialogTitle } from '$lib/components/ui/dialog';
	import { Switch } from '$lib/components/ui/switch';
	
	import { DataTable } from '$lib/components/ui/data-table';
	import { EnhancedForm } from '$lib/components/ui/form';
	
	import type { DataTableColumn, DataTableAction, DataTableBulkAction } from '$lib/components/ui/data-table';
	import type { FormSchema } from '$lib/components/ui/form';
	
	import { servicesService } from '$lib/services/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	
	import {
		Sparkles,
		Plus,
		Filter,
		Download,
		RefreshCw,
		Edit,
		Trash2,
		Eye,
		Clock,
		DollarSign,
		ToggleLeft,
		ToggleRight,
		Grid,
		List,
		Search,
		FileText,
		BarChart3,
		TrendingUp,
		Users,
		Calendar
	} from '@lucide/svelte';

	// State
	let services = $state<any[]>([]);
	let isLoading = $state(true);
	let selectedServices = $state<any[]>([]);
	let currentTab = $state('list');
	let viewMode = $state<'list' | 'grid'>('list');
	let showNewServiceDialog = $state(false);
	let showEditServiceDialog = $state(false);
	let editingService = $state<any>(null);
	let showFiltersDialog = $state(false);
	
	// Pagination & Filtering
	let currentPage = $state(1);
	let pageSize = $state(25);
	let totalCount = $state(0);
	let searchQuery = $state('');
	let categoryFilter = $state('');
	let statusFilter = $state('');
	let priceFromFilter = $state('');
	let priceToFilter = $state('');
	let sortBy = $state('name');

	// Reactive
	const user = $derived(authStore.user);
	const totalPages = $derived(Math.ceil(totalCount / pageSize));
	
	// Service categories
	const serviceCategories = [
		{ value: 'barber', label: 'حلاقة' },
		{ value: 'salon', label: 'صالون' },
		{ value: 'beauty', label: 'مركز تجميل' },
		{ value: 'car_wash', label: 'غسيل سيارات' },
		{ value: 'cleaning', label: 'تنظيف' },
		{ value: 'gym', label: 'صالة رياضية' },
		{ value: 'photographer', label: 'مصور' },
		{ value: 'makeup', label: 'مكياج' },
		{ value: 'other', label: 'أخرى' }
	];

	// Form schemas
	const serviceFormSchema: FormSchema = {
		title: 'معلومات الخدمة',
		fields: [
			{
				name: 'name',
				type: 'text',
				label: 'اسم الخدمة',
				required: true,
				placeholder: 'أدخل اسم الخدمة'
			},
			{
				name: 'name_ar',
				type: 'text',
				label: 'الاسم بالعربية',
				placeholder: 'الاسم بالعربية (اختياري)'
			},
			{
				name: 'description',
				type: 'textarea',
				label: 'الوصف',
				placeholder: 'وصف الخدمة',
				rows: 3
			},
			{
				name: 'description_ar',
				type: 'textarea',
				label: 'الوصف بالعربية',
				placeholder: 'الوصف بالعربية (اختياري)',
				rows: 3
			},
			{
				name: 'category',
				type: 'select',
				label: 'التصنيف',
				required: true,
				options: serviceCategories
			},
			{
				name: 'price',
				type: 'number',
				label: 'السعر (ريال)',
				required: true,
				validation: { min: 0 },
				step: 0.01
			},
			{
				name: 'duration',
				type: 'number',
				label: 'المدة (دقيقة)',
				required: true,
				validation: { min: 1, max: 480 }
			},
			{
				name: 'is_active',
				type: 'checkbox',
				label: 'الخدمة نشطة',
				placeholder: 'تفعيل الخدمة للعملاء'
			}
		]
	};

	// Table configuration
	const columns: DataTableColumn[] = [
		{ key: 'name', title: 'اسم الخدمة', sortable: true, searchable: true },
		{ key: 'category', title: 'التصنيف', sortable: true },
		{ key: 'price', title: 'السعر', sortable: true, type: 'currency' },
		{ key: 'duration', title: 'المدة (دقيقة)', sortable: true, type: 'number' },
		{ key: 'bookings_count', title: 'عدد الحجوزات', sortable: true, type: 'number' },
		{ key: 'revenue', title: 'الإيرادات', sortable: true, type: 'currency' },
		{ key: 'is_active', title: 'الحالة', sortable: true, type: 'boolean' },
		{ key: 'created_at', title: 'تاريخ الإنشاء', sortable: true, type: 'date' }
	];

	const actions: DataTableAction[] = [
		{
			key: 'view',
			label: 'عرض',
			icon: Eye,
			variant: 'outline',
			onClick: handleViewService
		},
		{
			key: 'edit',
			label: 'تعديل',
			icon: Edit,
			variant: 'outline',
			onClick: handleEditService
		},
		{
			key: 'toggle',
			label: 'تبديل الحالة',
			icon: ToggleLeft,
			variant: 'outline',
			onClick: handleToggleService
		},
		{
			key: 'delete',
			label: 'حذف',
			icon: Trash2,
			variant: 'destructive',
			onClick: handleDeleteService,
			show: (service) => !service.is_active
		}
	];

	const bulkActions: DataTableBulkAction[] = [
		{
			key: 'activate',
			label: 'تفعيل المحدد',
			icon: ToggleRight,
			variant: 'default',
			onClick: handleBulkActivate
		},
		{
			key: 'deactivate',
			label: 'إلغاء تفعيل المحدد',
			icon: ToggleLeft,
			variant: 'outline',
			onClick: handleBulkDeactivate
		},
		{
			key: 'export',
			label: 'تصدير المحدد',
			icon: Download,
			variant: 'outline',
			onClick: handleBulkExport
		}
	];

	// Functions
	async function loadServices() {
		isLoading = true;
		try {
			const params = {
				page: currentPage,
				page_size: pageSize,
				search: searchQuery || undefined,
				category: categoryFilter || undefined,
				is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
				price_min: priceFromFilter ? parseFloat(priceFromFilter) : undefined,
				price_max: priceToFilter ? parseFloat(priceToFilter) : undefined,
				ordering: sortBy
			};

			const response = await servicesService.getAll(params);
			
			if (response.success) {
				services = response.data.results || [];
				totalCount = response.data.count || 0;
			}
		} catch (error) {
			console.error('Error loading services:', error);
		} finally {
			isLoading = false;
		}
	}

	function handleViewService(service: any) {
		// Navigate to service detail page
		console.log('View service:', service);
	}

	function handleEditService(service: any) {
		editingService = service;
		showEditServiceDialog = true;
	}

	async function handleToggleService(service: any) {
		try {
			const response = await servicesService.update(service.id, {
				is_active: !service.is_active
			});
			if (response.success) {
				await loadServices();
			}
		} catch (error) {
			console.error('Error toggling service:', error);
		}
	}

	async function handleDeleteService(service: any) {
		if (confirm('هل أنت متأكد من حذف هذه الخدمة؟')) {
			try {
				const response = await servicesService.delete(service.id);
				if (response.success) {
					await loadServices();
				}
			} catch (error) {
				console.error('Error deleting service:', error);
			}
		}
	}

	async function handleBulkActivate(selectedServices: any[]) {
		try {
			const serviceIds = selectedServices.map(s => s.id);
			const response = await servicesService.bulkUpdate(serviceIds, { is_active: true });
			if (response.success) {
				await loadServices();
			}
		} catch (error) {
			console.error('Error bulk activating services:', error);
		}
	}

	async function handleBulkDeactivate(selectedServices: any[]) {
		try {
			const serviceIds = selectedServices.map(s => s.id);
			const response = await servicesService.bulkUpdate(serviceIds, { is_active: false });
			if (response.success) {
				await loadServices();
			}
		} catch (error) {
			console.error('Error bulk deactivating services:', error);
		}
	}

	async function handleBulkExport(selectedServices: any[]) {
		// Implement export functionality
		console.log('Exporting services:', selectedServices);
	}

	async function handleNewService(formData: any) {
		try {
			const response = await servicesService.create(formData);
			if (response.success) {
				showNewServiceDialog = false;
				await loadServices();
			}
		} catch (error) {
			console.error('Error creating service:', error);
		}
	}

	async function handleUpdateService(formData: any) {
		try {
			const response = await servicesService.update(editingService.id, formData);
			if (response.success) {
				showEditServiceDialog = false;
				editingService = null;
				await loadServices();
			}
		} catch (error) {
			console.error('Error updating service:', error);
		}
	}

	function handleTabChange(tab: string) {
		currentTab = tab;
	}

	function getCategoryLabel(category: string) {
		const cat = serviceCategories.find(c => c.value === category);
		return cat ? cat.label : category;
	}

	// Watchers
	$effect(() => {
		if (currentPage || pageSize || searchQuery || categoryFilter || statusFilter || priceFromFilter || priceToFilter || sortBy) {
			loadServices();
		}
	});

	onMount(() => {
		loadServices();
	});
</script>

<svelte:head>
	<title>إدارة الخدمات - Wagtee</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-3xl font-bold">إدارة الخدمات</h1>
			<p class="text-muted-foreground">عرض وإدارة جميع الخدمات المقدمة</p>
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
			
			<Button variant="outline" onclick={() => loadServices()}>
				<RefreshCw class="h-4 w-4 mr-2" />
				تحديث
			</Button>
			
			<Button onclick={() => goto('/dashboard/services/new')}>
				<Plus class="h-4 w-4 mr-2" />
				خدمة جديدة
			</Button>
		</div>
	</div>

	<!-- Tabs -->
	<Tabs value={currentTab} onValueChange={handleTabChange}>
		<TabsList class="grid w-full grid-cols-3">
			<TabsTrigger value="list" class="flex items-center gap-2">
				<FileText class="h-4 w-4" />
				قائمة الخدمات
			</TabsTrigger>
			<TabsTrigger value="categories" class="flex items-center gap-2">
				<Grid class="h-4 w-4" />
				التصنيفات
			</TabsTrigger>
			<TabsTrigger value="analytics" class="flex items-center gap-2">
				<BarChart3 class="h-4 w-4" />
				الإحصائيات
			</TabsTrigger>
		</TabsList>

		<!-- Services List -->
		<TabsContent value="list" class="space-y-6">
			<!-- Quick Stats -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">إجمالي الخدمات</p>
								<p class="text-2xl font-bold">{totalCount}</p>
							</div>
							<Sparkles class="h-8 w-8 text-purple-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">خدمات نشطة</p>
								<p class="text-2xl font-bold text-green-600">
									{services.filter(s => s.is_active).length}
								</p>
							</div>
							<ToggleRight class="h-8 w-8 text-green-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">متوسط السعر</p>
								<p class="text-2xl font-bold">
									{services.length > 0 ? 
										Math.round(services.reduce((sum, s) => sum + s.price, 0) / services.length) + ' ر.س' : 
										'0 ر.س'
									}
								</p>
							</div>
							<DollarSign class="h-8 w-8 text-blue-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">متوسط المدة</p>
								<p class="text-2xl font-bold">
									{services.length > 0 ? 
										Math.round(services.reduce((sum, s) => sum + s.duration, 0) / services.length) + ' د' : 
										'0 د'
									}
								</p>
							</div>
							<Clock class="h-8 w-8 text-orange-600" />
						</div>
					</CardContent>
				</Card>
			</div>

			<!-- Services Data -->
			{#if viewMode === 'list'}
				<DataTable
					data={services}
					columns={columns}
					loading={isLoading}
					searchable={true}
					exportable={true}
					selectable={true}
					actions={actions}
					bulkActions={bulkActions}
					bind:selectedRows={selectedServices}
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
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{#each services as service}
						<Card class="hover:shadow-lg transition-shadow">
							<CardHeader class="pb-3">
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<CardTitle class="text-lg">{service.name}</CardTitle>
										<Badge variant="secondary" class="mt-1">
											{getCategoryLabel(service.category)}
										</Badge>
									</div>
									<Badge variant={service.is_active ? 'default' : 'secondary'}>
										{service.is_active ? 'نشط' : 'غير نشط'}
									</Badge>
								</div>
							</CardHeader>
							<CardContent class="space-y-3">
								{#if service.description}
									<p class="text-sm text-muted-foreground line-clamp-2">
										{service.description}
									</p>
								{/if}
								
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center">
										<DollarSign class="h-4 w-4 mr-1" />
										{service.price} ر.س
									</div>
									<div class="flex items-center">
										<Clock class="h-4 w-4 mr-1" />
										{service.duration} د
									</div>
								</div>

								{#if service.bookings_count !== undefined}
									<div class="flex items-center justify-between text-sm text-muted-foreground">
										<div class="flex items-center">
											<Calendar class="h-4 w-4 mr-1" />
											{service.bookings_count} حجز
										</div>
										{#if service.revenue}
											<div class="flex items-center">
												<TrendingUp class="h-4 w-4 mr-1" />
												{service.revenue} ر.س
											</div>
										{/if}
									</div>
								{/if}

								<div class="flex items-center gap-2 pt-2">
									<Button size="sm" variant="outline" onclick={() => handleEditService(service)}>
										<Edit class="h-3 w-3 mr-1" />
										تعديل
									</Button>
									<Button 
										size="sm" 
										variant="outline" 
										onclick={() => handleToggleService(service)}
									>
										{service.is_active ? 'إلغاء تفعيل' : 'تفعيل'}
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

		<!-- Categories View -->
		<TabsContent value="categories" class="space-y-6">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each serviceCategories as category}
					{@const categoryServices = services.filter(s => s.category === category.value)}
					<Card>
						<CardHeader>
							<CardTitle>{category.label}</CardTitle>
							<CardDescription>
								{categoryServices.length} خدمة
							</CardDescription>
						</CardHeader>
						<CardContent>
							{#if categoryServices.length > 0}
								<div class="space-y-2">
									<div class="flex items-center justify-between text-sm">
										<span>نشطة:</span>
										<span class="font-medium text-green-600">
											{categoryServices.filter(s => s.is_active).length}
										</span>
									</div>
									<div class="flex items-center justify-between text-sm">
										<span>متوسط السعر:</span>
										<span class="font-medium">
											{Math.round(categoryServices.reduce((sum, s) => sum + s.price, 0) / categoryServices.length)} ر.س
										</span>
									</div>
									<div class="flex items-center justify-between text-sm">
										<span>متوسط المدة:</span>
										<span class="font-medium">
											{Math.round(categoryServices.reduce((sum, s) => sum + s.duration, 0) / categoryServices.length)} د
										</span>
									</div>
								</div>
							{:else}
								<p class="text-sm text-muted-foreground">لا توجد خدمات في هذا التصنيف</p>
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
						<CardTitle>إحصائيات الخدمات</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">قريباً...</p>
					</CardContent>
				</Card>
			</div>
		</TabsContent>
	</Tabs>
</div>

<!-- New Service Dialog -->
<Dialog bind:open={showNewServiceDialog}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>إضافة خدمة جديدة</DialogTitle>
		</DialogHeader>
		
		<EnhancedForm
			schema={serviceFormSchema}
			on:submit={(e) => handleNewService(e.detail)}
			on:cancel={() => showNewServiceDialog = false}
			submitText="إنشاء الخدمة"
		/>
	</DialogContent>
</Dialog>

<!-- Edit Service Dialog -->
<Dialog bind:open={showEditServiceDialog}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>تعديل الخدمة</DialogTitle>
		</DialogHeader>
		
		{#if editingService}
			<EnhancedForm
				schema={serviceFormSchema}
				values={{
					name: editingService.name,
					name_ar: editingService.name_ar,
					description: editingService.description,
					description_ar: editingService.description_ar,
					category: editingService.category,
					price: editingService.price,
					duration: editingService.duration,
					is_active: editingService.is_active
				}}
				on:submit={(e) => handleUpdateService(e.detail)}
				on:cancel={() => {
					showEditServiceDialog = false;
					editingService = null;
				}}
				submitText="حفظ التغييرات"
			/>
		{/if}
	</DialogContent>
</Dialog>

<!-- Filters Dialog -->
<Dialog bind:open={showFiltersDialog}>
	<DialogContent class="max-w-md">
		<DialogHeader>
			<DialogTitle>فلترة الخدمات</DialogTitle>
		</DialogHeader>
		
		<div class="space-y-4">
			<div>
				<Label for="category-filter">التصنيف</Label>
				<select
					id="category-filter"
					bind:value={categoryFilter}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
				>
					<option value="">جميع التصنيفات</option>
					{#each serviceCategories as category}
						<option value={category.value}>{category.label}</option>
					{/each}
				</select>
			</div>

			<div>
				<Label for="status-filter">الحالة</Label>
				<select
					id="status-filter"
					bind:value={statusFilter}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
				>
					<option value="">جميع الحالات</option>
					<option value="active">نشط</option>
					<option value="inactive">غير نشط</option>
				</select>
			</div>

			<div class="grid grid-cols-2 gap-2">
				<div>
					<Label for="price-from">السعر من</Label>
					<Input
						id="price-from"
						type="number"
						placeholder="0"
						bind:value={priceFromFilter}
					/>
				</div>
				<div>
					<Label for="price-to">إلى</Label>
					<Input
						id="price-to"
						type="number"
						placeholder="1000"
						bind:value={priceToFilter}
					/>
				</div>
			</div>

			<div class="flex justify-end gap-2 pt-4 border-t">
				<Button variant="outline" onclick={() => {
					categoryFilter = '';
					statusFilter = '';
					priceFromFilter = '';
					priceToFilter = '';
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