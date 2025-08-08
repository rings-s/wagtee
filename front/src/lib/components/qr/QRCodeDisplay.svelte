<!--
  QR Code Display Component - Saudi Market Integration
  Display and manage QR codes for business, services, and bookings
-->
<script lang="ts">
import { browser } from '$app/environment';
import { Download, Copy, Share2, RefreshCw, QrCode, Eye, ExternalLink } from '@lucide/svelte';
import { Button } from '$lib/components/ui/button';
import { Badge } from '$lib/components/ui/badge';
import * as Card from '$lib/components/ui/card';
import { toast } from 'svelte-sonner';

// Props using Svelte 5 $props rune
interface Props {
	qrCodeUrl?: string;
	qrCodeData?: string;
	title?: string;
	subtitle?: string;
	type?: 'business' | 'service' | 'booking';
	size?: 'sm' | 'md' | 'lg' | 'xl';
	showControls?: boolean;
	showPreview?: boolean;
	businessId?: number;
	serviceId?: number;
	bookingId?: string;
	containerClass?: string;
}

const {
	qrCodeUrl,
	qrCodeData,
	title,
	subtitle,
	type = 'business',
	size = 'md',
	showControls = true,
	showPreview = false,
	businessId,
	serviceId,
	bookingId,
	containerClass = ''
}: Props = $props();

// Svelte 5 runes for reactive state
let qrImageElement = $state<HTMLImageElement>();
let isLoading = $state<boolean>(false);
let error = $state<string | null>(null);
let previewUrl = $state<string | null>(null);

// Derived reactive values
const qrDisplayUrl = $derived(() => qrCodeUrl || previewUrl);
const sizeClasses = $derived(() => {
	const sizes = {
		sm: 'w-24 h-24',
		md: 'w-32 h-32',
		lg: 'w-48 h-48',
		xl: 'w-64 h-64'
	};
	return sizes[size];
});

const typeConfig = $derived(() => {
	const configs = {
		business: {
			label: 'رمز المؤسسة',
			description: 'للوصول السريع لصفحة الحجز',
			color: 'text-blue-600 dark:text-blue-400',
			bgColor: 'bg-blue-100 dark:bg-blue-900/30',
			icon: QrCode
		},
		service: {
			label: 'رمز الخدمة',
			description: 'للحجز المباشر لهذه الخدمة',
			color: 'text-purple-600 dark:text-purple-400',
			bgColor: 'bg-purple-100 dark:bg-purple-900/30',
			icon: QrCode
		},
		booking: {
			label: 'رمز الحجز',
			description: 'للوصول لتفاصيل الحجز',
			color: 'text-green-600 dark:text-green-400',
			bgColor: 'bg-green-100 dark:bg-green-900/30',
			icon: QrCode
		}
	};
	return configs[type];
});

