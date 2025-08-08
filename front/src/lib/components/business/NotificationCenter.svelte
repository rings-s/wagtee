<script lang="ts">
	import { onMount } from 'svelte';
	import type { Notification, NotificationTemplate, NotificationCampaign } from '$lib/types/index.js';
	import { appStore } from '$lib/stores/app.svelte.js';
	import { authStore } from '$lib/stores/auth.svelte.js';
	
	// UI Components
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '$lib/components/ui/dialog';
	import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '$lib/components/ui/select';
	import { Switch } from '$lib/components/ui/switch';
	import { Progress } from '$lib/components/ui/progress';
	import { toast } from 'svelte-sonner';
	
	// Icons
	import {
		Bell,
		MessageCircle,
		Mail,
		Smartphone,
		Send,
		Clock,
		CheckCircle,
		XCircle,
		AlertTriangle,
		Eye,
		Edit,
		Trash2,
		Plus,
		Search,
		Filter,
		RefreshCw,
		Zap,
		TrendingUp,
		Users,
		Calendar,
		Settings,
		Download,
		Upload,
		Play,
		Pause,
		BarChart3,
		Activity,
		Globe,
		Wifi,
		WifiOff
	} from 'lucide-svelte';

	interface Props {
		businessId?: number;
		showHeader?: boolean;
	}

	let { businessId, showHeader = true }: Props = $props();

	// Reactive state using Svelte 5 runes
	let searchTerm = $state('');
	let filterStatus = $state<'all' | 'sent' | 'pending' | 'failed' | 'delivered'>('all');
	let filterType = $state<'all' | 'whatsapp' | 'email' | 'sms' | 'push'>('all');
	let sortBy = $state<'created_at' | 'type' | 'status'>('created_at');
	let sortOrder = $state<'asc' | 'desc'>('desc');
	let selectedNotifications = $state<number[]>([]);
	
	// Dialog states
	let showTemplateDialog = $state(false);
	let showCampaignDialog = $state(false);
	let showNotificationDialog = $state(false);
	let editingTemplate = $state<NotificationTemplate | null>(null);
	let editingCampaign = $state<NotificationCampaign | null>(null);
	
	// Real-time connection state
	let wsConnection = $state<WebSocket | null>(null);
	let connectionStatus = $state<'connected' | 'disconnected' | 'connecting'>('disconnected');
	let lastUpdate = $state<Date | null>(null);

	// Form states
	let templateForm = $state({
		name: '',
		name_ar: '',
		type: 'whatsapp' as 'whatsapp' | 'email' | 'sms',
		subject: '',
		subject_ar: '',
		content: '',
		content_ar: '',
		is_active: true
	});

	let campaignForm = $state({
		name: '',
		name_ar: '',
		template_id: null as number | null,
		target_audience: 'all' as 'all' | 'vip' | 'regular' | 'inactive',
		schedule_type: 'immediate' as 'immediate' | 'scheduled',
		schedule_date: '',
		schedule_time: '',
		is_active: true
	});

	// Mock data - replace with actual API calls
	let notifications = $state<Notification[]>([]);
	let templates = $state<NotificationTemplate[]>([]);
	let campaigns = $state<NotificationCampaign[]>([]);
	let isLoading = $state(false);
	let isConnecting = $state(false);

	// Derived values
	const filteredNotifications = $derived(() => {
		let filtered = notifications;

		// Search filter
		if (searchTerm) {
			filtered = filtered.filter(notification => 
				notification.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
				notification.recipient.toLowerCase().includes(searchTerm.toLowerCase())
			);
		}

		// Status filter
		if (filterStatus !== 'all') {
			filtered = filtered.filter(notification => notification.status === filterStatus);
		}

		// Type filter
		if (filterType !== 'all') {
			filtered = filtered.filter(notification => notification.type === filterType);
		}

		// Sort
		filtered.sort((a, b) => {
			let comparison = 0;
			switch (sortBy) {
				case 'created_at':
					comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
					break;
				case 'type':
					comparison = a.type.localeCompare(b.type);
					break;
				case 'status':
					comparison = a.status.localeCompare(b.status);
					break;
			}
			return sortOrder === 'asc' ? comparison : -comparison;
		});

		return filtered;
	});

	const notificationStats = $derived(() => {
		const total = notifications.length;
		const sent = notifications.filter(n => n.status === 'sent').length;
		const delivered = notifications.filter(n => n.status === 'delivered').length;
		const failed = notifications.filter(n => n.status === 'failed').length;
		const pending = notifications.filter(n => n.status === 'pending').length;
		
		const deliveryRate = total > 0 ? (delivered / total) * 100 : 0;
		const successRate = total > 0 ? ((sent + delivered) / total) * 100 : 0;
		
		return {
			total,
			sent,
			delivered,
			failed,
			pending,
			deliveryRate,
			successRate
		};
	});

	// WebSocket connection management
	const connectWebSocket = () => {
		if (wsConnection?.readyState === WebSocket.OPEN) return;
		
		connectionStatus = 'connecting';
		isConnecting = true;
		
		try {
			// Replace with actual WebSocket URL
			wsConnection = new WebSocket(`ws://localhost:8000/ws/notifications/${businessId}/`);
			
			wsConnection.onopen = () => {
				connectionStatus = 'connected';
				isConnecting = false;
				lastUpdate = new Date();
				console.log('WebSocket connected');
			};
			
			wsConnection.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					handleRealtimeUpdate(data);
					lastUpdate = new Date();
				} catch (error) {
					console.error('WebSocket message error:', error);
				}
			};
			
			wsConnection.onclose = () => {
				connectionStatus = 'disconnected';
				isConnecting = false;
				console.log('WebSocket disconnected');
				
				// Reconnect after 5 seconds
				setTimeout(connectWebSocket, 5000);
			};
			
			wsConnection.onerror = (error) => {
				console.error('WebSocket error:', error);
				connectionStatus = 'disconnected';
				isConnecting = false;
			};
		} catch (error) {
			console.error('WebSocket connection error:', error);
			connectionStatus = 'disconnected';
			isConnecting = false;
		}
	};

	const handleRealtimeUpdate = (data: any) => {
		switch (data.type) {
			case 'notification_status_update':
				updateNotificationStatus(data.notification_id, data.status);
				break;
			case 'new_notification':
				addNewNotification(data.notification);
				break;
			case 'campaign_update':
				updateCampaignStatus(data.campaign_id, data.status);
				break;
		}
	};

	const updateNotificationStatus = (id: number, status: string) => {
		notifications = notifications.map(n => 
			n.id === id ? { ...n, status } : n
		);
	};

	const addNewNotification = (notification: Notification) => {
		notifications = [notification, ...notifications];
		toast.success('إشعار جديد تم إرساله');
	};

	const updateCampaignStatus = (id: number, status: string) => {
		campaigns = campaigns.map(c => 
			c.id === id ? { ...c, status } : c
		);
	};

	// Template management
	const handleCreateTemplate = async () => {
		try {
			// Replace with actual API call
			const newTemplate: NotificationTemplate = {
				id: Date.now(),
				...templateForm,
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString()
			};
			
			templates = [...templates, newTemplate];
			resetTemplateForm();
			showTemplateDialog = false;
			toast.success('تم إنشاء القالب بنجاح');
		} catch (error) {
			toast.error('فشل في إنشاء القالب');
		}
	};

	const handleUpdateTemplate = async () => {
		if (!editingTemplate) return;
		
		try {
			// Replace with actual API call
			templates = templates.map(t => 
				t.id === editingTemplate!.id 
					? { ...t, ...templateForm, updated_at: new Date().toISOString() }
					: t
			);
			
			resetTemplateForm();
			showTemplateDialog = false;
			editingTemplate = null;
			toast.success('تم تحديث القالب بنجاح');
		} catch (error) {
			toast.error('فشل في تحديث القالب');
		}
	};

	const handleDeleteTemplate = async (templateId: number) => {
		if (!confirm('هل أنت متأكد من حذف هذا القالب؟')) return;
		
		try {
			// Replace with actual API call
			templates = templates.filter(t => t.id !== templateId);
			toast.success('تم حذف القالب بنجاح');
		} catch (error) {
			toast.error('فشل في حذف القالب');
		}
	};

	const resetTemplateForm = () => {
		templateForm = {
			name: '',
			name_ar: '',
			type: 'whatsapp',
			subject: '',
			subject_ar: '',
			content: '',
			content_ar: '',
			is_active: true
		};
		editingTemplate = null;
	};

	// Campaign management
	const handleCreateCampaign = async () => {
		try {
			// Replace with actual API call
			const newCampaign: NotificationCampaign = {
				id: Date.now(),
				...campaignForm,
				status: campaignForm.schedule_type === 'immediate' ? 'running' : 'scheduled',
				created_at: new Date().toISOString(),
				updated_at: new Date().toISOString(),
				sent_count: 0,
				delivered_count: 0,
				failed_count: 0
			};
			
			campaigns = [...campaigns, newCampaign];
			resetCampaignForm();
			showCampaignDialog = false;
			toast.success('تم إنشاء الحملة بنجاح');
		} catch (error) {
			toast.error('فشل في إنشاء الحملة');
		}
	};

	const resetCampaignForm = () => {
		campaignForm = {
			name: '',
			name_ar: '',
			template_id: null,
			target_audience: 'all',
			schedule_type: 'immediate',
			schedule_date: '',
			schedule_time: '',
			is_active: true
		};
		editingCampaign = null;
	};

	// Utility functions
	const getStatusIcon = (status: string) => {
		switch (status) {
			case 'sent':
			case 'delivered':
				return CheckCircle;
			case 'failed':
				return XCircle;
			case 'pending':
				return Clock;
			default:
				return AlertTriangle;
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case 'delivered':
				return 'text-green-500';
			case 'sent':
				return 'text-blue-500';
			case 'failed':
				return 'text-red-500';
			case 'pending':
				return 'text-yellow-500';
			default:
				return 'text-gray-500';
		}
	};

	const getTypeIcon = (type: string) => {
		switch (type) {
			case 'whatsapp':
				return MessageCircle;
			case 'email':
				return Mail;
			case 'sms':
				return Smartphone;
			default:
				return Bell;
		}
	};

	const formatDate = (dateString: string) => {
		return new Date(dateString).toLocaleDateString('ar-SA', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	};

	// Load data on mount
	onMount(() => {
		if (authStore.isAuthenticated) {
			loadNotifications();
			loadTemplates();
			loadCampaigns();
			connectWebSocket();
		}
		
		return () => {
			wsConnection?.close();
		};
	});

	const loadNotifications = async () => {
		isLoading = true;
		try {
			// Mock data - replace with actual API call
			notifications = [
				{
					id: 1,
					type: 'whatsapp',
					recipient: '+966501234567',
					content: 'تذكير: لديك موعد غداً في الساعة 2:00 مساءً',
					status: 'delivered',
					created_at: new Date().toISOString(),
					sent_at: new Date().toISOString(),
					delivered_at: new Date().toISOString()
				},
				{
					id: 2,
					type: 'email',
					recipient: 'customer@example.com',
					content: 'تأكيد حجز موعدك',
					status: 'sent',
					created_at: new Date(Date.now() - 3600000).toISOString(),
					sent_at: new Date(Date.now() - 3600000).toISOString()
				}
			];
		} catch (error) {
			console.error('Error loading notifications:', error);
		} finally {
			isLoading = false;
		}
	};

	const loadTemplates = async () => {
		try {
			// Mock data - replace with actual API call
			templates = [
				{
					id: 1,
					name: 'Booking Confirmation',
					name_ar: 'تأكيد الحجز',
					type: 'whatsapp',
					subject: 'حجزك مؤكد',
					content: 'مرحباً {customer_name}, تم تأكيد حجزك في {appointment_date} في {appointment_time}',
					is_active: true,
					created_at: new Date().toISOString(),
					updated_at: new Date().toISOString()
				}
			];
		} catch (error) {
			console.error('Error loading templates:', error);
		}
	};

	const loadCampaigns = async () => {
		try {
			// Mock data - replace with actual API call
			campaigns = [
				{
					id: 1,
					name: 'Monthly Newsletter',
					name_ar: 'النشرة الشهرية',
					template_id: 1,
					target_audience: 'all',
					status: 'completed',
					sent_count: 150,
					delivered_count: 142,
					failed_count: 8,
					created_at: new Date(Date.now() - 86400000).toISOString(),
					updated_at: new Date(Date.now() - 86400000).toISOString()
				}
			];
		} catch (error) {
			console.error('Error loading campaigns:', error);
		}
	};
</script>

<!-- Notification Center Interface -->
<div class="space-y-6">
	{#if showHeader}
		<!-- Header Section -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">مركز الإشعارات</h1>
				<p class="text-muted-foreground">إدارة وإرسال الإشعارات والحملات التسويقية</p>
			</div>
			
			<div class="flex items-center gap-2">
				<!-- Connection Status -->
				<div class="flex items-center gap-2 px-3 py-1 rounded-lg bg-muted/50">
					{#if connectionStatus === 'connected'}
						<Wifi class="h-4 w-4 text-green-500" />
						<span class="text-xs text-green-600">متصل</span>
					{:else if connectionStatus === 'connecting'}
						<RefreshCw class="h-4 w-4 animate-spin text-yellow-500" />
						<span class="text-xs text-yellow-600">جاري الاتصال</span>
					{:else}
						<WifiOff class="h-4 w-4 text-red-500" />
						<span class="text-xs text-red-600">غير متصل</span>
					{/if}
				</div>
				
				<Button
					variant="outline"
					size="sm"
					onclick={() => loadNotifications()}
					disabled={isLoading}
				>
					<RefreshCw class="h-4 w-4 {isLoading ? 'animate-spin' : ''}" />
					تحديث
				</Button>
				
				<Button class="btn-premium hover-lift">
					<Send class="h-4 w-4" />
					إرسال إشعار
				</Button>
			</div>
		</div>
	{/if}

	<!-- Statistics Cards -->
	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center space-x-2">
					<Bell class="h-8 w-8 text-blue-500" />
					<div>
						<p class="text-2xl font-bold">{notificationStats.total}</p>
						<p class="text-xs text-muted-foreground">إجمالي الإشعارات</p>
					</div>
				</div>
			</CardContent>
		</Card>
		
		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center space-x-2">
					<CheckCircle class="h-8 w-8 text-green-500" />
					<div>
						<p class="text-2xl font-bold">{notificationStats.delivered}</p>
						<p class="text-xs text-muted-foreground">تم التسليم</p>
					</div>
				</div>
			</CardContent>
		</Card>
		
		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center space-x-2">
					<TrendingUp class="h-8 w-8 text-purple-500" />
					<div>
						<p class="text-2xl font-bold">{notificationStats.deliveryRate.toFixed(1)}%</p>
						<p class="text-xs text-muted-foreground">معدل التسليم</p>
					</div>
				</div>
			</CardContent>
		</Card>
		
		<Card class="card-premium">
			<CardContent class="p-6">
				<div class="flex items-center space-x-2">
					<Activity class="h-8 w-8 text-orange-500" />
					<div>
						<p class="text-2xl font-bold">{notificationStats.successRate.toFixed(1)}%</p>
						<p class="text-xs text-muted-foreground">معدل النجاح</p>
					</div>
				</div>
			</CardContent>
		</Card>
	</div>

	<!-- Main Content Tabs -->
	<Tabs value="notifications" class="space-y-4">
		<TabsList class="grid w-full grid-cols-4">
			<TabsTrigger value="notifications">الإشعارات</TabsTrigger>
			<TabsTrigger value="templates">القوالب</TabsTrigger>
			<TabsTrigger value="campaigns">الحملات</TabsTrigger>
			<TabsTrigger value="analytics">الإحصائيات</TabsTrigger>
		</TabsList>

		<!-- Notifications Tab -->
		<TabsContent value="notifications" class="space-y-4">
			<!-- Filters and Search -->
			<Card class="card-premium">
				<CardContent class="p-6">
					<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
						<!-- Search -->
						<div class="flex items-center space-x-2 flex-1 max-w-sm">
							<div class="relative flex-1">
								<Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
								<Input
									type="text"
									placeholder="البحث في الإشعارات..."
									bind:value={searchTerm}
									class="pl-9"
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
									<SelectItem value="delivered">تم التسليم</SelectItem>
									<SelectItem value="sent">تم الإرسال</SelectItem>
									<SelectItem value="pending">في الانتظار</SelectItem>
									<SelectItem value="failed">فشل</SelectItem>
								</SelectContent>
							</Select>

							<Select bind:value={filterType}>
								<SelectTrigger class="w-32">
									<SelectValue placeholder="النوع" />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="all">الكل</SelectItem>
									<SelectItem value="whatsapp">واتساب</SelectItem>
									<SelectItem value="email">إيميل</SelectItem>
									<SelectItem value="sms">SMS</SelectItem>
								</SelectContent>
							</Select>
						</div>
					</div>
				</CardContent>
			</Card>

			<!-- Notifications List -->
			<div class="space-y-4">
				{#if isLoading}
					{#each Array(5) as _}
						<Card class="animate-pulse">
							<CardContent class="p-6">
								<div class="flex items-center space-x-4">
									<div class="w-12 h-12 bg-muted rounded-full"></div>
									<div class="space-y-2 flex-1">
										<div class="h-4 bg-muted rounded w-3/4"></div>
										<div class="h-3 bg-muted rounded w-1/2"></div>
									</div>
								</div>
							</CardContent>
						</Card>
					{/each}
				{:else if filteredNotifications.length === 0}
					<Card class="text-center py-12">
						<CardContent>
							<Bell class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
							<h3 class="text-lg font-medium mb-2">لا توجد إشعارات</h3>
							<p class="text-muted-foreground mb-4">
								{searchTerm ? 'لم يتم العثور على إشعارات مطابقة' : 'لم يتم إرسال أي إشعارات بعد'}
							</p>
						</CardContent>
					</Card>
				{:else}
					{#each filteredNotifications as notification (notification.id)}
						<Card class="card-premium hover-lift transition-all duration-300">
							<CardContent class="p-6">
								<div class="flex items-start space-x-4">
									<!-- Type Icon -->
									<div class="flex-shrink-0">
										{@const TypeIcon = getTypeIcon(notification.type)}
										<div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
											<TypeIcon class="h-6 w-6 text-white" />
										</div>
									</div>
									
									<!-- Content -->
									<div class="flex-1 min-w-0">
										<div class="flex items-center justify-between mb-2">
											<h3 class="font-semibold truncate">{notification.recipient}</h3>
											<div class="flex items-center space-x-2">
												{@const StatusIcon = getStatusIcon(notification.status)}
												<StatusIcon class="h-4 w-4 {getStatusColor(notification.status)}" />
												<Badge variant={notification.status === 'delivered' ? 'default' : 
													notification.status === 'failed' ? 'destructive' : 'secondary'}>
													{notification.status === 'delivered' ? 'تم التسليم' :
													notification.status === 'sent' ? 'تم الإرسال' :
													notification.status === 'failed' ? 'فشل' : 'في الانتظار'}
												</Badge>
											</div>
										</div>
										
										<p class="text-sm text-muted-foreground mb-3 line-clamp-2">
											{notification.content}
										</p>
										
										<div class="flex items-center text-xs text-muted-foreground">
											<Clock class="h-3 w-3 mr-1" />
											{formatDate(notification.created_at)}
											{#if notification.delivered_at}
												<span class="mx-2">•</span>
												<span>تم التسليم: {formatDate(notification.delivered_at)}</span>
											{/if}
										</div>
									</div>
									
									<!-- Actions -->
									<div class="flex items-center space-x-1">
										<Button variant="ghost" size="sm">
											<Eye class="h-4 w-4" />
										</Button>
									</div>
								</div>
							</CardContent>
						</Card>
					{/each}
				{/if}
			</div>
		</TabsContent>

		<!-- Templates Tab -->
		<TabsContent value="templates" class="space-y-4">
			<div class="flex justify-between items-center">
				<h2 class="text-xl font-semibold">قوالب الإشعارات</h2>
				<Dialog bind:open={showTemplateDialog}>
					<DialogTrigger>
						<Button class="btn-premium hover-lift" onclick={resetTemplateForm}>
							<Plus class="h-4 w-4" />
							قالب جديد
						</Button>
					</DialogTrigger>
				</Dialog>
			</div>
			
			<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
				{#each templates as template (template.id)}
					<Card class="card-premium hover-lift">
						<CardHeader>
							<div class="flex items-center justify-between">
								<CardTitle class="text-lg">{template.name}</CardTitle>
								<Badge variant={template.is_active ? 'default' : 'secondary'}>
									{template.is_active ? 'نشط' : 'غير نشط'}
								</Badge>
							</div>
							{#if template.name_ar}
								<CardDescription>{template.name_ar}</CardDescription>
							{/if}
						</CardHeader>
						<CardContent>
							<div class="space-y-3">
								<div class="flex items-center text-sm">
									{@const TypeIcon = getTypeIcon(template.type)}
									<TypeIcon class="h-4 w-4 mr-2" />
									<span class="capitalize">{template.type}</span>
								</div>
								
								<p class="text-sm text-muted-foreground line-clamp-3">
									{template.content}
								</p>
								
								<div class="flex items-center justify-between pt-3">
									<span class="text-xs text-muted-foreground">
										{formatDate(template.updated_at)}
									</span>
									<div class="flex items-center space-x-1">
										<Button variant="ghost" size="sm">
											<Edit class="h-4 w-4" />
										</Button>
										<Button variant="ghost" size="sm" onclick={() => handleDeleteTemplate(template.id)}>
											<Trash2 class="h-4 w-4" />
										</Button>
									</div>
								</div>
							</div>
						</CardContent>
					</Card>
				{/each}
			</div>
		</TabsContent>

		<!-- Campaigns Tab -->
		<TabsContent value="campaigns" class="space-y-4">
			<div class="flex justify-between items-center">
				<h2 class="text-xl font-semibold">الحملات</h2>
				<Dialog bind:open={showCampaignDialog}>
					<DialogTrigger>
						<Button class="btn-premium hover-lift" onclick={resetCampaignForm}>
							<Plus class="h-4 w-4" />
							حملة جديدة
						</Button>
					</DialogTrigger>
				</Dialog>
			</div>
			
			<div class="space-y-4">
				{#each campaigns as campaign (campaign.id)}
					<Card class="card-premium hover-lift">
						<CardContent class="p-6">
							<div class="flex items-start justify-between">
								<div class="flex-1">
									<h3 class="font-semibold text-lg mb-1">{campaign.name}</h3>
									{#if campaign.name_ar}
										<p class="text-sm text-muted-foreground mb-3">{campaign.name_ar}</p>
									{/if}
									
									<div class="grid grid-cols-3 gap-4 mb-4">
										<div class="text-center">
											<p class="text-2xl font-bold text-blue-600">{campaign.sent_count}</p>
											<p class="text-xs text-muted-foreground">تم الإرسال</p>
										</div>
										<div class="text-center">
											<p class="text-2xl font-bold text-green-600">{campaign.delivered_count}</p>
											<p class="text-xs text-muted-foreground">تم التسليم</p>
										</div>
										<div class="text-center">
											<p class="text-2xl font-bold text-red-600">{campaign.failed_count}</p>
											<p class="text-xs text-muted-foreground">فشل</p>
										</div>
									</div>
									
									{#if campaign.sent_count > 0}
										<Progress 
											value={(campaign.delivered_count / campaign.sent_count) * 100} 
											class="mb-2"
										/>
										<p class="text-xs text-muted-foreground">
											معدل التسليم: {((campaign.delivered_count / campaign.sent_count) * 100).toFixed(1)}%
										</p>
									{/if}
								</div>
								
								<div class="text-right">
									<Badge variant={campaign.status === 'completed' ? 'default' : 
										campaign.status === 'running' ? 'secondary' : 'outline'}>
										{campaign.status === 'completed' ? 'مكتملة' :
										campaign.status === 'running' ? 'جارية' : 'مجدولة'}
									</Badge>
									<p class="text-xs text-muted-foreground mt-2">
										{formatDate(campaign.created_at)}
									</p>
								</div>
							</div>
						</CardContent>
					</Card>
				{/each}
			</div>
		</TabsContent>

		<!-- Analytics Tab -->
		<TabsContent value="analytics" class="space-y-4">
			<div class="grid gap-4 md:grid-cols-2">
				<Card class="card-premium">
					<CardHeader>
						<CardTitle>أداء الإشعارات</CardTitle>
					</CardHeader>
					<CardContent>
						<div class="space-y-4">
							<div class="flex justify-between items-center">
								<span>معدل التسليم</span>
								<span class="font-bold">{notificationStats.deliveryRate.toFixed(1)}%</span>
							</div>
							<Progress value={notificationStats.deliveryRate} />
							
							<div class="flex justify-between items-center">
								<span>معدل النجاح</span>
								<span class="font-bold">{notificationStats.successRate.toFixed(1)}%</span>
							</div>
							<Progress value={notificationStats.successRate} />
						</div>
					</CardContent>
				</Card>
				
				<Card class="card-premium">
					<CardHeader>
						<CardTitle>إحصائيات سريعة</CardTitle>
					</CardHeader>
					<CardContent>
						<div class="space-y-3">
							<div class="flex justify-between">
								<span>إجمالي الإشعارات</span>
								<span class="font-bold">{notificationStats.total}</span>
							</div>
							<div class="flex justify-between">
								<span>تم التسليم</span>
								<span class="font-bold text-green-600">{notificationStats.delivered}</span>
							</div>
							<div class="flex justify-between">
								<span>فشل</span>
								<span class="font-bold text-red-600">{notificationStats.failed}</span>
							</div>
							<div class="flex justify-between">
								<span>في الانتظار</span>
								<span class="font-bold text-yellow-600">{notificationStats.pending}</span>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</TabsContent>
	</Tabs>

	<!-- Template Dialog -->
	<DialogContent class="sm:max-w-2xl">
		<DialogHeader>
			<DialogTitle>
				{editingTemplate ? 'تعديل القالب' : 'قالب جديد'}
			</DialogTitle>
		</DialogHeader>

		<form
			class="space-y-4"
			onsubmit={(e) => {
				e.preventDefault();
				editingTemplate ? handleUpdateTemplate() : handleCreateTemplate();
			}}
		>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="template-name">اسم القالب</Label>
					<Input
						id="template-name"
						bind:value={templateForm.name}
						placeholder="مثل: تأكيد الحجز"
						required
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="template-name-ar">الاسم بالعربية</Label>
					<Input
						id="template-name-ar"
						bind:value={templateForm.name_ar}
						placeholder="الاسم بالعربية"
						dir="rtl"
					/>
				</div>
			</div>

			<div class="space-y-2">
				<Label for="template-type">نوع الإشعار</Label>
				<Select bind:value={templateForm.type}>
					<SelectTrigger>
						<SelectValue placeholder="اختر نوع الإشعار" />
					</SelectTrigger>
					<SelectContent>
						<SelectItem value="whatsapp">واتساب</SelectItem>
						<SelectItem value="email">إيميل</SelectItem>
						<SelectItem value="sms">SMS</SelectItem>
					</SelectContent>
				</Select>
			</div>

			{#if templateForm.type === 'email'}
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="space-y-2">
						<Label for="template-subject">الموضوع</Label>
						<Input
							id="template-subject"
							bind:value={templateForm.subject}
							placeholder="موضوع الرسالة"
						/>
					</div>
					
					<div class="space-y-2">
						<Label for="template-subject-ar">الموضوع بالعربية</Label>
						<Input
							id="template-subject-ar"
							bind:value={templateForm.subject_ar}
							placeholder="الموضوع بالعربية"
							dir="rtl"
						/>
					</div>
				</div>
			{/if}

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="template-content">المحتوى</Label>
					<Textarea
						id="template-content"
						bind:value={templateForm.content}
						placeholder="محتوى الإشعار..."
						rows={4}
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="template-content-ar">المحتوى بالعربية</Label>
					<Textarea
						id="template-content-ar"
						bind:value={templateForm.content_ar}
						placeholder="المحتوى بالعربية..."
						dir="rtl"
						rows={4}
					/>
				</div>
			</div>

			<div class="flex items-center space-x-2">
				<Switch
					id="template-active"
					bind:checked={templateForm.is_active}
				/>
				<Label for="template-active">قالب نشط</Label>
			</div>

			<div class="flex items-center justify-end space-x-2 pt-4 border-t border-border">
				<Button variant="outline" type="button" onclick={() => showTemplateDialog = false}>
					إلغاء
				</Button>
				<Button type="submit" class="btn-premium">
					{editingTemplate ? 'تحديث القالب' : 'إنشاء القالب'}
				</Button>
			</div>
		</form>
	</DialogContent>

	<!-- Campaign Dialog -->
	<DialogContent class="sm:max-w-2xl">
		<DialogHeader>
			<DialogTitle>حملة جديدة</DialogTitle>
		</DialogHeader>

		<form
			class="space-y-4"
			onsubmit={(e) => {
				e.preventDefault();
				handleCreateCampaign();
			}}
		>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="campaign-name">اسم الحملة</Label>
					<Input
						id="campaign-name"
						bind:value={campaignForm.name}
						placeholder="مثل: عرض خاص"
						required
					/>
				</div>
				
				<div class="space-y-2">
					<Label for="campaign-name-ar">الاسم بالعربية</Label>
					<Input
						id="campaign-name-ar"
						bind:value={campaignForm.name_ar}
						placeholder="الاسم بالعربية"
						dir="rtl"
					/>
				</div>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="campaign-template">القالب</Label>
					<Select bind:value={campaignForm.template_id}>
						<SelectTrigger>
							<SelectValue placeholder="اختر القالب" />
						</SelectTrigger>
						<SelectContent>
							{#each templates as template}
								<SelectItem value={template.id}>{template.name}</SelectItem>
							{/each}
						</SelectContent>
					</Select>
				</div>
				
				<div class="space-y-2">
					<Label for="campaign-audience">الجمهور المستهدف</Label>
					<Select bind:value={campaignForm.target_audience}>
						<SelectTrigger>
							<SelectValue placeholder="اختر الجمهور" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="all">جميع العملاء</SelectItem>
							<SelectItem value="vip">عملاء VIP</SelectItem>
							<SelectItem value="regular">عملاء منتظمون</SelectItem>
							<SelectItem value="inactive">عملاء غير نشطين</SelectItem>
						</SelectContent>
					</Select>
				</div>
			</div>

			<div class="space-y-2">
				<Label>وقت الإرسال</Label>
				<div class="flex items-center space-x-4">
					<div class="flex items-center space-x-2">
						<input
							type="radio"
							id="immediate"
							bind:group={campaignForm.schedule_type}
							value="immediate"
						/>
						<Label for="immediate">إرسال فوري</Label>
					</div>
					<div class="flex items-center space-x-2">
						<input
							type="radio"
							id="scheduled"
							bind:group={campaignForm.schedule_type}
							value="scheduled"
						/>
						<Label for="scheduled">جدولة</Label>
					</div>
				</div>
			</div>

			{#if campaignForm.schedule_type === 'scheduled'}
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="space-y-2">
						<Label for="schedule-date">التاريخ</Label>
						<Input
							id="schedule-date"
							type="date"
							bind:value={campaignForm.schedule_date}
							required
						/>
					</div>
					
					<div class="space-y-2">
						<Label for="schedule-time">الوقت</Label>
						<Input
							id="schedule-time"
							type="time"
							bind:value={campaignForm.schedule_time}
							required
						/>
					</div>
				</div>
			{/if}

			<div class="flex items-center justify-end space-x-2 pt-4 border-t border-border">
				<Button variant="outline" type="button" onclick={() => showCampaignDialog = false}>
					إلغاء
				</Button>
				<Button type="submit" class="btn-premium">
					إنشاء الحملة
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

	.line-clamp-3 {
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>