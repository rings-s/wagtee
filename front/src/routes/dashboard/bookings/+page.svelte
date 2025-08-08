<script lang="ts">
	import { onMount } from 'svelte';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '$lib/components/ui/dialog';
	
	import { DataTable } from '$lib/components/ui/data-table';
	import { EnhancedForm } from '$lib/components/ui/form';
	import BookingCalendar from '$lib/components/booking/BookingCalendar.svelte';
	
	import type { DataTableColumn, DataTableAction, DataTableBulkAction } from '$lib/components/ui/data-table';
	import type { FormSchema } from '$lib/components/ui/form';
	
	import { bookingsService, servicesService, customersService } from '$lib/services/api';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	
	import {
		Calendar,
		Plus,
		Filter,
		Download,
		RefreshCw,
		Edit,
		Trash2,
		Eye,
		Clock,
		User,
		Phone,
		MapPin,
		DollarSign,
		CheckCircle,
		XCircle,
		AlertCircle,
		Search,
		FileText,
		Send,
		MoreHorizontal
	} from '@lucide/svelte';

	// State
	let bookings = $state<any[]>([]);
	let services = $state<any[]>([]);
	let customers = $state<any[]>([]);
	let isLoading = $state(true);
	let selectedBookings = $state<any[]>([]);
	let currentTab = $state('list');
	let showNewBookingDialog = $state(false);
	let showEditBookingDialog = $state(false);
	let editingBooking = $state<any>(null);
	let showFiltersDialog = $state(false);
	
	// Pagination & Filtering
	let currentPage = $state(1);
	let pageSize = $state(25);
	let totalCount = $state(0);
	let searchQuery = $state('');
	let statusFilter = $state('');
	let dateFromFilter = $state('');
	let dateToFilter = $state('');
	let serviceFilter = $state('');
	let customerFilter = $state('');
	let sortBy = $state('-appointment_date');

	// Reactive
	const user = $derived(authStore.user);
	const totalPages = $derived(Math.ceil(totalCount / pageSize));
	
	// Form schemas
	const newBookingSchema: FormSchema = {
		title: 'حجز جديد',
		fields: [
			{
				name: 'customer_name',
				type: 'text',
				label: 'اسم العميل',
				required: true,
				placeholder: 'أدخل اسم العميل'
			},
			{
				name: 'customer_phone',
				type: 'tel',
				label: 'رقم الهاتف',
				required: true,
				placeholder: '+966xxxxxxxxx'
			},
			{
				name: 'service_id',
				type: 'select',
				label: 'الخدمة',
				required: true,
				options: services.map(s => ({ value: s.id, label: s.name }))
			},
			{
				name: 'appointment_date',
				type: 'date',
				label: 'تاريخ الموعد',
				required: true
			},
			{
				name: 'appointment_time',
				type: 'time',
				label: 'وقت الموعد',
				required: true
			},
			{
				name: 'notes',
				type: 'textarea',
				label: 'ملاحظات',
				placeholder: 'ملاحظات إضافية (اختياري)',
				rows: 3
			}
		]
	};

	// Table configuration
	const columns: DataTableColumn[] = [
		{ key: 'id', title: 'رقم الحجز', sortable: true, width: '100px' },
		{ key: 'customer_name', title: 'العميل', sortable: true, searchable: true },
		{ key: 'customer_phone', title: 'الهاتف', sortable: true, searchable: true },
		{ key: 'service_name', title: 'الخدمة', sortable: true, searchable: true },
		{ key: 'appointment_date', title: 'التاريخ', sortable: true, type: 'date' },
		{ key: 'appointment_time', title: 'الوقت', sortable: true },
		{ key: 'status', title: 'الحالة', sortable: true, type: 'badge' },
		{ key: 'total_price', title: 'السعر', sortable: true, type: 'currency' },
		{ key: 'booking_method', title: 'طريقة الحجز', sortable: true }
	];

	const actions: DataTableAction[] = [
		{
			key: 'view',
			label: 'عرض',
			icon: Eye,
			variant: 'outline',
			onClick: handleViewBooking
		},
		{
			key: 'edit',
			label: 'تعديل',
			icon: Edit,
			variant: 'outline',
			onClick: handleEditBooking,
			show: (booking) => ['pending', 'confirmed'].includes(booking.status)
		},
		{
			key: 'confirm',
			label: 'تأكيد',
			icon: CheckCircle,
			variant: 'default',
			onClick: (booking) => handleStatusChange(booking, 'confirmed'),
			show: (booking) => booking.status === 'pending'
		},
		{
			key: 'complete',
			label: 'إكمال',
			icon: CheckCircle,
			variant: 'default',
			onClick: (booking) => handleStatusChange(booking, 'completed'),
			show: (booking) => booking.status === 'confirmed'
		},
		{
			key: 'cancel',
			label: 'إلغاء',
			icon: XCircle,
			variant: 'destructive',
			onClick: (booking) => handleStatusChange(booking, 'cancelled'),
			show: (booking) => ['pending', 'confirmed'].includes(booking.status)
		}
	];

	const bulkActions: DataTableBulkAction[] = [
		{
			key: 'confirm',
			label: 'تأكيد المحدد',
			icon: CheckCircle,
			variant: 'default',
			onClick: handleBulkConfirm,
			confirmMessage: 'هل أنت متأكد من تأكيد الحجوزات المحددة؟'
		},
		{
			key: 'cancel',
			label: 'إلغاء المحدد',
			icon: XCircle,
			variant: 'destructive',
			onClick: handleBulkCancel,
			confirmMessage: 'هل أنت متأكد من إلغاء الحجوزات المحددة؟'
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
	async function loadBookings() {
		isLoading = true;
		try {
			const params = {
				page: currentPage,
				page_size: pageSize,
				search: searchQuery || undefined,
				status: statusFilter || undefined,
				service: serviceFilter || undefined,
				customer_phone: customerFilter || undefined,
				appointment_date__gte: dateFromFilter || undefined,
				appointment_date__lte: dateToFilter || undefined,
				ordering: sortBy
			};

			const response = await bookingsService.getAll(params);
			
			if (response.success) {
				bookings = response.data.results || [];
				totalCount = response.data.count || 0;
			}
		} catch (error) {
			console.error('Error loading bookings:', error);
		} finally {
			isLoading = false;
		}
	}

	async function loadServices() {
		try {
			const response = await servicesService.getAll({ is_active: true });
			if (response.success) {
				services = response.data.results || [];
			}
		} catch (error) {
			console.error('Error loading services:', error);
		}
	}

	function handleViewBooking(booking: any) {
		goto(`/dashboard/bookings/${booking.id}`);
	}

	function handleEditBooking(booking: any) {
		editingBooking = booking;
		showEditBookingDialog = true;
	}

	async function handleStatusChange(booking: any, newStatus: string) {
		try {
			const response = await bookingsService.updateStatus(booking.id, newStatus);
			if (response.success) {
				await loadBookings();
			}
		} catch (error) {
			console.error('Error updating booking status:', error);
		}
	}

	async function handleBulkConfirm(selectedBookings: any[]) {
		try {
			const bookingIds = selectedBookings.map(b => b.id);
			const response = await bookingsService.bulkUpdate(bookingIds, { status: 'confirmed' });
			if (response.success) {
				await loadBookings();
			}
		} catch (error) {
			console.error('Error bulk confirming bookings:', error);
		}
	}

	async function handleBulkCancel(selectedBookings: any[]) {
		try {
			const bookingIds = selectedBookings.map(b => b.id);
			const response = await bookingsService.bulkUpdate(bookingIds, { status: 'cancelled' });
			if (response.success) {
				await loadBookings();
			}
		} catch (error) {
			console.error('Error bulk cancelling bookings:', error);
		}
	}

	async function handleBulkExport(selectedBookings: any[]) {
		// Implement export functionality
		console.log('Exporting bookings:', selectedBookings);
	}

	async function handleNewBooking(formData: any) {
		try {
			const response = await bookingsService.create({
				customer_name: formData.customer_name,
				customer_phone: formData.customer_phone,
				service: formData.service_id,
				appointment_date: formData.appointment_date,
				appointment_time: formData.appointment_time,
				notes: formData.notes,
				booking_method: 'admin'
			});

			if (response.success) {
				showNewBookingDialog = false;
				await loadBookings();
			}
		} catch (error) {
			console.error('Error creating booking:', error);
		}
	}

	function handleTabChange(tab: string) {
		currentTab = tab;
	}

	// Watchers
	$effect(() => {
		if (currentPage || pageSize || searchQuery || statusFilter || dateFromFilter || dateToFilter || serviceFilter || customerFilter || sortBy) {
			loadBookings();
		}
	});

	onMount(() => {
		loadServices();
		loadBookings();
	});
</script>

<svelte:head>
	<title>إدارة الحجوزات - Wagtee</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-3xl font-bold">إدارة الحجوزات</h1>
			<p class="text-muted-foreground">عرض وإدارة جميع الحجوزات في نظامك</p>
		</div>

		<div class="flex items-center gap-2">
			<Button variant="outline" onclick={() => showFiltersDialog = true}>
				<Filter class="h-4 w-4 mr-2" />
				فلترة
			</Button>
			
			<Button variant="outline" onclick={() => loadBookings()}>
				<RefreshCw class="h-4 w-4 mr-2" />
				تحديث
			</Button>
			
			<Button onclick={() => goto('/dashboard/bookings/new')}>
				<Plus class="h-4 w-4 mr-2" />
				حجز جديد
			</Button>
		</div>
	</div>

	<!-- Tabs -->
	<Tabs value={currentTab} onValueChange={handleTabChange}>
		<TabsList class="grid w-full grid-cols-3">
			<TabsTrigger value="list" class="flex items-center gap-2">
				<FileText class="h-4 w-4" />
				قائمة الحجوزات
			</TabsTrigger>
			<TabsTrigger value="calendar" class="flex items-center gap-2">
				<Calendar class="h-4 w-4" />
				التقويم
			</TabsTrigger>
			<TabsTrigger value="analytics" class="flex items-center gap-2">
				<DollarSign class="h-4 w-4" />
				الإحصائيات
			</TabsTrigger>
		</TabsList>

		<!-- List View -->
		<TabsContent value="list" class="space-y-6">
			<!-- Quick Stats -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">إجمالي الحجوزات</p>
								<p class="text-2xl font-bold">{totalCount}</p>
							</div>
							<Calendar class="h-8 w-8 text-blue-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">قيد الانتظار</p>
								<p class="text-2xl font-bold text-orange-600">
									{bookings.filter(b => b.status === 'pending').length}
								</p>
							</div>
							<Clock class="h-8 w-8 text-orange-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">مؤكدة</p>
								<p class="text-2xl font-bold text-green-600">
									{bookings.filter(b => b.status === 'confirmed').length}
								</p>
							</div>
							<CheckCircle class="h-8 w-8 text-green-600" />
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">مكتملة</p>
								<p class="text-2xl font-bold text-blue-600">
									{bookings.filter(b => b.status === 'completed').length}
								</p>
							</div>
							<CheckCircle class="h-8 w-8 text-blue-600" />
						</div>
					</CardContent>
				</Card>
			</div>

			<!-- Data Table -->
			<DataTable
				data={bookings}
				columns={columns}
				loading={isLoading}
				searchable={true}
				exportable={true}
				selectable={true}
				actions={actions}
				bulkActions={bulkActions}
				bind:selectedRows={selectedBookings}
				pagination={{
					currentPage,
					pageSize,
					totalCount,
					onPageChange: (page) => currentPage = page,
					onPageSizeChange: (size) => pageSize = size
				}}
			/>
		</TabsContent>

		<!-- Calendar View -->
		<TabsContent value="calendar" class="space-y-6">
			<BookingCalendar
				view="week"
				selectedDate={new Date()}
				on:bookingMoved={loadBookings}
				on:bookingUpdated={loadBookings}
			/>
		</TabsContent>

		<!-- Analytics View -->
		<TabsContent value="analytics" class="space-y-6">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<!-- Analytics cards would go here -->
				<Card>
					<CardHeader>
						<CardTitle>إحصائيات الحجوزات</CardTitle>
					</CardHeader>
					<CardContent>
						<p class="text-muted-foreground">قريباً...</p>
					</CardContent>
				</Card>
			</div>
		</TabsContent>
	</Tabs>
</div>

<!-- New Booking Dialog -->
<Dialog bind:open={showNewBookingDialog}>
	<DialogContent class="max-w-2xl">
		<DialogHeader>
			<DialogTitle>إضافة حجز جديد</DialogTitle>
		</DialogHeader>
		
		<EnhancedForm
			schema={newBookingSchema}
			on:submit={(e) => handleNewBooking(e.detail)}
			on:cancel={() => showNewBookingDialog = false}
			submitText="إنشاء الحجز"
		/>
	</DialogContent>
</Dialog>

<!-- Filters Dialog -->
<Dialog bind:open={showFiltersDialog}>
	<DialogContent class="max-w-md">
		<DialogHeader>
			<DialogTitle>فلترة الحجوزات</DialogTitle>
		</DialogHeader>
		
		<div class="space-y-4">
			<div>
				<Label for="status-filter">الحالة</Label>
				<select
					id="status-filter"
					bind:value={statusFilter}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
				>
					<option value="">جميع الحالات</option>
					<option value="pending">قيد الانتظار</option>
					<option value="confirmed">مؤكد</option>
					<option value="completed">مكتمل</option>
					<option value="cancelled">ملغي</option>
				</select>
			</div>

			<div>
				<Label for="service-filter">الخدمة</Label>
				<select
					id="service-filter"
					bind:value={serviceFilter}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
				>
					<option value="">جميع الخدمات</option>
					{#each services as service}
						<option value={service.id}>{service.name}</option>
					{/each}
				</select>
			</div>

			<div>
				<Label for="date-from">من تاريخ</Label>
				<Input
					id="date-from"
					type="date"
					bind:value={dateFromFilter}
				/>
			</div>

			<div>
				<Label for="date-to">إلى تاريخ</Label>
				<Input
					id="date-to"
					type="date"
					bind:value={dateToFilter}
				/>
			</div>

			<div class="flex justify-end gap-2 pt-4 border-t">
				<Button variant="outline" onclick={() => {
					statusFilter = '';
					serviceFilter = '';
					dateFromFilter = '';
					dateToFilter = '';
					customerFilter = '';
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