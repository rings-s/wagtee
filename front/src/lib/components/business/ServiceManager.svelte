<script lang="ts">
	import { onMount } from 'svelte';
	import type { Service, ServiceForm } from '$lib/types/index.js';
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
	import { Switch } from '$lib/components/ui/switch';
	import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '$lib/components/ui/dialog';
	import { toast } from 'svelte-sonner';
	
	// Icons
	import {
		Plus,
		Edit,
		Trash2,
		Eye,
		Search,
		Filter,
		Grid,
		List,
		Clock,
		DollarSign,
		Star,
		Sparkles,
		TrendingUp,
		Copy,
		MoreHorizontal,
		RefreshCw
	} from 'lucide-svelte';

	interface Props {
		businessId?: number;
		view?: 'grid' | 'list';
		showHeader?: boolean;
	}

	let { businessId, view = 'grid', showHeader = true }: Props = $props();

	// Reactive state using Svelte 5 runes
	let searchTerm = $state('');
	let filterStatus = $state<'all' | 'active' | 'inactive'>('all');
	let sortBy = $state<'name' | 'price' | 'created_at'>('name');
	let sortOrder = $state<'asc' | 'desc'>('asc');
	let viewMode = $state(view);
	let selectedServices = $state<number[]>([]);
	let showServiceDialog = $state(false);
	let editingService = $state<Service | null>(null);
	let isSubmitting = $state(false);

	// FIXED: Form state with proper duration handling
	let serviceForm = $state<ServiceForm>({
		name: '',
		name_ar: '',
		description: '',
		description_ar: '',
		price: 0,
		duration: '01:00:00',
		is_active: true
	});

	// Duration conversion utilities
	const convertTimeToSeconds = (timeString: string): number => {
		const [hours, minutes] = timeString.split(':').map(Number);
		return (hours * 60 + minutes) * 60;
	};

	const convertSecondsToTime = (seconds: number): string => {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
	};

	const convertDurationFormat = (duration: string): string => {
		if (duration.includes(':')) {
			// If it's already in HH:MM format, convert to HH:MM:SS
			if (duration.split(':').length === 2) {
				return duration + ':00';
			}
		}
		return duration;
	};

	// Derived values
	const filteredServices = $derived(() => {
		let filtered = appStore.services;

		// Search filter
		if (searchTerm) {
			filtered = filtered.filter(service => 
				service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
				service.name_ar?.toLowerCase().includes(searchTerm.toLowerCase()) ||
				service.description?.toLowerCase().includes(searchTerm.toLowerCase())
			);
		}

		// Status filter
		if (filterStatus !== 'all') {
			filtered = filtered.filter(service => 
				filterStatus === 'active' ? service.is_active : !service.is_active
			);
		}

		// Sort
		filtered.sort((a, b) => {
			let comparison = 0;
			switch (sortBy) {
				case 'name':
					comparison = a.name.localeCompare(b.name);
					break;
				case 'price':
					comparison = a.price - b.price;
					break;
				case 'created_at':
					comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
					break;
			}
			return sortOrder === 'asc' ? comparison : -comparison;
		});

		return filtered;
	});

	const selectedServicesData = $derived(() => 
		appStore.services.filter(service => selectedServices.includes(service.id))
	);

	// FIXED: Actions with proper loading states and Arabic messages
	const handleCreateService = async () => {
		if (isSubmitting) return;
		
		// Validate required fields
		if (!serviceForm.name || !serviceForm.name_ar || serviceForm.price <= 0) {
			toast.error('يرجى ملء جميع الحقول المطلوبة');
			return;
		}

		isSubmitting = true;
		try {
			// Convert duration format for API
			const formData = {
				...serviceForm,
				duration: convertDurationFormat(serviceForm.duration)
			};

			const result = await appStore.createService(formData);
			if (result.success) {
				toast.success('تم إنشاء الخدمة بنجاح');
				showServiceDialog = false;
				resetForm();
			} else {
				toast.error(result.error || 'فشل في إنشاء الخدمة');
			}
		} catch (error) {
			console.error('Error creating service:', error);
			toast.error('حدث خطأ في إنشاء الخدمة');
		} finally {
			isSubmitting = false;
		}
	};

	const handleUpdateService = async () => {
		if (!editingService || isSubmitting) return;
		
		// Validate required fields
		if (!serviceForm.name || !serviceForm.name_ar || serviceForm.price <= 0) {
			toast.error('يرجى ملء جميع الحقول المطلوبة');
			return;
		}
		
		isSubmitting = true;
		try {
			// Convert duration format for API
			const formData = {
				...serviceForm,
				duration: convertDurationFormat(serviceForm.duration)
			};

			const result = await appStore.updateService(editingService.id, formData);
			if (result.success) {
				toast.success('تم تحديث الخدمة بنجاح');
				showServiceDialog = false;
				resetForm();
				editingService = null;
			} else {
				toast.error(result.error || 'فشل في تحديث الخدمة');
			}
		} catch (error) {
			console.error('Error updating service:', error);
			toast.error('حدث خطأ في تحديث الخدمة');
		} finally {
			isSubmitting = false;
		}
	};

	const handleDeleteService = async (serviceId: number) => {
		if (!confirm('هل أنت متأكد من حذف هذه الخدمة؟')) return;
		
		const result = await appStore.deleteService(serviceId);
		if (result.success) {
			toast.success('تم حذف الخدمة بنجاح');
		} else {
			toast.error(result.error || 'فشل في حذف الخدمة');
		}
	};

	const handleBulkDelete = async () => {
		if (selectedServices.length === 0) return;
		if (!confirm(`حذف ${selectedServices.length} خدمة محددة؟`)) return;

		const results = await Promise.all(
			selectedServices.map(id => appStore.deleteService(id))
		);

		const successCount = results.filter(r => r.success).length;
		toast.success(`تم حذف ${successCount} خدمة بنجاح`);
		selectedServices = [];
	};

	const handleToggleActive = async (serviceId: number, isActive: boolean) => {
		const result = await appStore.updateService(serviceId, { is_active: isActive });
		if (result.success) {
			toast.success(`تم ${isActive ? 'تفعيل' : 'إلغاء تفعيل'} الخدمة`);
		} else {
			toast.error('فشل في تحديث حالة الخدمة');
		}
	};

	const handleEditService = (service: Service) => {
		editingService = service;
		serviceForm = {
			name: service.name,
			name_ar: service.name_ar || '',
			description: service.description || '',
			description_ar: service.description_ar || '',
			price: service.price,
			duration: convertSecondsToTime(typeof service.duration === 'string' ? 
				convertTimeToSeconds(service.duration.split(':').slice(0, 2).join(':')) : 
				service.duration * 60
			),
			is_active: service.is_active
		};
		showServiceDialog = true;
	};

	const handleDuplicateService = (service: Service) => {
		serviceForm = {
			name: `${service.name} (نسخة)`,
			name_ar: service.name_ar ? `${service.name_ar} (نسخة)` : '',
			description: service.description || '',
			description_ar: service.description_ar || '',
			price: service.price,
			duration: convertSecondsToTime(typeof service.duration === 'string' ? 
				convertTimeToSeconds(service.duration.split(':').slice(0, 2).join(':')) : 
				service.duration * 60
			),
			is_active: service.is_active
		};
		editingService = null;
		showServiceDialog = true;
	};

	const resetForm = () => {
		serviceForm = {
			name: '',
			name_ar: '',
			description: '',
			description_ar: '',
			price: 0,
			duration: '01:00',
			is_active: true
		};
		editingService = null;
	};

	const formatDuration = (duration: string): string => {
		const [hours, minutes] = duration.split(':');
		const h = parseInt(hours);
		const m = parseInt(minutes);
		if (h > 0 && m > 0) return `${h}س ${m}د`;
		if (h > 0) return `${h}س`;
		return `${m}د`;
	};

	const formatPrice = (price: number): string => {
		return new Intl.NumberFormat('ar-SA', {
			style: 'currency',
			currency: 'SAR'
		}).format(price);
	};

	// Load services on mount
	onMount(() => {
		if (authStore.isAuthenticated) {
			appStore.loadServices();
		}
	});
