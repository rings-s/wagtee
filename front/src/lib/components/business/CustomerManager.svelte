<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import type { Customer, CustomerForm } from '$lib/types/index.js';
	import { api } from '$lib/services/api-client.js';
	import { authStore } from '$lib/stores/auth.svelte.js';
	
	// UI Components
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '$lib/components/ui/select';
	import { Dialog, DialogContent, DialogHeader, DialogTitle } from '$lib/components/ui/dialog';
	import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '$lib/components/ui/sheet';
	import { Avatar, AvatarFallback, AvatarImage } from '$lib/components/ui/avatar';
	import { toast } from 'svelte-sonner';
	
	// Icons
	import {
		Users,
		Plus,
		Edit,
		Trash2,
		Eye,
		Search,
		Filter,
		Grid,
		List,
		Phone,
		Mail,
		MapPin,
		Calendar,
		DollarSign,
		TrendingUp,
		Star,
		UserPlus,
		MessageCircle,
		Gift,
		Crown,
		Target,
		RefreshCw,
		Download,
		MoreHorizontal
	} from 'lucide-svelte';

	interface Props {
		businessId?: number;
		view?: 'grid' | 'list';
		showHeader?: boolean;
	}

	let { businessId, view = 'grid', showHeader = true }: Props = $props();

	const dispatch = createEventDispatcher();

	// State management using Svelte 5 runes
	let customers = $state<Customer[]>([]);
	let isLoading = $state(false);
	let searchQuery = $state('');
	let segmentFilter = $state<string>('');
	let statusFilter = $state<string>('');
	let sortBy = $state<'name' | 'created_at' | 'last_booking_date' | 'total_spent'>('name');
	let sortOrder = $state<'asc' | 'desc'>('asc');
	let viewMode = $state(view);
	let selectedCustomers = $state<number[]>([]);
	
	// Dialog and sheet states
	let showCustomerDialog = $state(false);
	let showNewCustomerSheet = $state(false);
	let showCustomerDetailSheet = $state(false);
	let selectedCustomer = $state<Customer | null>(null);
	let editingCustomer = $state<Customer | null>(null);
	
	// Form submission state
	let isSubmitting = $state(false);
	
	// FIXED: Complete customer form with all fields
	let customerForm = $state<CustomerForm>({
		name: '',
		phone_number: '',
		email: '',
		date_of_birth: '',
		gender: '',
		address: '',
		notes: ''
	});

	// Customer segments with Arabic labels
	const customerSegments = [
		{ value: 'new', label: 'عملاء جدد', color: 'bg-blue-100 text-blue-800', icon: UserPlus },
		{ value: 'regular', label: 'عملاء منتظمون', color: 'bg-green-100 text-green-800', icon: Users },
		{ value: 'vip', label: 'عملاء VIP', color: 'bg-purple-100 text-purple-800', icon: Crown },
		{ value: 'inactive', label: 'عملاء غير نشطين', color: 'bg-gray-100 text-gray-800', icon: Target }
	];

	// Computed properties
	const filteredCustomers = $derived(() => {
		return customers.filter(customer => {
			const matchesSearch = !searchQuery || 
				customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				customer.phone_number.includes(searchQuery) ||
				customer.email?.toLowerCase().includes(searchQuery.toLowerCase());
			
			const matchesSegment = !segmentFilter || customer.customer_segment === segmentFilter;
			const matchesStatus = !statusFilter || customer.status === statusFilter;
			
			return matchesSearch && matchesSegment && matchesStatus;
		});
	});

	const selectedCustomersData = $derived(() => 
		customers.filter(customer => selectedCustomers.includes(customer.id))
	);

	const customerStats = $derived(() => ({
		total: customers.length,
		new: customers.filter(c => c.customer_segment === 'new').length,
		regular: customers.filter(c => c.customer_segment === 'regular').length,
		vip: customers.filter(c => c.customer_segment === 'vip').length,
		inactive: customers.filter(c => c.customer_segment === 'inactive').length,
		avgSpent: customers.length > 0 
			? customers.reduce((sum, c) => sum + (c.total_spent || 0), 0) / customers.length 
			: 0
	}));

	// FIXED: Complete CRUD operations
	const createNewCustomer = () => {
		resetCustomerForm();
		showNewCustomerSheet = true;
	};

	const handleCreateCustomer = async () => {
		if (isSubmitting) return;
		
		// Enhanced validation
		if (!customerForm.name || !customerForm.phone_number) {
			toast.error('يرجى ملء الاسم ورقم الهاتف');
			return;
		}

		// Saudi phone validation
		if (!customerForm.phone_number.match(/^\+966[0-9]{9}$/)) {
			toast.error('رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx');
			return;
		}

		// Email validation if provided
		if (customerForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerForm.email)) {
			toast.error('البريد الإلكتروني غير صحيح');
			return;
		}

		isSubmitting = true;
		try {
			// Create customer using real API
			const result = await api.customers.create(customerForm);
			
			if (result.success && result.data) {
				customers = [...customers, result.data];
				toast.success('تم إنشاء العميل بنجاح');
				showNewCustomerSheet = false;
				resetCustomerForm();
				dispatch('customerCreated', result.data);
			} else {
				toast.error(result.error || 'فشل في إنشاء العميل');
			}
			
		} catch (error) {
			console.error('Error creating customer:', error);
			toast.error('فشل في إنشاء العميل');
		} finally {
			isSubmitting = false;
		}
	};

	const handleEditCustomer = (customer: Customer) => {
		editingCustomer = customer;
		customerForm = {
			name: customer.name,
			phone_number: customer.phone_number,
			email: customer.email || '',
			date_of_birth: customer.date_of_birth || '',
			gender: customer.gender || '',
			address: customer.address || '',
			notes: customer.notes || ''
		};
		showNewCustomerSheet = true;
	};

	const handleUpdateCustomer = async () => {
		if (!editingCustomer || isSubmitting) return;
		
		// Enhanced validation
		if (!customerForm.name || !customerForm.phone_number) {
			toast.error('يرجى ملء الاسم ورقم الهاتف');
			return;
		}

		// Saudi phone validation
		if (!customerForm.phone_number.match(/^\+966[0-9]{9}$/)) {
			toast.error('رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx');
			return;
		}

		// Email validation if provided
		if (customerForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerForm.email)) {
			toast.error('البريد الإلكتروني غير صحيح');
			return;
		}

		isSubmitting = true;
		try {
			// Update customer using real API
			const result = await api.customers.update(editingCustomer.id, customerForm);
			
			if (result.success && result.data) {
				customers = customers.map(customer => 
					customer.id === editingCustomer?.id ? result.data! : customer
				);
				toast.success('تم تحديث العميل بنجاح');
				showNewCustomerSheet = false;
				resetCustomerForm();
				editingCustomer = null;
			} else {
				toast.error(result.error || 'فشل في تحديث العميل');
			}
			
		} catch (error) {
			console.error('Error updating customer:', error);
			toast.error('فشل في تحديث العميل');
		} finally {
			isSubmitting = false;
		}
	};

	const handleDeleteCustomer = async (customerId: number) => {
		if (!confirm('هل أنت متأكد من حذف هذا العميل؟')) return;
		
		try {
			const result = await api.customers.delete(customerId);
			
			if (result.success) {
				customers = customers.filter(c => c.id !== customerId);
				toast.success('تم حذف العميل بنجاح');
			} else {
				toast.error(result.error || 'فشل في حذف العميل');
			}
		} catch (error) {
			console.error('Error deleting customer:', error);
			toast.error('فشل في حذف العميل');
		}
	};

	const handleViewCustomer = (customer: Customer) => {
		selectedCustomer = customer;
		showCustomerDetailSheet = true;
	};

	const resetCustomerForm = () => {
		customerForm = {
			name: '',
			phone_number: '',
			email: '',
			date_of_birth: '',
			gender: '',
			address: '',
			notes: ''
		};
		editingCustomer = null;
	};

	// Utility functions
	const getSegmentInfo = (segment: string) => {
		return customerSegments.find(s => s.value === segment) || 
			{ value: segment, label: segment, color: 'bg-gray-100 text-gray-800', icon: Users };
	};

	const getInitials = (name: string) => {
		return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
	};

	const formatDate = (dateString: string | null) => {
		if (!dateString) return 'غير محدد';
		return new Date(dateString).toLocaleDateString('ar-SA');
	};

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat('ar-SA', {
			style: 'currency',
			currency: 'SAR'
		}).format(amount);
	};

	// Load data
	const loadCustomers = async () => {
		isLoading = true;
		try {
			const result = await api.customers.getAll();
			
			if (result.success && result.data?.results) {
				customers = result.data.results;
			} else if (result.success && Array.isArray(result.data)) {
				customers = result.data;
			} else {
				console.error('Error loading customers:', result.error);
				toast.error(result.error || 'فشل في تحميل العملاء');
			}
		} catch (error) {
			console.error('Error loading customers:', error);
			toast.error('فشل في تحميل العملاء');
		} finally {
			isLoading = false;
		}
	};

	// Load data on mount
	onMount(() => {
		if (authStore.isAuthenticated) {
			loadCustomers();
		}
	});
