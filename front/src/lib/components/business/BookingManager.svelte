<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import type { Booking, Service, Customer } from '$lib/types/index.js';
	import { api } from '$lib/services/api-client.js';
	import { appStore } from '$lib/stores/app.svelte.js';
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
	import { Sheet } from '$lib/components/ui/sheet';
	import { Calendar } from '$lib/components/ui/calendar';
	import { Popover, PopoverContent, PopoverTrigger } from '$lib/components/ui/popover';
	import { toast } from 'svelte-sonner';
	
	// Icons
	import {
		Calendar as CalendarIcon,
		Clock,
		Plus,
		Edit,
		Trash2,
		Eye,
		Search,
		Filter,
		RefreshCw,
		Users,
		ChevronLeft,
		ChevronRight,
		GripVertical,
		Phone,
		Mail,
		User,
		MapPin,
		CheckCircle,
		XCircle,
		AlertCircle
	} from 'lucide-svelte';
	
	// Date utilities
	import { DateFormatter } from '@internationalized/date';
	import type { DateValue } from '@internationalized/date';

	interface Props {
		businessId?: number;
		showHeader?: boolean;
	}

	let { businessId, showHeader = true }: Props = $props();

	const dispatch = createEventDispatcher();

	// State management using Svelte 5 runes
	let currentView = $state<'month' | 'week' | 'day'>('week');
	let currentDate = $state(new Date());
	let selectedDate = $state<DateValue | undefined>(undefined);
	let bookings = $state<Booking[]>([]);
	let services = $state<Service[]>([]);
	let customers = $state<Customer[]>([]);
	let isLoading = $state(false);
	let searchQuery = $state('');
	let statusFilter = $state<string>('');
	let serviceFilter = $state<number | null>(null);
	let dateFilter = $state<DateValue | undefined>(undefined);
	let sortField = $state<'date' | 'customer' | 'service' | 'status'>('date');
	let sortOrder = $state<'asc' | 'desc'>('asc');
	
	// Dialog and sheet states
	let showBookingDialog = $state(false);
	let showNewBookingSheet = $state(false);
	let selectedBooking = $state<Booking | null>(null);
	let editingBooking = $state<Booking | null>(null);
	let isDragging = $state(false);
	let draggedBooking = $state<Booking | null>(null);
	
	// Form submission state
	let isSubmitting = $state(false);
	
	// FIXED: Proper nested customer object structure
	let newBookingData = $state({
		service_id: '',
		customer: {
			name: '',
			phone_number: '',
			email: ''
		},
		appointment_date: '',
		appointment_time: '',
		notes: '',
		booking_method: 'online' as const,
		auto_confirm: false
	});
	
	// Arabic localization
	const dateFormatter = new DateFormatter('ar-SA', {
		dateStyle: 'full',
		calendar: 'gregory'
	});
	
	const timeFormatter = new DateFormatter('ar-SA', {
		timeStyle: 'short',
		hour12: false
	});
	
	// Arabic month names
	const arabicMonths = [
		'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
		'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
	];
	
	// Arabic day names (Saudi week starts Saturday)
	const arabicDays = ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'];
	
	// Time slots (9 AM to 9 PM)
	const timeSlots = [
		'09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
		'12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
		'15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
		'18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'
	];

	// Computed properties
	const filteredBookings = $derived(() => {
		return bookings.filter(booking => {
			const matchesSearch = !searchQuery || 
				booking.customer?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
				booking.service?.name.toLowerCase().includes(searchQuery.toLowerCase());
			
			const matchesStatus = !statusFilter || booking.status === statusFilter;
			const matchesService = !serviceFilter || booking.service?.id === serviceFilter;
			
			let matchesDate = true;
			if (dateFilter) {
				const bookingDate = new Date(booking.appointment_date);
				const filterDate = new Date(dateFilter.year, dateFilter.month - 1, dateFilter.day);
				matchesDate = bookingDate.toDateString() === filterDate.toDateString();
			}
			
			return matchesSearch && matchesStatus && matchesService && matchesDate;
		});
	});

	const weekDays = $derived(() => {
		const startOfWeek = new Date(currentDate);
		// Set to Saturday (Saudi week starts Saturday)
		const dayOfWeek = startOfWeek.getDay();
		const diffToSaturday = (dayOfWeek + 1) % 7; // Saturday = 6, but we want 0
		startOfWeek.setDate(startOfWeek.getDate() - diffToSaturday);
		
		return Array.from({ length: 7 }, (_, i) => {
			const date = new Date(startOfWeek);
			date.setDate(startOfWeek.getDate() + i);
			return date;
		});
	});

	const currentMonthDays = $derived(() => {
		const year = currentDate.getFullYear();
		const month = currentDate.getMonth();
		const firstDay = new Date(year, month, 1);
		const lastDay = new Date(year, month + 1, 0);
		
		// Start from Saturday (Saudi week)
		const startDate = new Date(firstDay);
		const startDayOfWeek = (firstDay.getDay() + 1) % 7; // Adjust for Saturday start
		startDate.setDate(firstDay.getDate() - startDayOfWeek);
		
		const days = [];
		const currentIterDate = new Date(startDate);
		
		// Generate 6 weeks (42 days) to fill the calendar grid
		for (let i = 0; i < 42; i++) {
			days.push(new Date(currentIterDate));
			currentIterDate.setDate(currentIterDate.getDate() + 1);
		}
		
		return days;
	});

	// Booking management functions
	const getBookingsForDateAndTime = (date: Date, time: string): Booking[] => {
		const dateStr = date.toISOString().split('T')[0];
		return bookings.filter(booking => 
			booking.appointment_date === dateStr && 
			booking.appointment_time === time
		);
	};

	const getBookingsForDate = (date: Date): Booking[] => {
		const dateStr = date.toISOString().split('T')[0];
		return bookings.filter(booking => booking.appointment_date === dateStr);
	};

	const checkBookingConflicts = (date: Date, time: string, serviceId: number, excludeBookingId?: number): boolean => {
		const service = services.find(s => s.id === serviceId);
		if (!service?.duration) return false;
		
		const startTime = new Date(`${date.toISOString().split('T')[0]} ${time}`);
		const endTime = new Date(startTime.getTime() + service.duration * 60000);
		
		return bookings.some(booking => {
			if (excludeBookingId && booking.id === excludeBookingId) return false;
			
			const bookingStart = new Date(`${booking.appointment_date} ${booking.appointment_time}`);
			const bookingService = services.find(s => s.id === booking.service?.id);
			const bookingEnd = new Date(bookingStart.getTime() + (bookingService?.duration || 0) * 60000);
			
			return (startTime < bookingEnd && endTime > bookingStart);
		});
	};

	// CRUD operations
	const createNewBooking = (date?: Date, time?: string) => {
		if (date && time) {
			newBookingData.appointment_date = date.toISOString().split('T')[0];
			newBookingData.appointment_time = time;
		}
		showNewBookingSheet = true;
	};

	const handleCreateBooking = async () => {
		if (isSubmitting) return;
		
		// Enhanced validation
		if (!newBookingData.service_id || !newBookingData.customer.name || !newBookingData.customer.phone_number ||
			!newBookingData.appointment_date || !newBookingData.appointment_time) {
			toast.error('يرجى ملء جميع الحقول المطلوبة');
			return;
		}

		// Saudi phone validation
		if (!newBookingData.customer.phone_number.match(/^\+966[0-9]{9}$/)) {
			toast.error('رقم الهاتف يجب أن يكون بصيغة +966xxxxxxxxx');
			return;
		}

		// Email validation if provided
		if (newBookingData.customer.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newBookingData.customer.email)) {
			toast.error('البريد الإلكتروني غير صحيح');
			return;
		}

		// Date validation
		const appointmentDateTime = new Date(newBookingData.appointment_date + ' ' + newBookingData.appointment_time);
		if (appointmentDateTime <= new Date()) {
			toast.error('لا يمكن حجز موعد في الماضي');
			return;
		}

		// Conflict validation
		const date = new Date(newBookingData.appointment_date);
		const hasConflicts = checkBookingConflicts(date, newBookingData.appointment_time, parseInt(newBookingData.service_id));
		if (hasConflicts) {
			toast.error('يوجد تعارض مع حجز آخر في هذا الوقت');
			return;
		}

		isSubmitting = true;
		try {
			// Use proper nested customer structure for API
			const bookingPayload = {
				service_id: parseInt(newBookingData.service_id),
				customer: newBookingData.customer, // Properly nested
				appointment_date: newBookingData.appointment_date,
				appointment_time: newBookingData.appointment_time,
				notes: newBookingData.notes,
				booking_method: newBookingData.booking_method,
				auto_confirm: newBookingData.auto_confirm
			};

			// Create booking using real API
			const result = await api.bookings.create(bookingPayload);
			
			if (result.success && result.data) {
				bookings = [...bookings, result.data];
				toast.success('تم إنشاء الحجز بنجاح');
				showNewBookingSheet = false;
				resetNewBookingForm();
				dispatch('bookingCreated', result.data);
			} else {
				toast.error(result.error || 'فشل في إنشاء الحجز');
			}
			
		} catch (error) {
			console.error('Error creating booking:', error);
			toast.error('فشل في إنشاء الحجز');
		} finally {
			isSubmitting = false;
		}
	};

	const resetNewBookingForm = () => {
		newBookingData = {
			service_id: '',
			customer: {
				name: '',
				phone_number: '',
				email: ''
			},
			appointment_date: '',
			appointment_time: '',
			notes: '',
			booking_method: 'online',
			auto_confirm: false
		};
	};

	const handleDeleteBooking = async (bookingId: number) => {
		if (!confirm('هل أنت متأكد من حذف هذا الحجز؟')) return;
		
		try {
			const result = await api.bookings.delete(bookingId);
			
			if (result.success) {
				bookings = bookings.filter(b => b.id !== bookingId);
				toast.success('تم حذف الحجز بنجاح');
			} else {
				toast.error(result.error || 'فشل في حذف الحجز');
			}
		} catch (error) {
			console.error('Error deleting booking:', error);
			toast.error('فشل في حذف الحجز');
		}
	};

	// Drag and drop functionality
	const handleDragStart = (e: DragEvent, booking: Booking) => {
		if (!e.dataTransfer) return;
		e.dataTransfer.effectAllowed = 'move';
		draggedBooking = booking;
		isDragging = true;
	};

	const handleDragOver = (e: DragEvent) => {
		e.preventDefault();
		if (e.dataTransfer) {
			e.dataTransfer.dropEffect = 'move';
		}
	};

	const handleDrop = async (e: DragEvent, date: Date, time: string) => {
		e.preventDefault();
		if (!draggedBooking) return;

		const hasConflicts = checkBookingConflicts(date, time, draggedBooking.service?.id || 0, draggedBooking.id);
		if (hasConflicts) {
			toast.error('لا يمكن نقل الحجز - يوجد تعارض');
			isDragging = false;
			draggedBooking = null;
			return;
		}

		try {
			// Update booking date and time using real API
			const result = await api.bookings.update(draggedBooking.id, {
				appointment_date: date.toISOString().split('T')[0],
				appointment_time: time
			});
			
			if (result.success && result.data) {
				bookings = bookings.map(booking => 
					booking.id === draggedBooking?.id ? result.data! : booking
				);
				toast.success('تم نقل الحجز بنجاح');
			} else {
				toast.error(result.error || 'فشل في نقل الحجز');
			}
		} catch (error) {
			console.error('Error updating booking:', error);
			toast.error('فشل في نقل الحجز');
		}

		isDragging = false;
		draggedBooking = null;
	};

	// Status helpers
	const getStatusColor = (status: string) => {
		switch (status) {
			case 'confirmed': return 'bg-green-500';
			case 'pending': return 'bg-yellow-500';
			case 'cancelled': return 'bg-red-500';
			case 'completed': return 'bg-blue-500';
			default: return 'bg-gray-500';
		}
	};

	const getStatusText = (status: string) => {
		switch (status) {
			case 'confirmed': return 'مؤكد';
			case 'pending': return 'في الانتظار';
			case 'cancelled': return 'ملغي';
			case 'completed': return 'مكتمل';
			default: return status;
		}
	};

	// Navigation functions
	const navigateDate = (direction: 'prev' | 'next') => {
		const newDate = new Date(currentDate);
		
		switch (currentView) {
			case 'month':
				newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
				break;
			case 'week':
				newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
				break;
			case 'day':
				newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
				break;
		}
		
		currentDate = newDate;
	};

	// Load data
	const loadBookings = async () => {
		isLoading = true;
		try {
			// Load services from appStore (already integrated with real API)
			await appStore.loadServices();
			services = appStore.services;
			
			// Load bookings from real API
			const bookingsResult = await api.bookings.getAll();
			if (bookingsResult.success && bookingsResult.data?.results) {
				bookings = bookingsResult.data.results;
			} else if (bookingsResult.success && Array.isArray(bookingsResult.data)) {
				bookings = bookingsResult.data;
			} else {
				console.error('Error loading bookings:', bookingsResult.error);
				toast.error(bookingsResult.error || 'فشل في تحميل الحجوزات');
			}

			// Load customers from real API
			const customersResult = await api.customers.getAll();
			if (customersResult.success && customersResult.data?.results) {
				customers = customersResult.data.results;
			} else if (customersResult.success && Array.isArray(customersResult.data)) {
				customers = customersResult.data;
			} else {
				console.error('Error loading customers:', customersResult.error);
				// Don't show error toast for customers as it's less critical
			}
		} catch (error) {
			console.error('Error loading data:', error);
			toast.error('فشل في تحميل البيانات');
		} finally {
			isLoading = false;
		}
	};

	// Load data on mount
	onMount(() => {
		if (authStore.isAuthenticated) {
			loadBookings();
		}
	});