// Generate QR code if data is provided but URL is not
async function generateQRCode() {
	if (!qrCodeData || qrDisplayUrl) return;
	
	try {
		isLoading = true;
		error = null;
		
		// Using QR Server API for generation (fallback)
		const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=${encodeURIComponent(qrCodeData)}&format=png&bgcolor=ffffff&color=000000&margin=10`;
		previewUrl = qrUrl;
		
	} catch (err) {
		error = 'فشل في إنشاء رمز QR';
		console.error('QR generation error:', err);
	} finally {
		isLoading = false;
	}
}

// Download QR code as image
async function downloadQRCode() {
	if (!qrDisplayUrl) return;
	
	try {
		const response = await fetch(qrDisplayUrl);
		const blob = await response.blob();
		const url = window.URL.createObjectURL(blob);
		
		const link = document.createElement('a');
		link.href = url;
		link.download = `wagtee-qr-${type}-${Date.now()}.png`;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		window.URL.revokeObjectURL(url);
		
		toast.success('تم تحميل رمز QR بنجاح');
		
	} catch (err) {
		toast.error('فشل في تحميل رمز QR');
		console.error('Download error:', err);
	}
}

// Copy QR code data to clipboard
async function copyQRData() {
	const dataToCopy = qrCodeData || qrDisplayUrl;
	if (!dataToCopy) return;
	
	try {
		await navigator.clipboard.writeText(dataToCopy);
		toast.success('تم نسخ رمز QR إلى الحافظة');
	} catch (err) {
		toast.error('فشل في نسخ رمز QR');
		console.error('Copy error:', err);
	}
}

// Share QR code
async function shareQRCode() {
	const shareData = qrCodeData || qrDisplayUrl;
	if (!shareData) return;
	
	try {
		if (navigator.share) {
			await navigator.share({
				title: title || 'رمز QR - Wagtee',
				text: subtitle || 'رمز QR للوصول السريع',
				url: shareData
			});
		} else {
			// Fallback to copy
			await copyQRData();
		}
	} catch (err) {
		console.error('Share error:', err);
	}
}

// Open QR code URL in new tab
function openQRUrl() {
	if (qrCodeData) {
		window.open(qrCodeData, '_blank');
	}
}

// Refresh/regenerate QR code
async function refreshQRCode() {
	if (qrCodeData) {
		previewUrl = null;
		await generateQRCode();
	}
}

// FIXED: Use Svelte 5 effect instead of onMount
$effect(() => {
	if (browser && qrCodeData && !qrDisplayUrl) {
		generateQRCode();
	}
});
</script>

<!-- QR Code Display Component -->
<div class="qr-code-display {containerClass}">
	<Card.Root class="glass-card border-white/20 shadow-xl backdrop-blur-xl">
		{#if title || subtitle}
			<Card.Header class="pb-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg {typeConfig.bgColor}">
							<svelte:component this={typeConfig.icon} class="h-5 w-5 {typeConfig.color}" />
						</div>
						<div class="space-y-1">
							{#if title}
								<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200">
									{title}
								</Card.Title>
							{:else}
								<Card.Title class="text-lg font-bold text-slate-800 dark:text-slate-200">
									{typeConfig.label}
								</Card.Title>
							{/if}
							{#if subtitle}
								<Card.Description class="text-slate-600 dark:text-slate-400">
									{subtitle}
								</Card.Description>
							{:else}
								<Card.Description class="text-slate-600 dark:text-slate-400">
									{typeConfig.description}
								</Card.Description>
							{/if}
						</div>
					</div>
					
					<Badge variant="outline" class="border-current/30 {typeConfig.color}">
						{type.toUpperCase()}
					</Badge>
				</div>
			</Card.Header>
		{/if}
		
		<Card.Content class="space-y-4">
			<!-- QR Code Image -->
			<div class="flex items-center justify-center">
				{#if isLoading}
					<div class="flex items-center justify-center {sizeClasses} bg-slate-100 dark:bg-slate-800 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600">
						<div class="text-center space-y-2">
							<RefreshCw class="h-8 w-8 animate-spin text-slate-400 mx-auto" />
							<p class="text-sm text-slate-500 dark:text-slate-400">
								جار إنشاء رمز QR...
							</p>
						</div>
					</div>
				{:else if error}
					<div class="flex items-center justify-center {sizeClasses} bg-red-50 dark:bg-red-950/30 rounded-xl border-2 border-dashed border-red-300 dark:border-red-700">
						<div class="text-center space-y-2">
							<svg class="h-8 w-8 text-red-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
							</svg>
							<p class="text-sm text-red-600 dark:text-red-400">
								{error}
							</p>
						</div>
					</div>
				{:else if qrDisplayUrl}
					<div class="relative group">
						<img
							bind:this={qrImageElement}
							src={qrDisplayUrl}
							alt="QR Code"
							class="{sizeClasses} object-contain rounded-xl border border-slate-200 dark:border-slate-700 shadow-lg bg-white dark:bg-slate-900 transition-transform duration-300 group-hover:scale-105"
							loading="lazy"
						/>
						
						<!-- Hover overlay -->
						{#if showPreview}
							<div class="absolute inset-0 bg-black/60 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
								<Button 
									variant="ghost" 
									size="sm"
									onclick={() => {/* Open preview modal */}}
									class="text-white hover:bg-white/20"
								>
									<Eye class="h-4 w-4 ml-1" />
									معاينة
								</Button>
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center justify-center {sizeClasses} bg-slate-100 dark:bg-slate-800 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600">
						<div class="text-center space-y-2">
							<QrCode class="h-8 w-8 text-slate-400 mx-auto" />
							<p class="text-sm text-slate-500 dark:text-slate-400">
								لم يتم إنشاء رمز QR
							</p>
						</div>
					</div>
				{/if}
			</div>
			
			<!-- QR Code Info -->
			{#if qrDisplayUrl && !isLoading}
				<div class="text-center space-y-2">
					<div class="text-sm text-slate-600 dark:text-slate-400">
						{#if type === 'business'}
							يمكن للعملاء مسح هذا الرمز للوصول لصفحة الحجز مباشرة
						{:else if type === 'service'}
							يمكن للعملاء مسح هذا الرمز لحجز هذه الخدمة مباشرة
						{:else if type === 'booking'}
							يمكن للعميل مسح هذا الرمز لعرض تفاصيل الحجز
						{/if}
					</div>
					
					{#if qrCodeData && qrCodeData.startsWith('http')}
						<Button 
							variant="ghost" 
							size="sm" 
							onclick={openQRUrl}
							class="text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30"
						>
							<ExternalLink class="h-4 w-4 ml-1" />
							فتح الرابط
						</Button>
					{/if}
				</div>
			{/if}
			
			<!-- Control Buttons -->
			{#if showControls && qrDisplayUrl && !isLoading}
				<div class="flex items-center justify-center gap-2 border-t border-slate-200/50 dark:border-slate-700/50 pt-4">
					<Button 
						variant="ghost" 
						size="sm" 
						onclick={downloadQRCode}
						class="glass-button"
						title="تحميل رمز QR"
					>
						<Download class="h-4 w-4" />
					</Button>
					
					<Button 
						variant="ghost" 
						size="sm" 
						onclick={copyQRData}
						class="glass-button"
						title="نسخ رمز QR"
					>
						<Copy class="h-4 w-4" />
					</Button>
					
					<Button 
						variant="ghost" 
						size="sm" 
						onclick={shareQRCode}
						class="glass-button"
						title="مشاركة رمز QR"
					>
						<Share2 class="h-4 w-4" />
					</Button>
					
					{#if qrCodeData}
						<Button 
							variant="ghost" 
							size="sm" 
							onclick={refreshQRCode}
							class="glass-button"
							title="تحديث رمز QR"
						>
							<RefreshCw class="h-4 w-4" />
						</Button>
					{/if}
				</div>
			{/if}
			
			<!-- Additional Info -->
			{#if businessId || serviceId || bookingId}
				<div class="text-xs text-center text-slate-500 dark:text-slate-500 border-t border-slate-200/50 dark:border-slate-700/50 pt-3">
					{#if businessId}
						رقم المؤسسة: {businessId}
					{:else if serviceId}
						رقم الخدمة: {serviceId}
					{:else if bookingId}
						رقم الحجز: {bookingId}
					{/if}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>

<style>
	.qr-code-display {
		@apply space-y-0;
	}
	
	.glass-card {
		background: rgba(255, 255, 255, 0.25);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border: 1px solid rgba(255, 255, 255, 0.18);
		box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
	}

	.dark .glass-card {
		background: rgba(15, 23, 42, 0.25);
		border: 1px solid rgba(255, 255, 255, 0.05);
		box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
	}
	
	.glass-button {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.1);
		transition: all 0.3s ease;
	}

	.glass-button:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: translateY(-1px);
		box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
	}

	.dark .glass-button {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.dark .glass-button:hover {
		background: rgba(255, 255, 255, 0.1);
	}
</style>