</script>

<!-- Services Management Interface -->
<div class="space-y-6" dir="rtl">
	{#if showHeader}
		<!-- Header Section -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">إدارة الخدمات</h1>
				<p class="text-muted-foreground">إدارة خدمات ومنتجات عملك</p>
			</div>
			
			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					onclick={() => appStore.loadServices()}
					disabled={appStore.isServicesLoading}
				>
					<RefreshCw class="h-4 w-4 {appStore.isServicesLoading ? 'animate-spin' : ''}" />
					تحديث
				</Button>
				
				<Dialog bind:open={showServiceDialog}>
					<DialogTrigger>
						<Button class="btn-premium hover-lift" onclick={resetForm}>
							<Plus class="h-4 w-4" />
							إضافة خدمة
						</Button>
					</DialogTrigger>
				</Dialog>
			</div>
		</div>
	{/if}

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
							placeholder="البحث في الخدمات..."
							bind:value={searchTerm}
							class="pr-9"
						/>
					</div>
				</div>

				<!-- Filters -->
				<div class="flex items-center space-x-2">
					<Select bind:value={filterStatus}>
						<SelectTrigger class="w-32">
							<SelectValue placeholder="الحالة" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">الكل</SelectItem>
							<SelectItem value="active">نشط</SelectItem>
							<SelectItem value="inactive">غير نشط</SelectItem>
						</SelectContent>
					</Select>

					<Select bind:value={sortBy}>
						<SelectTrigger class="w-32">
							<SelectValue placeholder="ترتيب بـ" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="name">الاسم</SelectItem>
							<SelectItem value="price">السعر</SelectItem>
							<SelectItem value="created_at">التاريخ</SelectItem>
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
			{#if selectedServices.length > 0}
				<div class="mt-4 flex items-center justify-between border-t border-border pt-4">
					<span class="text-sm text-muted-foreground">
						{selectedServices.length} خدمة محددة
					</span>
					<div class="flex items-center space-x-2">
						<Button variant="outline" size="sm" onclick={handleBulkDelete}>
							<Trash2 class="h-4 w-4" />
							حذف المحدد
						</Button>
					</div>
				</div>
			{/if}
		</CardContent>
	</Card>

	<!-- Services Content -->
	{#if appStore.isServicesLoading}
		<div class="grid gap-4 {viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}">
			{#each Array(6) as _}
				<Card class="animate-pulse">
					<CardContent class="p-6">
						<div class="h-4 bg-muted rounded w-3/4 mb-2"></div>
						<div class="h-3 bg-muted rounded w-1/2 mb-4"></div>
						<div class="h-8 bg-muted rounded w-full"></div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{:else if filteredServices.length === 0}
		<Card class="text-center py-12">
			<CardContent>
				<Sparkles class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
				<h3 class="text-lg font-medium mb-2">لا توجد خدمات</h3>
				<p class="text-muted-foreground mb-4">
					{searchTerm ? 'حاول تعديل مصطلحات البحث' : 'ابدأ بإنشاء أول خدمة لك'}
				</p>
				{#if !searchTerm}
					<Button onclick={() => showServiceDialog = true}>
						<Plus class="h-4 w-4" />
						إنشاء خدمة
					</Button>
				{/if}
			</CardContent>
		</Card>
	{:else}
		<!-- Services Grid/List -->
		<div class="grid gap-4 {viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}">
			{#each filteredServices as service (service.id)}
				<Card class="card-premium hover-lift transition-all duration-300 group relative overflow-hidden">
					<!-- Selection Checkbox -->
					<div class="absolute top-4 right-4 z-10">
						<input
							type="checkbox"
							class="rounded border-border"
							bind:group={selectedServices}
							value={service.id}
						/>
					</div>

					<!-- Status Indicator -->
					<div class="absolute top-4 left-4 z-10">
						<Badge variant={service.is_active ? 'success' : 'secondary'}>
							{service.is_active ? 'نشط' : 'غير نشط'}
						</Badge>
					</div>

					<CardContent class="p-6 pt-12">
						<div class="space-y-4">
							<!-- Service Name -->
							<div>
								<h3 class="font-semibold text-lg">{service.name_ar || service.name}</h3>
								{#if service.name_ar && service.name !== service.name_ar}
									<p class="text-sm text-muted-foreground">{service.name}</p>
								{/if}
							</div>

							<!-- Service Details -->
							<div class="space-y-2">
								{#if service.description_ar || service.description}
									<p class="text-sm text-muted-foreground line-clamp-2">
										{service.description_ar || service.description}
									</p>
								{/if}
								
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center space-x-1">
										<Clock class="h-4 w-4 text-muted-foreground" />
										<span>{formatDuration(service.duration)}</span>
									</div>
									<div class="flex items-center space-x-1 font-semibold text-primary">
										<DollarSign class="h-4 w-4" />
										<span>{formatPrice(service.price)}</span>
									</div>
								</div>
							</div>

							<!-- Actions -->
							<div class="flex items-center justify-between pt-4 border-t border-border">
								<div class="flex items-center space-x-1">
									<Button variant="ghost" size="sm" onclick={() => handleEditService(service)}>
										<Edit class="h-4 w-4" />
									</Button>
									<Button variant="ghost" size="sm" onclick={() => handleDuplicateService(service)}>
										<Copy class="h-4 w-4" />
									</Button>
									<Button variant="ghost" size="sm" onclick={() => handleDeleteService(service.id)}>
										<Trash2 class="h-4 w-4" />
									</Button>
								</div>
								
								<Switch
									checked={service.is_active}
									onCheckedChange={(checked) => handleToggleActive(service.id, checked)}
								/>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}

	<!-- Service Form Dialog -->
	<DialogContent class="sm:max-w-2xl">
		<DialogHeader>
			<DialogTitle>
				{editingService ? 'تعديل الخدمة' : 'إنشاء خدمة جديدة'}
			</DialogTitle>
		</DialogHeader>

		<form
			class="space-y-6"
			onsubmit={(e) => {
				e.preventDefault();
				editingService ? handleUpdateService() : handleCreateService();
			}}
		>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Service Name Arabic -->
				<div class="space-y-2">
					<Label for="name_ar">اسم الخدمة (عربي)</Label>
					<Input
						id="name_ar"
						bind:value={serviceForm.name_ar}
						placeholder="مثل: قص شعر"
						dir="rtl"
						required
					/>
				</div>
				
				<!-- Service Name English -->
				<div class="space-y-2">
					<Label for="name">اسم الخدمة (إنجليزي)</Label>
					<Input
						id="name"
						bind:value={serviceForm.name}
						placeholder="e.g., Haircut"
						required
					/>
				</div>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Price -->
				<div class="space-y-2">
					<Label for="price">السعر (ريال سعودي)</Label>
					<Input
						id="price"
						type="number"
						min="0"
						step="0.01"
						bind:value={serviceForm.price}
						required
					/>
				</div>

				<!-- FIXED: Duration with proper time input -->
				<div class="space-y-2">
					<Label for="duration">المدة</Label>
					<Input
						id="duration"
						type="time"
						bind:value={serviceForm.duration}
						required
					/>
				</div>
			</div>

			<!-- Description Arabic -->
			<div class="space-y-2">
				<Label for="description_ar">الوصف (عربي)</Label>
				<Textarea
					id="description_ar"
					bind:value={serviceForm.description_ar}
					placeholder="وصف الخدمة..."
					dir="rtl"
					rows={3}
				/>
			</div>

			<!-- Description English -->
			<div class="space-y-2">
				<Label for="description">الوصف (إنجليزي)</Label>
				<Textarea
					id="description"
					bind:value={serviceForm.description}
					placeholder="Describe your service..."
					rows={3}
				/>
			</div>

			<!-- Active Status -->
			<div class="flex items-center space-x-2">
				<Switch
					id="is_active"
					bind:checked={serviceForm.is_active}
				/>
				<Label for="is_active">خدمة نشطة</Label>
			</div>

			<!-- FIXED: Form Actions with loading states -->
			<div class="flex items-center justify-end space-x-2 pt-4 border-t border-border">
				<Button variant="outline" type="button" onclick={() => showServiceDialog = false}>
					إلغاء
				</Button>
				<Button type="submit" class="btn-premium" disabled={isSubmitting}>
					{isSubmitting ? 'جاري الحفظ...' : editingService ? 'تحديث الخدمة' : 'إنشاء الخدمة'}
				</Button>
			</div>
		</form>
	</DialogContent>
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

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