</script>

<!-- Calendar Interface -->
<div class="space-y-6" dir="rtl">
	{#if showHeader}
		<!-- Header -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">إدارة الحجوزات</h1>
				<p class="text-muted-foreground">تقويم الحجوزات وإدارة المواعيد</p>
			</div>
			
			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					onclick={loadBookings}
					disabled={isLoading}
				>
					<RefreshCw class="h-4 w-4 {isLoading ? 'animate-spin' : ''}" />
					تحديث
				</Button>
				
				<Button class="btn-premium hover-lift" onclick={() => createNewBooking()}>
					<Plus class="h-4 w-4" />
					حجز جديد
				</Button>
			</div>
		</div>
	{/if}

	<!-- Calendar Header -->
	<Card class="card-premium">
		<CardHeader>
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-4">
					<Button variant="outline" size="sm" onclick={() => navigateDate('prev')}>
						<ChevronRight class="h-4 w-4" />
					</Button>
					
					<h2 class="text-xl font-semibold">
						{arabicMonths[currentDate.getMonth()]} {currentDate.getFullYear()}
					</h2>
					
					<Button variant="outline" size="sm" onclick={() => navigateDate('next')}>
						<ChevronLeft class="h-4 w-4" />
					</Button>
				</div>
				
				<div class="flex items-center gap-2">
					<div class="flex rounded-lg border p-1">
						<Button
							variant={currentView === 'month' ? 'default' : 'ghost'}
							size="sm"
							onclick={() => currentView = 'month'}
						>
							شهر
						</Button>
						<Button
							variant={currentView === 'week' ? 'default' : 'ghost'}
							size="sm"
							onclick={() => currentView = 'week'}
						>
							أسبوع
						</Button>
						<Button
							variant={currentView === 'day' ? 'default' : 'ghost'}
							size="sm"
							onclick={() => currentView = 'day'}
						>
							يوم
						</Button>
					</div>
				</div>
			</div>
		</CardHeader>
	</Card>

	<!-- Calendar Grid -->
	<Card class="card-premium">
		<CardContent class="p-6">
			<!-- Week View -->
			{#if currentView === 'week'}
				<div class="space-y-4">
					<!-- Days Header -->
					<div class="grid grid-cols-8 gap-1 border-b pb-2">
						<div class="text-xs font-medium text-muted-foreground p-2">الوقت</div>
						{#each weekDays as day}
							<div class="text-center p-2">
								<div class="text-sm font-medium">{arabicDays[day.getDay()]}</div>
								<div class="text-xs text-muted-foreground">{day.getDate()}</div>
							</div>
						{/each}
					</div>
					
					<!-- Time Slots -->
					<div class="grid grid-cols-8 gap-1">
						{#each timeSlots as time}
							<div class="text-xs text-muted-foreground p-2 border-l">{time}</div>
							{#each weekDays as day}
								<div 
									class="relative min-h-[60px] border border-border/50 group hover:bg-muted/30 transition-colors"
									ondragover={handleDragOver}
									ondrop={(e) => handleDrop(e, day, time)}
								>
									<!-- Existing Bookings -->
									{#each getBookingsForDateAndTime(day, time) as booking}
										<div 
											class="absolute inset-1 p-2 rounded text-xs {getStatusColor(booking.status)} text-white cursor-move z-10"
											draggable="true"
											ondragstart={(e) => handleDragStart(e, booking)}
										>
											<div class="font-medium">{booking.customer?.name}</div>
											<div class="opacity-90">{booking.service?.name}</div>
										</div>
									{/each}
									
									<!-- Add Button for Empty Slots -->
									{#if getBookingsForDateAndTime(day, time).length === 0}
										<button 
											class="absolute inset-0 w-full h-full opacity-0 group-hover:opacity-100 bg-blue-500/10 flex items-center justify-center transition-all duration-200 hover:bg-blue-500/20"
											onclick={() => createNewBooking(day, time)}
										>
											<Plus class="h-4 w-4 text-blue-600" />
										</button>
									{/if}
								</div>
							{/each}
						{/each}
					</div>
				</div>
			{/if}

			<!-- Month View -->
			{#if currentView === 'month'}
				<div class="space-y-4">
					<!-- Days Header -->
					<div class="grid grid-cols-7 gap-1 border-b pb-2">
						{#each arabicDays as day}
							<div class="text-center p-2 text-sm font-medium">{day}</div>
						{/each}
					</div>
					
					<!-- Calendar Days -->
					<div class="grid grid-cols-7 gap-1">
						{#each currentMonthDays as day}
							{@const dayBookings = getBookingsForDate(day)}
							{@const isCurrentMonth = day.getMonth() === currentDate.getMonth()}
							{@const isToday = day.toDateString() === new Date().toDateString()}
							
							<div 
								class="relative min-h-[100px] border border-border/50 p-1 {isCurrentMonth ? 'bg-background' : 'bg-muted/30'} {isToday ? 'ring-2 ring-primary' : ''}"
								onclick={() => createNewBooking(day)}
							>
								<div class="text-sm font-medium mb-1 {isCurrentMonth ? '' : 'opacity-50'}">
									{day.getDate()}
								</div>
								
								<div class="space-y-1">
									{#each dayBookings.slice(0, 3) as booking}
										<div class="text-xs p-1 rounded {getStatusColor(booking.status)} text-white truncate">
											{booking.customer?.name}
										</div>
									{/each}
									{#if dayBookings.length > 3}
										<div class="text-xs text-muted-foreground">+{dayBookings.length - 3} أكثر</div>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Day View -->
			{#if currentView === 'day'}
				<div class="space-y-4">
					<div class="text-lg font-semibold text-center">
						{arabicDays[currentDate.getDay()]} - {currentDate.getDate()} {arabicMonths[currentDate.getMonth()]}
					</div>
					
					<div class="grid grid-cols-2 gap-1">
						<div class="text-xs font-medium text-muted-foreground p-2">الوقت</div>
						<div class="text-xs font-medium text-muted-foreground p-2">الحجز</div>
						
						{#each timeSlots as time}
							<div class="text-xs text-muted-foreground p-2 border-l">{time}</div>
							<div 
								class="relative min-h-[60px] border border-border/50 group hover:bg-muted/30 transition-colors"
								ondragover={handleDragOver}
								ondrop={(e) => handleDrop(e, currentDate, time)}
							>
								{#each getBookingsForDateAndTime(currentDate, time) as booking}
									<div 
										class="absolute inset-1 p-2 rounded text-xs {getStatusColor(booking.status)} text-white cursor-move"
										draggable="true"
										ondragstart={(e) => handleDragStart(e, booking)}
									>
										<div class="font-medium">{booking.customer?.name}</div>
										<div class="opacity-90">{booking.service?.name}</div>
									</div>
								{/each}
								
								{#if getBookingsForDateAndTime(currentDate, time).length === 0}
									<button 
										class="absolute inset-0 w-full h-full opacity-0 group-hover:opacity-100 bg-blue-500/10 flex items-center justify-center transition-all duration-200 hover:bg-blue-500/20"
										onclick={() => createNewBooking(currentDate, time)}
									>
										<Plus class="h-4 w-4 text-blue-600" />
									</button>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			{/if}
		</CardContent>
	</Card>
</div>

<!-- New Booking Sheet -->
<Sheet.Root bind:open={showNewBookingSheet}>
	<Sheet.Content side="left" class="w-full sm:max-w-lg">
		<Sheet.Header>
			<Sheet.Title>حجز جديد</Sheet.Title>
			<Sheet.Description>
				إضافة حجز جديد للتقويم
			</Sheet.Description>
		</Sheet.Header>
		
		<form
			class="space-y-6 mt-6"
			onsubmit={(e) => {
				e.preventDefault();
				handleCreateBooking();
			}}
		>
			<!-- Service Selection -->
			<div class="space-y-2">
				<Label for="service">الخدمة</Label>
				<Select bind:value={newBookingData.service_id}>
					<SelectTrigger>
						<SelectValue placeholder="اختر الخدمة" />
					</SelectTrigger>
					<SelectContent>
						{#each services as service}
							<SelectItem value={service.id.toString()}>{service.name}</SelectItem>
						{/each}
					</SelectContent>
				</Select>
			</div>

			<!-- Customer Information -->
			<div class="space-y-4">
				<h3 class="text-lg font-medium">بيانات العميل</h3>
				
				<div class="space-y-2">
					<Label for="customer-name">اسم العميل</Label>
					<Input
						id="customer-name"
						bind:value={newBookingData.customer.name}
						placeholder="أدخل اسم العميل"
						required
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="customer-phone">رقم الهاتف</Label>
					<Input
						id="customer-phone"
						bind:value={newBookingData.customer.phone_number}
						placeholder="+966xxxxxxxxx"
						required
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="customer-email">البريد الإلكتروني (اختياري)</Label>
					<Input
						id="customer-email"
						bind:value={newBookingData.customer.email}
						placeholder="example@email.com"
						type="email"
					/>
				</div>
			</div>

			<!-- Date and Time -->
			<div class="grid grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="date">التاريخ</Label>
					<Input
						id="date"
						type="date"
						bind:value={newBookingData.appointment_date}
						required
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="time">الوقت</Label>
					<Select bind:value={newBookingData.appointment_time}>
						<SelectTrigger>
							<SelectValue placeholder="اختر الوقت" />
						</SelectTrigger>
						<SelectContent>
							{#each timeSlots as time}
								<SelectItem value={time}>{time}</SelectItem>
							{/each}
						</SelectContent>
					</Select>
				</div>
			</div>

			<!-- Notes -->
			<div class="space-y-2">
				<Label for="notes">ملاحظات</Label>
				<Textarea
					id="notes"
					bind:value={newBookingData.notes}
					placeholder="ملاحظات إضافية..."
					rows={3}
				/>
			</div>

			<!-- Actions -->
			<div class="flex items-center justify-end space-x-2 pt-4 border-t border-border">
				<Button variant="outline" type="button" onclick={() => showNewBookingSheet = false}>
					إلغاء
				</Button>
				<Button type="submit" class="btn-premium" disabled={isSubmitting}>
					{isSubmitting ? 'جاري الحفظ...' : 'إنشاء الحجز'}
				</Button>
			</div>
		</form>
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