</script>

<!-- Customer Management Interface -->
<div class="space-y-6" dir="rtl">
	{#if showHeader}
		<!-- Header -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">إدارة العملاء</h1>
				<p class="text-muted-foreground">إدارة قاعدة عملائك وبناء علاقات قوية</p>
			</div>
			
			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					onclick={loadCustomers}
					disabled={isLoading}
				>
					<RefreshCw class="h-4 w-4 {isLoading ? 'animate-spin' : ''}" />
					تحديث
				</Button>
				
				<!-- FIXED: Functional Add Customer Button -->
				<Button class="btn-premium hover-lift" onclick={createNewCustomer}>
					<Plus class="h-4 w-4" />
					إضافة عميل
				</Button>
			</div>
		</div>
	{/if}

	<!-- Customer Statistics -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-muted-foreground">إجمالي العملاء</p>
						<p class="text-2xl font-bold">{customerStats.total}</p>
					</div>
					<Users class="h-8 w-8 text-blue-600" />
				</div>
			</CardContent>
		</Card>

		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-muted-foreground">عملاء VIP</p>
						<p class="text-2xl font-bold text-purple-600">{customerStats.vip}</p>
					</div>
					<Crown class="h-8 w-8 text-purple-600" />
				</div>
			</CardContent>
		</Card>

		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-muted-foreground">عملاء جدد</p>
						<p class="text-2xl font-bold text-green-600">{customerStats.new}</p>
					</div>
					<UserPlus class="h-8 w-8 text-green-600" />
				</div>
			</CardContent>
		</Card>

		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-muted-foreground">متوسط الإنفاق</p>
						<p class="text-2xl font-bold">{formatPrice(customerStats.avgSpent)}</p>
					</div>
					<DollarSign class="h-8 w-8 text-orange-600" />
				</div>
			</CardContent>
		</Card>
	</div>

	<!-- Filters and Search -->
	<Card class="card-premium">
		<CardContent class="p-6">
			<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<!-- Search -->
				<div class="flex items-center space-x-2 flex-1 max-w-sm">
					<div class="relative flex-1">
						<Search class="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
						<Input
							type="text"
							placeholder="البحث في العملاء..."
							bind:value={searchQuery}
							class="pr-9"
						/>
					</div>
				</div>

				<!-- Filters -->
				<div class="flex items-center space-x-2">
					<Select bind:value={segmentFilter}>
						<SelectTrigger class="w-32">
							<SelectValue placeholder="الفئة" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="">جميع الفئات</SelectItem>
							{#each customerSegments as segment}
								<SelectItem value={segment.value}>{segment.label}</SelectItem>
							{/each}
						</SelectContent>
					</Select>

					<Select bind:value={sortBy}>
						<SelectTrigger class="w-32">
							<SelectValue placeholder="ترتيب بـ" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="name">الاسم</SelectItem>
							<SelectItem value="created_at">تاريخ التسجيل</SelectItem>
							<SelectItem value="last_booking_date">آخر حجز</SelectItem>
							<SelectItem value="total_spent">الإنفاق</SelectItem>
						</SelectContent>
					</Select>

					<!-- View Mode Toggle -->
					<div class="flex items-center border border-border rounded-lg p-1">
						<Button
							variant="ghost"
							size="sm"
							class="h-8 w-8 p-0 {viewMode === 'grid' ? 'bg-muted' : ''}"
							onclick={() => viewMode = 'grid'}
						>
							<Grid class="h-4 w-4" />
						</Button>
						<Button
							variant="ghost"
							size="sm"
							class="h-8 w-8 p-0 {viewMode === 'list' ? 'bg-muted' : ''}"
							onclick={() => viewMode = 'list'}
						>
							<List class="h-4 w-4" />
						</Button>
					</div>
				</div>
			</div>

			<!-- Bulk Actions -->
			{#if selectedCustomers.length > 0}
				<div class="mt-4 flex items-center justify-between border-t border-border pt-4">
					<span class="text-sm text-muted-foreground">
						{selectedCustomers.length} عميل محدد
					</span>
					<div class="flex items-center space-x-2">
						<Button variant="outline" size="sm">
							<Download class="h-4 w-4" />
							تصدير
						</Button>
						<Button variant="outline" size="sm">
							<MessageCircle class="h-4 w-4" />
							رسالة جماعية
						</Button>
					</div>
				</div>
			{/if}
		</CardContent>
	</Card>

	<!-- Customers Content -->
	{#if isLoading}
		<div class="grid gap-4 {viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}">
			{#each Array(6) as _}
				<Card class="animate-pulse">
					<CardContent class="p-6">
						<div class="flex items-center gap-4">
							<div class="h-12 w-12 bg-muted rounded-full"></div>
							<div class="space-y-2">
								<div class="h-4 bg-muted rounded w-32"></div>
								<div class="h-3 bg-muted rounded w-24"></div>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else if filteredCustomers.length === 0}
		<Card class="text-center py-12">
			<CardContent>
				<Users class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
				<h3 class="text-lg font-medium mb-2">لا يوجد عملاء</h3>
				<p class="text-muted-foreground mb-4">
					{searchQuery ? 'لم يتم العثور على عملاء مطابقين' : 'ابدأ ببناء قاعدة عملائك'}
				</p>
				{#if !searchQuery}
					<Button onclick={createNewCustomer}>
						<Plus class="h-4 w-4" />
						إضافة عميل جديد
					</Button>
				{/if}
			</CardContent>
		</Card>
	{:else}
		<!-- Customers Grid/List -->
		<div class="grid gap-4 {viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}">
			{#each filteredCustomers as customer (customer.id)}
				<Card class="card-premium hover-lift transition-all duration-300 group relative overflow-hidden">
					<!-- Selection Checkbox -->
					<div class="absolute top-4 right-4 z-10">
						<input
							type="checkbox"
							class="rounded border-border"
							bind:group={selectedCustomers}
							value={customer.id}
						/>
					</div>

					<CardContent class="p-6">
						<div class="space-y-4">
							<!-- Customer Header -->
							<div class="flex items-center gap-4">
								<Avatar class="h-12 w-12">
									<AvatarImage src={customer.avatar} alt={customer.name} />
									<AvatarFallback>{getInitials(customer.name)}</AvatarFallback>
								</Avatar>
								
								<div class="flex-1 min-w-0">
									<h3 class="font-semibold text-lg truncate">{customer.name}</h3>
									<div class="flex items-center gap-2 mt-1">
										{@const segmentInfo = getSegmentInfo(customer.customer_segment)}
										<Badge class={segmentInfo.color}>
											{segmentInfo.label}
										</Badge>
									</div>
								</div>
							</div>

							<!-- Contact Information -->
							<div class="space-y-2 text-sm">
								<div class="flex items-center gap-2">
									<Phone class="h-4 w-4 text-muted-foreground" />
									<span>{customer.phone_number}</span>
								</div>
								{#if customer.email}
									<div class="flex items-center gap-2">
										<Mail class="h-4 w-4 text-muted-foreground" />
										<span class="truncate">{customer.email}</span>
									</div>
								{/if}
							</div>

							<!-- Customer Statistics -->
							<div class="grid grid-cols-2 gap-4 text-sm">
								<div class="text-center p-2 bg-muted/20 rounded">
									<div class="font-bold text-lg">{customer.total_bookings || 0}</div>
									<div class="text-muted-foreground">حجز</div>
								</div>
								<div class="text-center p-2 bg-muted/20 rounded">
									<div class="font-bold text-lg">
										{formatPrice(customer.total_spent || 0)}
									</div>
									<div class="text-muted-foreground">إنفاق</div>
								</div>
							</div>

							{#if customer.last_booking_date}
								<div class="flex items-center text-sm text-muted-foreground">
									<Calendar class="h-4 w-4 ml-2" />
									آخر حجز: {formatDate(customer.last_booking_date)}
								</div>
							{/if}

							<!-- Actions -->
							<div class="flex items-center gap-2 pt-4 border-t border-border">
								<Button variant="ghost" size="sm" onclick={() => handleViewCustomer(customer)}>
									<Eye class="h-4 w-4" />
								</Button>
								<Button variant="ghost" size="sm" onclick={() => handleEditCustomer(customer)}>
									<Edit class="h-4 w-4" />
								</Button>
								<Button variant="ghost" size="sm" onclick={() => handleDeleteCustomer(customer.id)}>
									<Trash2 class="h-4 w-4" />
								</Button>
								<Button size="sm" class="mr-auto">
									<Calendar class="h-4 w-4 ml-1" />
									حجز جديد
								</Button>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<!-- FIXED: Complete New/Edit Customer Sheet -->
<Sheet.Root bind:open={showNewCustomerSheet}>
	<Sheet.Content side="left" class="w-full sm:max-w-lg">
		<Sheet.Header>
			<Sheet.Title>{editingCustomer ? 'تعديل العميل' : 'إضافة عميل جديد'}</Sheet.Title>
			<Sheet.Description>
				{editingCustomer ? 'تعديل بيانات العميل' : 'إضافة عميل جديد إلى قاعدة البيانات'}
			</Sheet.Description>
		</Sheet.Header>
		
		<form
			class="space-y-6 mt-6"
			onsubmit={(e) => {
				e.preventDefault();
				editingCustomer ? handleUpdateCustomer() : handleCreateCustomer();
			}}
		>
			<!-- Customer Name -->
			<div class="space-y-2">
				<Label for="customer-name">الاسم الكامل *</Label>
				<Input
					id="customer-name"
					bind:value={customerForm.name}
					placeholder="أدخل الاسم الكامل"
					required
				/>
			</div>
			
			<!-- Phone Number -->
			<div class="space-y-2">
				<Label for="customer-phone">رقم الهاتف *</Label>
				<Input
					id="customer-phone"
					bind:value={customerForm.phone_number}
					placeholder="+966xxxxxxxxx"
					required
				/>
			</div>
			
			<!-- Email -->
			<div class="space-y-2">
				<Label for="customer-email">البريد الإلكتروني</Label>
				<Input
					id="customer-email"
					type="email"
					bind:value={customerForm.email}
					placeholder="البريد الإلكتروني (اختياري)"
				/>
			</div>
			
			<!-- Date of Birth -->
			<div class="space-y-2">
				<Label for="customer-dob">تاريخ الميلاد</Label>
				<Input
					id="customer-dob"
					type="date"
					bind:value={customerForm.date_of_birth}
				/>
			</div>
			
			<!-- Gender -->
			<div class="space-y-2">
				<Label for="customer-gender">الجنس</Label>
				<Select bind:value={customerForm.gender}>
					<SelectTrigger>
						<SelectValue placeholder="اختر الجنس" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="">غير محدد</SelectItem>
						<SelectItem value="male">ذكر</SelectItem>
						<SelectItem value="female">أنثى</SelectItem>
					</SelectContent>
				</Select>
			</div>
			
			<!-- Address -->
			<div class="space-y-2">
				<Label for="customer-address">العنوان</Label>
				<Textarea
					id="customer-address"
					bind:value={customerForm.address}
					placeholder="العنوان (اختياري)"
					rows={2}
				/>
			</div>
			
			<!-- Notes -->
			<div class="space-y-2">
				<Label for="customer-notes">ملاحظات</Label>
				<Textarea
					id="customer-notes"
					bind:value={customerForm.notes}
					placeholder="ملاحظات عن العميل (اختياري)"
					rows={3}
				/>
			</div>

			<!-- Actions -->
			<div class="flex items-center justify-end space-x-2 pt-4 border-t border-border">
				<Button variant="outline" type="button" onclick={() => showNewCustomerSheet = false}>
					إلغاء
				</Button>
				<Button type="submit" class="btn-premium" disabled={isSubmitting}>
					{isSubmitting ? 'جاري الحفظ...' : editingCustomer ? 'تحديث العميل' : 'إضافة العميل'}
				</Button>
			</div>
		</form>
	</Sheet.Content>
</Sheet.Root>

<!-- Customer Detail Sheet -->
<Sheet.Root bind:open={showCustomerDetailSheet}>
	<Sheet.Content side="right" class="w-full sm:max-w-lg">
		<Sheet.Header>
			<Sheet.Title>تفاصيل العميل</Sheet.Title>
			<Sheet.Description>
				معلومات مفصلة عن العميل
			</Sheet.Description>
		</Sheet.Header>
		
		{#if selectedCustomer}
			<div class="space-y-6 mt-6">
				<!-- Customer Header -->
				<div class="flex items-center gap-4">
					<Avatar class="h-16 w-16">
						<AvatarImage src={selectedCustomer.avatar} alt={selectedCustomer.name} />
						<AvatarFallback>{getInitials(selectedCustomer.name)}</AvatarFallback>
					</Avatar>
					
					<div>
						<h3 class="text-xl font-bold">{selectedCustomer.name}</h3>
						{@const segmentInfo = getSegmentInfo(selectedCustomer.customer_segment)}
						<Badge class={segmentInfo.color}>
							{segmentInfo.label}
						</Badge>
					</div>
				</div>

				<!-- Customer Stats -->
				<div class="grid grid-cols-3 gap-4">
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">{selectedCustomer.total_bookings || 0}</div>
							<div class="text-sm text-muted-foreground">حجز</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">{formatPrice(selectedCustomer.total_spent || 0)}</div>
							<div class="text-sm text-muted-foreground">إنفاق</div>
						</CardContent>
					</Card>
					<Card>
						<CardContent class="p-4 text-center">
							<div class="text-2xl font-bold">-</div>
							<div class="text-sm text-muted-foreground">تقييم</div>
						</CardContent>
					</Card>
				</div>

				<!-- Contact Information -->
				<div class="space-y-4">
					<h4 class="font-medium">معلومات التواصل</h4>
					<div class="space-y-2">
						<div class="flex items-center gap-2">
							<Phone class="h-4 w-4 text-muted-foreground" />
							<span>{selectedCustomer.phone_number}</span>
						</div>
						{#if selectedCustomer.email}
							<div class="flex items-center gap-2">
								<Mail class="h-4 w-4 text-muted-foreground" />
								<span>{selectedCustomer.email}</span>
							</div>
						{/if}
						{#if selectedCustomer.address}
							<div class="flex items-center gap-2">
								<MapPin class="h-4 w-4 text-muted-foreground" />
								<span>{selectedCustomer.address}</span>
							</div>
						{/if}
					</div>
				</div>

				<!-- Additional Information -->
				{#if selectedCustomer.notes}
					<div class="space-y-4">
						<h4 class="font-medium">ملاحظات</h4>
						<p class="text-sm text-muted-foreground">{selectedCustomer.notes}</p>
					</div>
				{/if}

				<!-- Actions -->
				<div class="flex gap-2 pt-4 border-t border-border">
					<Button variant="outline" onclick={() => handleEditCustomer(selectedCustomer)}>
						<Edit class="h-4 w-4 ml-2" />
						تعديل
					</Button>
					<Button class="flex-1">
						<Calendar class="h-4 w-4 ml-2" />
						حجز جديد
					</Button>
				</div>
			</div>
		{/if}
	</Sheet.Content>
</Sheet.Root>

<style>
	.card-premium {
		background: rgba(255, 255, 255, 0.7);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
	}

	.btn-premium {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border: none;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
		transition: all 0.3s ease;
	}

	.btn-premium:hover {
		transform: translateY(-2px);
		box-shadow: 0 7px 25px rgba(102, 126, 234, 0.6);
	}

	.hover-lift {
		transition: transform 0.2s ease, box-shadow 0.2s ease;
	}

	.hover-lift:hover {
		transform: translateY(-2px);
	}
</style>