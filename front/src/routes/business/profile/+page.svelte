<script lang="ts">
/**
 * Business Profile Management - Premium UI/UX with Svelte 5 Runes
 * Comprehensive business profile editing with Leaflet maps, image gallery, QR codes
 * Features: Real-time validation, WhatsApp integration, Saudi market localization
 */
import { onMount, onDestroy } from 'svelte';
import { browser } from '$app/environment';
import { page } from '$app/stores';
import { goto } from '$app/navigation';
import { toast } from 'svelte-sonner';

import * as Card from '$lib/components/ui/card';
import * as Tabs from '$lib/components/ui/tabs';
import { Button } from '$lib/components/ui/button';
import { Input } from '$lib/components/ui/input';
import { Label } from '$lib/components/ui/label';
import { Textarea } from '$lib/components/ui/textarea';
import * as Select from '$lib/components/ui/select';
import { Badge } from '$lib/components/ui/badge';
import * as Dialog from '$lib/components/ui/dialog';
import { Progress } from '$lib/components/ui/progress';

import { 
	Building2, 
	MapPin, 
	Camera, 
	Upload, 
	Download,
	Share2,
	QrCode,
	Star,
	Clock,
	Globe,
	Phone,
	Mail,
	Save,
	RefreshCw,
	Trash2,
	Edit3,
	Eye,
	EyeOff,
	AlertTriangle,
	CheckCircle2,
	XCircle,
	Loader2,
	Copy,
	ExternalLink,
	Settings,
	Crown,
	Zap,
	Shield,
	Heart,
	Award,
	Target,
	TrendingUp,
	Users,
	Calendar,
	MessageCircle,
	Smartphone,
	Palette,
	Languages,
	Navigation,
	Compass,
	Search,
	Filter,
	SortAsc,
	MoreHorizontal,
	Plus,
	X,
	ArrowLeft,
	ArrowRight,
	ChevronDown,
	ChevronUp,
	Info,
	HelpCircle,
	Sparkles,
	ImageIcon,
	FileImage,
	MousePointer,
	Maximize2
} from '@lucide/svelte';

import type { BusinessProfile, ServiceType } from '$lib/types/index.js';
import { api } from '$lib/services/api-client.js';
import { authStore } from '$lib/stores/auth.svelte.js';
import QRCodeDisplay from '$lib/components/qr/QRCodeDisplay.svelte';

// Svelte 5 Runes State Management
let businessProfile = $state<BusinessProfile | null>(null);
let originalProfile = $state<BusinessProfile | null>(null);
let isEditing = $state<boolean>(false);
let isLoading = $state<boolean>(true);
let isSaving = $state<boolean>(false);
let error = $state<string | null>(null);
let activeTab = $state<string>('general');
let uploadProgress = $state<number>(0);
let showQRDialog = $state<boolean>(false);
let selectedImageIndex = $state<number>(0);
let showImageGallery = $state<boolean>(false);
let mapInstance = $state<any>(null);
let locationDetecting = $state<boolean>(false);
let formErrors = $state<Record<string, string>>({});

// Form data states
let formData = $state({
	service_type: '' as ServiceType,
	description: '',
	description_ar: '',
	address: '',
	address_ar: '',
	latitude: null as number | null,
	longitude: null as number | null,
	working_hours: {} as Record<string, any>,
	images: [] as string[],
	is_active: true
});

// Image upload state
let dragOver = $state<boolean>(false);
let uploadingImages = $state<boolean>(false);
let selectedFiles = $state<FileList | null>(null);

// Location state
let currentLocation = $state<{ lat: number; lng: number } | null>(null);
let locationPermission = $state<'granted' | 'denied' | 'prompt' | null>(null);

// Service type options
const serviceTypes = [
	{ value: 'barber', label: 'صالون حلاقة - Barber', icon: '💇‍♂️' },
	{ value: 'salon', label: 'صالون تجميل - Hair Salon', icon: '💇‍♀️' },
	{ value: 'beauty_center', label: 'مركز تجميل - Beauty Center', icon: '💄' },
	{ value: 'car_wash', label: 'غسيل سيارات - Car Wash', icon: '🚗' },
	{ value: 'cleaning', label: 'مركز تنظيف - Cleaning Center', icon: '🧽' },
	{ value: 'gym', label: 'نادي رياضي - Gym', icon: '💪' },
	{ value: 'photographer', label: 'مصور - Photographer', icon: '📸' },
	{ value: 'makeup_artist', label: 'خبير تجميل - Makeup Artist', icon: '🎨' },
	{ value: 'bazar', label: 'بازار - Bazar', icon: '🛍️' },
	{ value: 'events', label: 'فعاليات - Events', icon: '🎉' }
];

// Working hours days
const workingDays = [
	{ key: 'saturday', label: 'السبت', labelEn: 'Saturday' },
	{ key: 'sunday', label: 'الأحد', labelEn: 'Sunday' },
	{ key: 'monday', label: 'الاثنين', labelEn: 'Monday' },
	{ key: 'tuesday', label: 'الثلاثاء', labelEn: 'Tuesday' },
	{ key: 'wednesday', label: 'الأربعاء', labelEn: 'Wednesday' },
	{ key: 'thursday', label: 'الخميس', labelEn: 'Thursday' },
	{ key: 'friday', label: 'الجمعة', labelEn: 'Friday' }
];

// Derived reactive computations
const hasUnsavedChanges = $derived(() => {
	if (!businessProfile || !originalProfile) return false;
	return JSON.stringify(formData) !== JSON.stringify({
		service_type: originalProfile.service_type,
		description: originalProfile.description,
		description_ar: originalProfile.description_ar,
		address: originalProfile.address,
		address_ar: originalProfile.address_ar,
		latitude: originalProfile.latitude,
		longitude: originalProfile.longitude,
		working_hours: originalProfile.working_hours,
		images: originalProfile.images,
		is_active: originalProfile.is_active
	});
});

const isFormValid = $derived(() => {
	return formData.service_type && 
		   formData.address && 
		   Object.keys(formErrors).length === 0;
});

const completionPercentage = $derived(() => {
	if (!businessProfile) return 0;
	
	let completed = 0;
	let total = 10;
	
	// Basic info
	if (formData.service_type) completed++;
	if (formData.description) completed++;
	if (formData.description_ar) completed++;
	
	// Address info
	if (formData.address) completed++;
	if (formData.address_ar) completed++;
	if (formData.latitude && formData.longitude) completed++;
	
	// Working hours
	if (Object.keys(formData.working_hours).length > 0) completed++;
	
	// Images
	if (formData.images.length > 0) completed++;
	
	// Active status
	if (formData.is_active !== undefined) completed++;
	
	// QR code exists
	if (businessProfile.qr_code) completed++;
	
	return Math.round((completed / total) * 100);
});

const profileStrength = $derived(() => {
	const percentage = completionPercentage;
	if (percentage >= 90) return { level: 'ممتاز', color: 'text-emerald-600', bgColor: 'bg-emerald-100' };
	if (percentage >= 70) return { level: 'جيد', color: 'text-blue-600', bgColor: 'bg-blue-100' };
	if (percentage >= 50) return { level: 'متوسط', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
	return { level: 'ضعيف', color: 'text-red-600', bgColor: 'bg-red-100' };
});

// Load business profile data
async function loadBusinessProfile() {
	isLoading = true;
	error = null;

	try {
		const response = await api.business.getBusinessProfile();
		
		if (response.success && response.data) {
			businessProfile = response.data;
			originalProfile = JSON.parse(JSON.stringify(response.data));
			
			// Initialize form data
			formData = {
				service_type: businessProfile.service_type || '',
				description: businessProfile.description || '',
				description_ar: businessProfile.description_ar || '',
				address: businessProfile.address || '',
				address_ar: businessProfile.address_ar || '',
				latitude: businessProfile.latitude,
				longitude: businessProfile.longitude,
				working_hours: businessProfile.working_hours || {},
				images: businessProfile.images || [],
				is_active: businessProfile.is_active
			};

			// Initialize map if coordinates exist
			if (businessProfile.latitude && businessProfile.longitude) {
				currentLocation = { 
					lat: Number(businessProfile.latitude), 
					lng: Number(businessProfile.longitude) 
				};
			}
		} else {
			error = response.error || 'فشل تحميل بيانات الملف التجاري';
		}
	} catch (err: any) {
		error = 'حدث خطأ في الاتصال بالخادم';
		console.error('Business profile load error:', err);
	} finally {
		isLoading = false;
	}
}

// Save business profile
async function saveBusinessProfile() {
	if (!isFormValid) return;

	isSaving = true;
	formErrors = {};

	try {
		const updateData = {
			...formData,
			latitude: formData.latitude ? Number(formData.latitude) : null,
			longitude: formData.longitude ? Number(formData.longitude) : null
		};

		const response = await api.business.updateBusinessProfile(updateData);
		
		if (response.success && response.data) {
			businessProfile = response.data;
			originalProfile = JSON.parse(JSON.stringify(response.data));
			isEditing = false;
			
			toast.success('تم حفظ الملف التجاري بنجاح', {
				description: 'تم تحديث معلومات عملك بنجاح'
			});
		} else {
			if (response.errors) {
				formErrors = response.errors;
			}
			error = response.error || 'فشل حفظ الملف التجاري';
			toast.error('فشل حفظ الملف التجاري', {
				description: error
			});
		}
	} catch (err: any) {
		error = 'حدث خطأ في الاتصال بالخادم';
		toast.error('خطأ في الاتصال', {
			description: 'تعذر الاتصال بالخادم'
		});
		console.error('Business profile save error:', err);
	} finally {
		isSaving = false;
	}
}

// Cancel editing
function cancelEditing() {
	if (hasUnsavedChanges) {
		if (confirm('لديك تغييرات غير محفوظة. هل تريد إلغاء التعديلات؟')) {
			// Reset form data to original
			if (originalProfile) {
				formData = {
					service_type: originalProfile.service_type || '',
					description: originalProfile.description || '',
					description_ar: originalProfile.description_ar || '',
					address: originalProfile.address || '',
					address_ar: originalProfile.address_ar || '',
					latitude: originalProfile.latitude,
					longitude: originalProfile.longitude,
					working_hours: originalProfile.working_hours || {},
					images: originalProfile.images || [],
					is_active: originalProfile.is_active
				};
			}
			isEditing = false;
			formErrors = {};
		}
	} else {
		isEditing = false;
	}
}

// Get current location
async function getCurrentLocation() {
	if (!browser) return;
	
	locationDetecting = true;
	
	try {
		const position = await new Promise<GeolocationPosition>((resolve, reject) => {
			navigator.geolocation.getCurrentPosition(resolve, reject, {
				enableHighAccuracy: true,
				timeout: 10000,
				maximumAge: 300000
			});
		});
		
		const { latitude, longitude } = position.coords;
		formData.latitude = latitude;
		formData.longitude = longitude;
		currentLocation = { lat: latitude, lng: longitude };
		
		// Reverse geocoding to get address
		try {
			const response = await fetch(
				`https://api.mapbox.com/geocoding/v5/mapbox.places/${longitude},${latitude}.json?access_token=YOUR_MAPBOX_TOKEN`
			);
			const data = await response.json();
			
			if (data.features && data.features[0]) {
				const place = data.features[0];
				if (!formData.address) {
					formData.address = place.place_name || '';
				}
			}
		} catch (geocodingError) {
			console.warn('Reverse geocoding failed:', geocodingError);
		}
		
		toast.success('تم تحديد الموقع بنجاح', {
			description: 'تم الحصول على إحداثياتك الحالية'
		});
		
	} catch (error: any) {
		console.error('Location error:', error);
		
		let errorMessage = 'فشل تحديد الموقع';
		if (error.code === 1) {
			errorMessage = 'تم رفض الإذن للوصول للموقع';
			locationPermission = 'denied';
		} else if (error.code === 2) {
			errorMessage = 'الموقع غير متوفر';
		} else if (error.code === 3) {
			errorMessage = 'انتهت مهلة تحديد الموقع';
		}
		
		toast.error('خطأ في تحديد الموقع', {
			description: errorMessage
		});
	} finally {
		locationDetecting = false;
	}
}

// Share location via WhatsApp
function shareLocationWhatsApp() {
	if (!currentLocation) return;
	
	const { lat, lng } = currentLocation;
	const message = encodeURIComponent(
		`موقع عملي: ${formData.address}\n` +
		`https://maps.google.com/maps?q=${lat},${lng}`
	);
	
	const whatsappUrl = `https://wa.me/?text=${message}`;
	window.open(whatsappUrl, '_blank');
}

// Handle file upload
async function handleFileUpload(files: FileList) {
	if (!files || files.length === 0) return;
	
	uploadingImages = true;
	uploadProgress = 0;
	
	try {
		const uploadPromises = Array.from(files).map(async (file, index) => {
			const formData = new FormData();
			formData.append('image', file);
			
			// Simulate upload progress
			const progressInterval = setInterval(() => {
				uploadProgress = Math.min(uploadProgress + 10, 90);
			}, 100);
			
			try {
				const response = await api.business.uploadBusinessImage(formData);
				clearInterval(progressInterval);
				uploadProgress = 100;
				
				if (response.success && response.data) {
					return response.data.image_url;
				}
				throw new Error(response.error || 'Upload failed');
			} catch (error) {
				clearInterval(progressInterval);
				throw error;
			}
		});
		
		const uploadedUrls = await Promise.all(uploadPromises);
		formData.images = [...formData.images, ...uploadedUrls];
		
		toast.success('تم رفع الصور بنجاح', {
			description: `تم رفع ${uploadedUrls.length} صورة`
		});
		
	} catch (error: any) {
		toast.error('فشل رفع الصور', {
			description: error.message || 'حدث خطأ أثناء رفع الصور'
		});
	} finally {
		uploadingImages = false;
		uploadProgress = 0;
	}
}

// Remove image
function removeImage(index: number) {
	if (confirm('هل تريد حذف هذه الصورة؟')) {
		formData.images = formData.images.filter((_, i) => i !== index);
	}
}

// Handle drag and drop
function handleDragOver(event: DragEvent) {
	event.preventDefault();
	dragOver = true;
}

function handleDragLeave(event: DragEvent) {
	event.preventDefault();
	dragOver = false;
}

function handleDrop(event: DragEvent) {
	event.preventDefault();
	dragOver = false;
	
	const files = event.dataTransfer?.files;
	if (files) {
		handleFileUpload(files);
	}
}

// Working hours management
function updateWorkingHours(day: string, field: 'open_time' | 'close_time' | 'is_closed', value: any) {
	if (!formData.working_hours[day]) {
		formData.working_hours[day] = {
			open_time: '09:00',
			close_time: '18:00',
			is_closed: false
		};
	}
	
	formData.working_hours[day][field] = value;
}

// Generate QR Code
async function generateQRCode() {
	if (!businessProfile) return;
	
	try {
		const response = await api.business.generateBusinessQR();
		
		if (response.success && response.data) {
			businessProfile.qr_code = response.data.qr_code_url;
			
			toast.success('تم إنشاء رمز QR بنجاح', {
				description: 'يمكن للعملاء مسح الرمز للوصول لملفك التجاري'
			});
		} else {
			toast.error('فشل إنشاء رمز QR', {
				description: response.error || 'حدث خطأ'
			});
		}
	} catch (error) {
		toast.error('خطأ في إنشاء رمز QR', {
			description: 'تعذر الاتصال بالخادم'
		});
	}
}

// Copy QR URL to clipboard
async function copyQRUrl() {
	if (!businessProfile?.qr_code) return;
	
	try {
		await navigator.clipboard.writeText(businessProfile.qr_code);
		toast.success('تم نسخ رابط رمز QR', {
			description: 'يمكنك الآن مشاركة الرابط مع العملاء'
		});
	} catch (error) {
		toast.error('فشل نسخ الرابط', {
			description: 'تعذر نسخ الرابط للحافظة'
		});
	}
}

// Validate form fields
$effect(() => {
	const errors: Record<string, string> = {};
	
	if (!formData.service_type) {
		errors.service_type = 'نوع الخدمة مطلوب';
	}
	
	if (!formData.address.trim()) {
		errors.address = 'العنوان مطلوب';
	}
	
	if (formData.description && formData.description.length > 1000) {
		errors.description = 'الوصف يجب أن يكون أقل من 1000 حرف';
	}
	
	if (formData.description_ar && formData.description_ar.length > 1000) {
		errors.description_ar = 'الوصف العربي يجب أن يكون أقل من 1000 حرف';
	}
	
	formErrors = errors;
});

// Check location permission on mount
$effect(() => {
	if (browser && navigator.permissions) {
		navigator.permissions.query({ name: 'geolocation' }).then(permission => {
			locationPermission = permission.state;
			
			permission.onchange = () => {
				locationPermission = permission.state;
			};
		});
	}
});

// Load data on mount
onMount(async () => {
	await loadBusinessProfile();
});

// Cleanup
onDestroy(() => {
	if (mapInstance) {
		mapInstance.remove();
	}
});
</script>

<svelte:head>
	<title>إدارة الملف التجاري - Wagtee</title>
	<meta name="description" content="إدارة وتحديث معلومات ملفك التجاري على منصة Wagtee مع الخرائط التفاعلية وإدارة الصور" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950">
	<!-- Header -->
	<header class="sticky top-0 z-50 backdrop-blur-xl bg-white/80 dark:bg-slate-950/80 border-b border-white/20 shadow-lg">
		<div class="container mx-auto px-6 py-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-4">
					<Button variant="ghost" size="sm" onclick={() => goto('/dashboard')} class="glass-button">
						<ArrowLeft class="h-4 w-4 ml-2" />
						العودة للوحة التحكم
					</Button>
					
					<div class="space-y-1">
						<h1 class="text-2xl font-black bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
							إدارة الملف التجاري
						</h1>
						<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">
							Business Profile Management
						</p>
					</div>
				</div>

				<div class="flex items-center gap-3">
					<!-- Profile Completion -->
					<div class="flex items-center gap-3 rounded-full bg-white/60 dark:bg-slate-800/60 px-4 py-2 backdrop-blur-sm border border-white/20">
						<div class="relative h-8 w-8">
							<svg class="h-full w-full transform -rotate-90" viewBox="0 0 36 36">
								<path
									class="text-slate-200 dark:text-slate-700"
									stroke="currentColor"
									stroke-width="3"
									fill="none"
									d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
								/>
								<path
									class="{profileStrength.color} transition-all duration-700"
									stroke="currentColor"
									stroke-width="3"
									stroke-linecap="round"
									fill="none"
									stroke-dasharray="{completionPercentage}, 100"
									d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
								/>
							</svg>
							<div class="absolute inset-0 flex items-center justify-center">
								<span class="text-xs font-bold {profileStrength.color}">
									{completionPercentage}%
								</span>
							</div>
						</div>
						<div class="space-y-0.5">
							<p class="text-xs font-semibold text-slate-600 dark:text-slate-400">مستوى الملف</p>
							<Badge class="{profileStrength.bgColor} {profileStrength.color} text-xs">
								{profileStrength.level}
							</Badge>
						</div>
					</div>

					<!-- Action Buttons -->
					{#if isEditing}
						<Button
							variant="outline"
							size="sm"
							onclick={cancelEditing}
							disabled={isSaving}
							class="glass-button"
						>
							<X class="h-4 w-4 ml-2" />
							إلغاء
						</Button>
						
						<Button
							onclick={saveBusinessProfile}
							disabled={isSaving || !isFormValid}
							size="sm"
							class="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg"
						>
							{#if isSaving}
								<Loader2 class="h-4 w-4 ml-2 animate-spin" />
								جار الحفظ...
							{:else}
								<Save class="h-4 w-4 ml-2" />
								حفظ التغييرات
							{/if}
						</Button>
					{:else}
						<Button
							onclick={() => isEditing = true}
							size="sm"
							class="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 shadow-lg"
						>
							<Edit3 class="h-4 w-4 ml-2" />
							تعديل الملف
						</Button>
					{/if}
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="container mx-auto px-6 py-8">
		{#if isLoading}
			<!-- Premium Loading State -->
			<div class="flex items-center justify-center py-20">
				<Card.Root class="glass-card border-white/20 shadow-2xl backdrop-blur-xl">
					<Card.Content class="p-12">
						<div class="space-y-6 text-center">
							<div class="relative">
								<div class="h-16 w-16 mx-auto">
									<div class="absolute inset-0 rounded-full border-4 border-blue-200 dark:border-blue-800/30"></div>
									<div class="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 animate-spin"></div>
									<div class="absolute inset-2 rounded-full border-4 border-transparent border-t-indigo-500 animate-spin animation-delay-200"></div>
								</div>
								<div class="absolute inset-0 rounded-full bg-gradient-to-r from-blue-400 to-indigo-500 opacity-20 blur-xl animate-pulse mx-auto h-16 w-16"></div>
							</div>
							
							<div class="space-y-3">
								<h3 class="text-xl font-bold text-slate-800 dark:text-slate-200">
									جار تحميل الملف التجاري
								</h3>
								<p class="text-slate-600 dark:text-slate-400 font-medium">
									يرجى الانتظار بينما نقوم بتحميل معلومات عملك...
								</p>
							</div>
						</div>
					</Card.Content>
				</Card.Root>
			</div>
		{:else if error}
			<!-- Premium Error State -->
			<div class="flex items-center justify-center py-20">
				<Card.Root class="glass-card max-w-lg border-red-200/30 shadow-2xl backdrop-blur-xl">
					<Card.Content class="p-12">
						<div class="space-y-6 text-center">
							<div class="relative">
								<div class="mx-auto h-20 w-20 rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-950 dark:to-red-900 flex items-center justify-center shadow-inner">
									<AlertTriangle class="h-10 w-10 text-red-600 dark:text-red-400" />
								</div>
								<div class="absolute inset-0 mx-auto h-20 w-20 rounded-full bg-red-500 opacity-10 blur-xl animate-pulse"></div>
							</div>
							
							<div class="space-y-3">
								<h3 class="text-xl font-bold text-slate-800 dark:text-slate-200">حدث خطأ</h3>
								<p class="text-slate-600 dark:text-slate-400 font-medium">{error}</p>
							</div>
							
							<Button 
								variant="default"
								onclick={loadBusinessProfile}
								class="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg"
							>
								<RefreshCw class="h-4 w-4 ml-2" />
								إعادة المحاولة
							</Button>
						</div>
					</Card.Content>
				</Card.Root>
			</div>
		{:else if businessProfile}
			<!-- Business Profile Content -->
			<div class="space-y-8">
				<!-- Quick Stats & Actions Row -->
				<div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
					<!-- Profile Status Card -->
					<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl group hover:shadow-2xl transition-all duration-500">
						<Card.Content class="p-6">
							<div class="flex items-center justify-between mb-4">
								<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900">
									<Shield class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
								</div>
								<Badge variant="outline" class="border-emerald-200 text-emerald-700 dark:border-emerald-800 dark:text-emerald-300">
									{formData.is_active ? 'نشط' : 'غير نشط'}
								</Badge>
							</div>
							<div class="space-y-2">
								<h3 class="text-lg font-black text-slate-800 dark:text-slate-200">
									حالة الملف
								</h3>
								<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">
									{formData.is_active ? 'ملف تجاري نشط' : 'ملف تجاري متوقف'}
								</p>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- Service Type Card -->
					<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl group hover:shadow-2xl transition-all duration-500">
						<Card.Content class="p-6">
							<div class="flex items-center justify-between mb-4">
								<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-950 dark:to-blue-900">
									<Building2 class="h-6 w-6 text-blue-600 dark:text-blue-400" />
								</div>
								<span class="text-2xl">
									{serviceTypes.find(t => t.value === formData.service_type)?.icon || '🏢'}
								</span>
							</div>
							<div class="space-y-2">
								<h3 class="text-lg font-black text-slate-800 dark:text-slate-200">
									نوع الخدمة
								</h3>
								<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">
									{serviceTypes.find(t => t.value === formData.service_type)?.label || 'غير محدد'}
								</p>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- Rating Card -->
					<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl group hover:shadow-2xl transition-all duration-500">
						<Card.Content class="p-6">
							<div class="flex items-center justify-between mb-4">
								<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-950 dark:to-amber-900">
									<Star class="h-6 w-6 text-amber-600 dark:text-amber-400 fill-current" />
								</div>
								<div class="flex items-center gap-1">
									{#each Array(5) as _, i}
										<Star class="h-4 w-4 {i < Math.floor(businessProfile.rating) ? 'text-amber-500 fill-current' : 'text-slate-300 dark:text-slate-600'}" />
									{/each}
								</div>
							</div>
							<div class="space-y-2">
								<h3 class="text-lg font-black text-slate-800 dark:text-slate-200">
									{businessProfile.rating.toFixed(1)}
								</h3>
								<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">تقييم العملاء</p>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- QR Code Action Card -->
					<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl group hover:shadow-2xl transition-all duration-500 cursor-pointer"
						onclick={() => showQRDialog = true}>
						<Card.Content class="p-6">
							<div class="flex items-center justify-between mb-4">
								<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900">
									<QrCode class="h-6 w-6 text-purple-600 dark:text-purple-400" />
								</div>
								<Badge variant="outline" class="border-purple-200 text-purple-700 dark:border-purple-800 dark:text-purple-300">
									{businessProfile.qr_code ? 'متوفر' : 'إنشاء'}
								</Badge>
							</div>
							<div class="space-y-2">
								<h3 class="text-lg font-black text-slate-800 dark:text-slate-200">
									رمز QR
								</h3>
								<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">
									{businessProfile.qr_code ? 'مشاهدة الرمز' : 'إنشاء رمز جديد'}
								</p>
							</div>
						</Card.Content>
					</Card.Root>
				</div>

				<!-- Main Profile Form -->
				<Tabs.Root bind:value={activeTab} class="space-y-8">
					<Tabs.List class="grid w-full grid-cols-4 gap-2 rounded-xl bg-white/60 dark:bg-slate-800/60 p-2 backdrop-blur-sm border border-white/20">
						<Tabs.Trigger value="general" class="glass-tab">
							<Building2 class="h-4 w-4 ml-2" />
							معلومات عامة
						</Tabs.Trigger>
						<Tabs.Trigger value="location" class="glass-tab">
							<MapPin class="h-4 w-4 ml-2" />
							الموقع والخرائط
						</Tabs.Trigger>
						<Tabs.Trigger value="schedule" class="glass-tab">
							<Clock class="h-4 w-4 ml-2" />
							ساعات العمل
						</Tabs.Trigger>
						<Tabs.Trigger value="gallery" class="glass-tab">
							<Camera class="h-4 w-4 ml-2" />
							معرض الصور
						</Tabs.Trigger>
					</Tabs.List>

					<!-- General Information Tab -->
					<Tabs.Content value="general" class="space-y-6">
						<Card.Root class="glass-card border-white/20 shadow-2xl backdrop-blur-xl">
							<Card.Header class="pb-6">
								<Card.Title class="flex items-center gap-3 text-xl font-bold">
									<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-100 to-indigo-200 dark:from-blue-950 dark:to-indigo-900">
										<Building2 class="h-6 w-6 text-blue-600 dark:text-blue-400" />
									</div>
									المعلومات الأساسية
								</Card.Title>
								<Card.Description class="text-slate-600 dark:text-slate-400 font-medium">
									إدارة معلومات عملك الأساسية ووصف الخدمات المقدمة
								</Card.Description>
							</Card.Header>
							<Card.Content class="space-y-6">
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									<!-- Service Type Selection -->
									<div class="space-y-3">
										<Label for="service_type" class="text-sm font-bold text-slate-700 dark:text-slate-300">
											نوع الخدمة *
										</Label>
										<Select.Root 
											bind:selected={formData.service_type} 
											disabled={!isEditing}
										>
											<Select.Trigger class="glass-input">
												<Select.Value placeholder="اختر نوع الخدمة" />
											</Select.Trigger>
											<Select.Content class="glass-dropdown">
												{#each serviceTypes as serviceType}
													<Select.Item value={serviceType.value} class="flex items-center gap-3">
														<span class="text-lg">{serviceType.icon}</span>
														<span class="font-medium">{serviceType.label}</span>
													</Select.Item>
												{/each}
											</Select.Content>
										</Select.Root>
										{#if formErrors.service_type}
											<p class="text-sm text-red-600 font-semibold flex items-center gap-2">
												<AlertTriangle class="h-4 w-4" />
												{formErrors.service_type}
											</p>
										{/if}
									</div>

									<!-- Business Status -->
									<div class="space-y-3">
										<Label class="text-sm font-bold text-slate-700 dark:text-slate-300">
											حالة النشاط
										</Label>
										<div class="flex items-center gap-4">
											<div class="flex items-center space-x-2">
												<input 
													id="active"
													type="radio" 
													bind:group={formData.is_active} 
													value={true}
													disabled={!isEditing}
													class="glass-radio" 
												/>
												<Label for="active" class="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
													نشط
												</Label>
											</div>
											<div class="flex items-center space-x-2">
												<input 
													id="inactive"
													type="radio" 
													bind:group={formData.is_active} 
													value={false}
													disabled={!isEditing}
													class="glass-radio" 
												/>
												<Label for="inactive" class="text-sm font-semibold text-red-700 dark:text-red-300">
													غير نشط
												</Label>
											</div>
										</div>
									</div>
								</div>

								<!-- Description Fields -->
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									<!-- English Description -->
									<div class="space-y-3">
										<Label for="description" class="text-sm font-bold text-slate-700 dark:text-slate-300">
											وصف الخدمات (English)
										</Label>
										<Textarea
											id="description"
											bind:value={formData.description}
											placeholder="Describe your business services in English..."
											disabled={!isEditing}
											rows={6}
											class="glass-input"
										/>
										{#if formErrors.description}
											<p class="text-sm text-red-600 font-semibold flex items-center gap-2">
												<AlertTriangle class="h-4 w-4" />
												{formErrors.description}
											</p>
										{/if}
										<p class="text-xs text-slate-500 dark:text-slate-400">
											{formData.description.length}/1000 حرف
										</p>
									</div>

									<!-- Arabic Description -->
									<div class="space-y-3">
										<Label for="description_ar" class="text-sm font-bold text-slate-700 dark:text-slate-300">
											وصف الخدمات (العربية)
										</Label>
										<Textarea
											id="description_ar"
											bind:value={formData.description_ar}
											placeholder="اكتب وصفًا مفصلاً عن خدماتك باللغة العربية..."
											disabled={!isEditing}
											rows={6}
											class="glass-input text-right"
											dir="rtl"
										/>
										{#if formErrors.description_ar}
											<p class="text-sm text-red-600 font-semibold flex items-center gap-2">
												<AlertTriangle class="h-4 w-4" />
												{formErrors.description_ar}
											</p>
										{/if}
										<p class="text-xs text-slate-500 dark:text-slate-400">
											{formData.description_ar.length}/1000 حرف
										</p>
									</div>
								</div>
							</Card.Content>
						</Card.Root>
					</Tabs.Content>

					<!-- Location Tab -->
					<Tabs.Content value="location" class="space-y-6">
						<Card.Root class="glass-card border-white/20 shadow-2xl backdrop-blur-xl">
							<Card.Header class="pb-6">
								<Card.Title class="flex items-center gap-3 text-xl font-bold">
									<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-950 dark:to-emerald-900">
										<MapPin class="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
									</div>
									الموقع والعنوان
								</Card.Title>
								<Card.Description class="text-slate-600 dark:text-slate-400 font-medium">
									حدد موقع عملك بدقة لتسهيل وصول العملاء إليك
								</Card.Description>
							</Card.Header>
							<Card.Content class="space-y-6">
								<!-- Location Detection -->
								<div class="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200/50 dark:border-blue-800/50">
									<div class="flex items-center gap-3">
										<Navigation class="h-5 w-5 text-blue-600 dark:text-blue-400" />
										<div>
											<h4 class="font-bold text-blue-800 dark:text-blue-200">تحديد الموقع التلقائي</h4>
											<p class="text-sm text-blue-700 dark:text-blue-300">
												{locationPermission === 'granted' ? 'مُتاح' : locationPermission === 'denied' ? 'مرفوض' : 'غير محدد'}
											</p>
										</div>
									</div>
									
									<div class="flex items-center gap-2">
										{#if currentLocation}
											<Button
												variant="outline"
												size="sm"
												onclick={shareLocationWhatsApp}
												class="glass-button"
											>
												<Smartphone class="h-4 w-4 ml-2" />
												مشاركة في واتساب
											</Button>
										{/if}
										
										<Button
											onclick={getCurrentLocation}
											disabled={locationDetecting || !isEditing}
											size="sm"
											class="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
										>
											{#if locationDetecting}
												<Loader2 class="h-4 w-4 ml-2 animate-spin" />
												جار التحديد...
											{:else}
												<Compass class="h-4 w-4 ml-2" />
												تحديد موقعي
											{/if}
										</Button>
									</div>
								</div>

								<!-- Address Fields -->
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									<!-- English Address -->
									<div class="space-y-3">
										<Label for="address" class="text-sm font-bold text-slate-700 dark:text-slate-300">
											العنوان (English) *
										</Label>
										<Textarea
											id="address"
											bind:value={formData.address}
											placeholder="Enter your business address in English..."
											disabled={!isEditing}
											rows={4}
											class="glass-input"
										/>
										{#if formErrors.address}
											<p class="text-sm text-red-600 font-semibold flex items-center gap-2">
												<AlertTriangle class="h-4 w-4" />
												{formErrors.address}
											</p>
										{/if}
									</div>

									<!-- Arabic Address -->
									<div class="space-y-3">
										<Label for="address_ar" class="text-sm font-bold text-slate-700 dark:text-slate-300">
											العنوان (العربية)
										</Label>
										<Textarea
											id="address_ar"
											bind:value={formData.address_ar}
											placeholder="أدخل عنوان عملك باللغة العربية..."
											disabled={!isEditing}
											rows={4}
											class="glass-input text-right"
											dir="rtl"
										/>
									</div>
								</div>

								<!-- Coordinates -->
								{#if formData.latitude && formData.longitude}
									<div class="grid grid-cols-2 gap-6">
										<div class="space-y-3">
											<Label class="text-sm font-bold text-slate-700 dark:text-slate-300">
												خط العرض (Latitude)
											</Label>
											<Input
												bind:value={formData.latitude}
												type="number"
												step="any"
												disabled={!isEditing}
												class="glass-input"
											/>
										</div>
										
										<div class="space-y-3">
											<Label class="text-sm font-bold text-slate-700 dark:text-slate-300">
												خط الطول (Longitude)
											</Label>
											<Input
												bind:value={formData.longitude}
												type="number"
												step="any"
												disabled={!isEditing}
												class="glass-input"
											/>
										</div>
									</div>
								{/if}

								<!-- Map Placeholder -->
								<div class="relative h-80 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border border-slate-200 dark:border-slate-700 overflow-hidden">
									<div class="p-6 h-full flex items-center justify-center">
										<div class="text-center space-y-4">
											<div class="relative">
												<MapPin class="h-16 w-16 mx-auto text-slate-400 dark:text-slate-500" />
												<div class="absolute inset-0 h-16 w-16 mx-auto rounded-full bg-emerald-500/20 blur-xl animate-pulse"></div>
											</div>
											<div>
												<p class="text-lg font-bold text-slate-600 dark:text-slate-400 mb-2">
													خريطة تفاعلية
												</p>
												<p class="text-sm text-slate-500 dark:text-slate-500">
													يتطلب تكامل مكتبة الخرائط (Leaflet.js)
												</p>
											</div>
											
											{#if currentLocation}
												<Badge class="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
													الموقع محدد: {currentLocation.lat.toFixed(6)}, {currentLocation.lng.toFixed(6)}
												</Badge>
											{/if}
										</div>
									</div>
								</div>
							</Card.Content>
						</Card.Root>
					</Tabs.Content>

					<!-- Working Hours Tab -->
					<Tabs.Content value="schedule" class="space-y-6">
						<Card.Root class="glass-card border-white/20 shadow-2xl backdrop-blur-xl">
							<Card.Header class="pb-6">
								<Card.Title class="flex items-center gap-3 text-xl font-bold">
									<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-950 dark:to-amber-900">
										<Clock class="h-6 w-6 text-amber-600 dark:text-amber-400" />
									</div>
									ساعات العمل
								</Card.Title>
								<Card.Description class="text-slate-600 dark:text-slate-400 font-medium">
									حدد أوقات عمل منشأتك لكل يوم من أيام الأسبوع
								</Card.Description>
							</Card.Header>
							<Card.Content class="space-y-6">
								<div class="space-y-4">
									{#each workingDays as day}
										<div class="flex items-center gap-6 p-4 rounded-xl bg-gradient-to-r from-white/50 to-white/30 dark:from-slate-800/50 dark:to-slate-800/30 border border-white/30 dark:border-slate-700/30 backdrop-blur-sm">
											<div class="flex items-center gap-3 w-32">
												<Calendar class="h-5 w-5 text-slate-500 dark:text-slate-400" />
												<div>
													<p class="font-bold text-slate-800 dark:text-slate-200">{day.label}</p>
													<p class="text-xs text-slate-500 dark:text-slate-400">{day.labelEn}</p>
												</div>
											</div>
											
											{#if formData.working_hours[day.key]?.is_closed}
												<div class="flex items-center gap-3 flex-1">
													<Badge class="bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">
														مغلق
													</Badge>
													<Button
														variant="outline"
														size="sm"
														onclick={() => updateWorkingHours(day.key, 'is_closed', false)}
														disabled={!isEditing}
														class="glass-button"
													>
														<Eye class="h-4 w-4 ml-2" />
														فتح
													</Button>
												</div>
											{:else}
												<div class="flex items-center gap-4 flex-1">
													<div class="flex items-center gap-2">
														<Label class="text-sm font-semibold text-slate-600 dark:text-slate-400">من:</Label>
														<Input
															type="time"
															value={formData.working_hours[day.key]?.open_time || '09:00'}
															onchange={(e) => updateWorkingHours(day.key, 'open_time', e.target.value)}
															disabled={!isEditing}
															class="glass-input w-32"
														/>
													</div>
													
													<div class="flex items-center gap-2">
														<Label class="text-sm font-semibold text-slate-600 dark:text-slate-400">إلى:</Label>
														<Input
															type="time"
															value={formData.working_hours[day.key]?.close_time || '18:00'}
															onchange={(e) => updateWorkingHours(day.key, 'close_time', e.target.value)}
															disabled={!isEditing}
															class="glass-input w-32"
														/>
													</div>
													
													<Button
														variant="outline"
														size="sm"
														onclick={() => updateWorkingHours(day.key, 'is_closed', true)}
														disabled={!isEditing}
														class="glass-button"
													>
														<EyeOff class="h-4 w-4 ml-2" />
														إغلاق
													</Button>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</Card.Content>
						</Card.Root>
					</Tabs.Content>

					<!-- Gallery Tab -->
					<Tabs.Content value="gallery" class="space-y-6">
						<Card.Root class="glass-card border-white/20 shadow-2xl backdrop-blur-xl">
							<Card.Header class="pb-6">
								<Card.Title class="flex items-center gap-3 text-xl font-bold">
									<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900">
										<Camera class="h-6 w-6 text-purple-600 dark:text-purple-400" />
									</div>
									معرض الصور
								</Card.Title>
								<Card.Description class="text-slate-600 dark:text-slate-400 font-medium">
									أضف صور جذابة لعملك لتشجيع العملاء على الحجز
								</Card.Description>
							</Card.Header>
							<Card.Content class="space-y-6">
								<!-- Upload Area -->
								{#if isEditing}
									<div 
										class="relative p-8 border-2 border-dashed rounded-xl transition-all duration-300 {dragOver ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/30' : 'border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/50'}"
										on:dragover={handleDragOver}
										on:dragleave={handleDragLeave}
										on:drop={handleDrop}
									>
										<input
											type="file"
											accept="image/*"
											multiple
											class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
											onchange={(e) => e.target.files && handleFileUpload(e.target.files)}
										/>
										
										<div class="text-center space-y-4">
											{#if uploadingImages}
												<div class="space-y-4">
													<Loader2 class="h-12 w-12 mx-auto text-blue-500 animate-spin" />
													<div class="space-y-2">
														<p class="text-lg font-bold text-blue-700 dark:text-blue-300">
															جار رفع الصور...
														</p>
														<Progress value={uploadProgress} class="max-w-xs mx-auto" />
														<p class="text-sm text-blue-600 dark:text-blue-400">
															{uploadProgress}%
														</p>
													</div>
												</div>
											{:else}
												<div class="space-y-3">
													<Upload class="h-12 w-12 mx-auto text-slate-400 dark:text-slate-500" />
													<div>
														<h4 class="text-lg font-bold text-slate-700 dark:text-slate-300">
															اسحب الصور هنا أو اضغط للاختيار
														</h4>
														<p class="text-sm text-slate-500 dark:text-slate-400">
															PNG, JPG, JPEG حتى 10MB لكل صورة
														</p>
													</div>
													<Button variant="outline" class="glass-button">
														<FileImage class="h-4 w-4 ml-2" />
														اختيار الصور
													</Button>
												</div>
											{/if}
										</div>
									</div>
								{/if}

								<!-- Images Grid -->
								{#if formData.images && formData.images.length > 0}
									<div class="space-y-4">
										<div class="flex items-center justify-between">
											<h4 class="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
												<ImageIcon class="h-5 w-5" />
												الصور المرفوعة ({formData.images.length})
											</h4>
											
											{#if isEditing}
												<Button
													variant="outline"
													size="sm"
													onclick={() => showImageGallery = true}
													class="glass-button"
												>
													<Eye class="h-4 w-4 ml-2" />
													معاينة
												</Button>
											{/if}
										</div>
										
										<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
											{#each formData.images as image, index}
												<div class="group relative aspect-square rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
													<img 
														src={image} 
														alt="Business image {index + 1}"
														class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
														loading="lazy"
													/>
													
													{#if isEditing}
														<div class="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-colors duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
															<div class="flex items-center gap-2">
																<Button
																	variant="ghost"
																	size="sm"
																	onclick={() => {
																		selectedImageIndex = index;
																		showImageGallery = true;
																	}}
																	class="bg-white/20 hover:bg-white/30 text-white border-white/20"
																>
																	<Eye class="h-4 w-4" />
																</Button>
																<Button
																	variant="ghost"
																	size="sm"
																	onclick={() => removeImage(index)}
																	class="bg-red-500/20 hover:bg-red-500/30 text-white border-red-500/20"
																>
																	<Trash2 class="h-4 w-4" />
																</Button>
															</div>
														</div>
													{/if}
												</div>
											{/each}
										</div>
									</div>
								{:else}
									<div class="text-center py-12 space-y-4">
										<ImageIcon class="h-16 w-16 mx-auto text-slate-300 dark:text-slate-600" />
										<div>
											<h4 class="text-lg font-bold text-slate-600 dark:text-slate-400">
												لا توجد صور
											</h4>
											<p class="text-sm text-slate-500 dark:text-slate-500">
												أضف صور جذابة لعملك لجذب المزيد من العملاء
											</p>
										</div>
									</div>
								{/if}
							</Card.Content>
						</Card.Root>
					</Tabs.Content>
				</Tabs.Root>
			</div>
		{/if}
	</main>
</div>

<!-- QR Code Dialog -->
{#if businessProfile}
	<Dialog.Root bind:open={showQRDialog}>
		<Dialog.Content class="glass-card max-w-md">
			<Dialog.Header>
				<Dialog.Title class="flex items-center gap-3">
					<QrCode class="h-6 w-6 text-purple-600" />
					رمز QR للملف التجاري
				</Dialog.Title>
				<Dialog.Description>
					يمكن للعملاء مسح هذا الرمز للوصول السريع إلى ملفك التجاري وحجز المواعيد
				</Dialog.Description>
			</Dialog.Header>
			
			<div class="space-y-6">
				{#if businessProfile.qr_code}
					<div class="text-center space-y-4">
						<QRCodeDisplay 
							value={`${window.location.origin}/qr/business/${businessProfile.id}`}
							size={200}
						/>
						
						<div class="space-y-2">
							<p class="text-sm font-semibold text-slate-600 dark:text-slate-400">
								رابط الملف التجاري
							</p>
							<div class="flex items-center gap-2">
								<Input
									value={`${window.location.origin}/qr/business/${businessProfile.id}`}
									readonly
									class="glass-input text-xs"
								/>
								<Button
									variant="outline"
									size="sm"
									onclick={copyQRUrl}
									class="glass-button"
								>
									<Copy class="h-4 w-4" />
								</Button>
							</div>
						</div>
					</div>
					
					<div class="flex gap-3">
						<Button
							variant="outline"
							onclick={() => window.open(`${window.location.origin}/qr/business/${businessProfile.id}`, '_blank')}
							class="glass-button flex-1"
						>
							<ExternalLink class="h-4 w-4 ml-2" />
							معاينة
						</Button>
						<Button
							onclick={copyQRUrl}
							class="bg-gradient-to-r from-purple-500 to-indigo-600 flex-1"
						>
							<Share2 class="h-4 w-4 ml-2" />
							مشاركة
						</Button>
					</div>
				{:else}
					<div class="text-center space-y-4">
						<div class="mx-auto h-32 w-32 rounded-xl bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-950 dark:to-purple-900 flex items-center justify-center">
							<QrCode class="h-16 w-16 text-purple-600 dark:text-purple-400" />
						</div>
						
						<div class="space-y-2">
							<h4 class="text-lg font-bold text-slate-800 dark:text-slate-200">
								لم يتم إنشاء رمز QR بعد
							</h4>
							<p class="text-sm text-slate-600 dark:text-slate-400">
								انقر لإنشاء رمز QR جديد لملفك التجاري
							</p>
						</div>
						
						<Button
							onclick={generateQRCode}
							class="bg-gradient-to-r from-purple-500 to-indigo-600"
						>
							<Plus class="h-4 w-4 ml-2" />
							إنشاء رمز QR
						</Button>
					</div>
				{/if}
			</div>
		</Dialog.Content>
	</Dialog.Root>
{/if}

<!-- Image Gallery Dialog -->
<Dialog.Root bind:open={showImageGallery}>
	<Dialog.Content class="glass-card max-w-4xl max-h-[90vh] overflow-hidden">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-3">
				<ImageIcon class="h-6 w-6 text-purple-600" />
				معرض صور العمل
			</Dialog.Title>
		</Dialog.Header>
		
		{#if formData.images && formData.images.length > 0}
			<div class="space-y-4">
				<!-- Main Image Display -->
				<div class="relative aspect-video rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800">
					<img 
						src={formData.images[selectedImageIndex]} 
						alt="Business image {selectedImageIndex + 1}"
						class="w-full h-full object-contain"
					/>
					
					<!-- Navigation Arrows -->
					{#if formData.images.length > 1}
						<Button
							variant="ghost"
							size="sm"
							onclick={() => selectedImageIndex = (selectedImageIndex - 1 + formData.images.length) % formData.images.length}
							class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/20 hover:bg-black/30 text-white"
						>
							<ArrowLeft class="h-5 w-5" />
						</Button>
						
						<Button
							variant="ghost"
							size="sm"
							onclick={() => selectedImageIndex = (selectedImageIndex + 1) % formData.images.length}
							class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/20 hover:bg-black/30 text-white"
						>
							<ArrowRight class="h-5 w-5" />
						</Button>
					{/if}
				</div>
				
				<!-- Thumbnail Navigation -->
				{#if formData.images.length > 1}
					<div class="grid grid-cols-6 gap-2 max-h-24 overflow-y-auto">
						{#each formData.images as image, index}
							<button
								onclick={() => selectedImageIndex = index}
								class="aspect-square rounded-lg overflow-hidden border-2 transition-colors {selectedImageIndex === index ? 'border-purple-500' : 'border-slate-200 dark:border-slate-700'}"
							>
								<img 
									src={image} 
									alt="Thumbnail {index + 1}"
									class="w-full h-full object-cover"
								/>
							</button>
						{/each}
					</div>
				{/if}
				
				<!-- Image Counter -->
				<div class="text-center">
					<p class="text-sm text-slate-500 dark:text-slate-400">
						{selectedImageIndex + 1} من {formData.images.length}
					</p>
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<style>
	/* Premium Glassmorphism Effects */
	:global(.glass-card) {
		background: rgba(255, 255, 255, 0.25);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border: 1px solid rgba(255, 255, 255, 0.18);
		box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
	}

	:global(.dark .glass-card) {
		background: rgba(15, 23, 42, 0.25);
		border: 1px solid rgba(255, 255, 255, 0.05);
		box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
	}

	:global(.glass-button) {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all 0.3s ease;
	}

	:global(.glass-button:hover) {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
		box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
	}

	:global(.dark .glass-button) {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	:global(.dark .glass-button:hover) {
		background: rgba(255, 255, 255, 0.1);
	}

	:global(.glass-input) {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	:global(.dark .glass-input) {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	:global(.glass-tab) {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all 0.3s ease;
	}

	:global(.glass-tab[data-state="active"]) {
		background: rgba(59, 130, 246, 0.2);
		border-color: rgba(59, 130, 246, 0.3);
	}

	:global(.glass-dropdown) {
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	:global(.dark .glass-dropdown) {
		background: rgba(15, 23, 42, 0.95);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	:global(.glass-radio) {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 2px solid rgba(255, 255, 255, 0.2);
	}

	.animation-delay-200 {
		animation-delay: 200ms;
	}

	/* RTL Support */
	:global([dir="rtl"]) .glass-card {
		text-align: right;
	}
</style>