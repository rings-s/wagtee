<script lang="ts">
	import { onMount } from 'svelte';
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
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Popover, PopoverContent, PopoverTrigger } from '$lib/components/ui/popover';
	import { Calendar } from '$lib/components/ui/calendar';
	import { toast } from 'svelte-sonner';
	
	// Icons
	import {
		Clock,
		Calendar as CalendarIcon,
		Plus,
		Minus,
		Edit,
		Trash2,
		Copy,
		Save,
		RefreshCw,
		Settings,
		MapPin,
		Moon,
		Sun,
		Coffee,
		Users,
		AlertTriangle,
		CheckCircle,
		XCircle,
		Download,
		Upload,
		MoreHorizontal,
		Zap,
		Star,
		Globe,
		Smartphone,
		FileText,
		Archive,
		Calendar as CalendarDays,
		Timer,
		Activity,
		TrendingUp,
		Filter,
		Search,
		ChevronDown,
		ChevronRight,
		Sparkles,
		Bell,
		Shield,
		Eye,
		EyeOff
	} from 'lucide-svelte';

	interface Props {
		businessId?: number;
		showHeader?: boolean;
		compactMode?: boolean;
	}

	let { businessId, showHeader = true, compactMode = false }: Props = $props();

	// Saudi work week (Saturday-Sunday)
	const DAYS_OF_WEEK = [
		{ key: 'saturday', label: 'Saturday', labelAr: 'السبت', index: 6 },
		{ key: 'sunday', label: 'Sunday', labelAr: 'الأحد', index: 0 },
		{ key: 'monday', label: 'Monday', labelAr: 'الاثنين', index: 1 },
		{ key: 'tuesday', label: 'Tuesday', labelAr: 'الثلاثاء', index: 2 },
		{ key: 'wednesday', label: 'Wednesday', labelAr: 'الأربعاء', index: 3 },
		{ key: 'thursday', label: 'Thursday', labelAr: 'الخميس', index: 4 },
		{ key: 'friday', label: 'Friday', labelAr: 'الجمعة', index: 5 }
	];

	const PRAYER_TIMES = [
		{ name: 'Fajr', nameAr: 'الفجر', time: '05:00' },
		{ name: 'Dhuhr', nameAr: 'الظهر', time: '12:15' },
		{ name: 'Asr', nameAr: 'العصر', time: '15:30' },
		{ name: 'Maghrib', nameAr: 'المغرب', time: '18:00' },
		{ name: 'Isha', nameAr: 'العشاء', time: '19:30' }
	];

	const SAUDI_HOLIDAYS = [
		{ name: 'Saudi National Day', nameAr: 'اليوم الوطني السعودي', date: '2025-09-23' },
		{ name: 'Foundation Day', nameAr: 'يوم التأسيس', date: '2025-02-22' },
		{ name: 'Eid Al-Fitr', nameAr: 'عيد الفطر', date: '2025-03-30', duration: 3 },
		{ name: 'Eid Al-Adha', nameAr: 'عيد الأضحى', date: '2025-06-06', duration: 4 }
	];

	const BUSINESS_TYPES = [
		'barber', 'salon', 'beauty_center', 'car_wash', 'cleaning', 
		'gym', 'photographer', 'makeup_artist', 'bazar', 'events'
	];

	// Time slot interface
	interface TimeSlot {
		id: string;
		startTime: string;
		endTime: string;
		capacity?: number;
		serviceIds?: number[];
		isBreak?: boolean;
		notes?: string;
	}

	// Business hours interface
	interface DaySchedule {
		isOpen: boolean;
		timeSlots: TimeSlot[];
		breakTimes: TimeSlot[];
		capacity: number;
		notes: string;
	}

	interface BusinessHours {
		[key: string]: DaySchedule;
	}

	interface SeasonalSchedule {
		id: string;
		name: string;
		nameAr: string;
		startDate: string;
		endDate: string;
		schedule: BusinessHours;
		isActive: boolean;
		priority: number;
	}

	interface HolidayException {
		id: string;
		date: string;
		name: string;
		nameAr: string;
		isClosed: boolean;
		customSchedule?: DaySchedule;
		isRecurring: boolean;
		recurringType?: 'weekly' | 'monthly' | 'yearly';
	}

	// Reactive state using Svelte 5 runes
	let activeTab = $state('weekly');
	let selectedDay = $state('saturday');
	let viewMode = $state<'simple' | 'advanced'>('simple');
	let timeFormat = $state<'12h' | '24h'>('12h');
	let language = $state<'en' | 'ar'>('en');
	let showPreview = $state(false);
	let isLoading = $state(false);
	let isDirty = $state(false);

	// Business hours state
	let businessHours = $state<BusinessHours>({
		saturday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		sunday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		monday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		tuesday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		wednesday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		thursday: { isOpen: true, timeSlots: [], breakTimes: [], capacity: 10, notes: '' },
		friday: { isOpen: false, timeSlots: [], breakTimes: [], capacity: 10, notes: 'Closed for Friday prayers' }
	});

	let seasonalSchedules = $state<SeasonalSchedule[]>([]);
	let holidayExceptions = $state<HolidayException[]>([]);
	let templates = $state<{ [key: string]: BusinessHours }>({});

	// Form states
	let showScheduleDialog = $state(false);
	let showSeasonalDialog = $state(false);
	let showHolidayDialog = $state(false);
	let showTemplateDialog = $state(false);
	let editingSchedule = $state<SeasonalSchedule | null>(null);
	let editingHoliday = $state<HolidayException | null>(null);

	// Advanced configuration
	let settings = $state({
		enablePrayerTimeIntegration: false,
		enableRamadanSchedule: false,
		enableCapacityManagement: true,
		enableServiceSpecificHours: false,
		minimumBookingNotice: 30, // minutes
		maximumAdvanceBooking: 30, // days
		slotDuration: 60, // minutes
		bufferTime: 15, // minutes between appointments
		enableBreakReminders: true,
		enableHolidayNotifications: true,
		autoCloseOnHolidays: true,
		enableSeasonalAdjustments: true
	});

	// Services state (for service-specific hours)
	let services = $state<Array<{ id: number; name: string; duration: number }>>([]);

	// Drag and drop state
	let draggedSlot = $state<TimeSlot | null>(null);
	let dropZone = $state<string | null>(null);

	// Calendar state for holidays
	let selectedDate = $state<Date | null>(null);
	let calendarOpen = $state(false);

	// Derived values
	const currentDaySchedule = $derived(() => businessHours[selectedDay]);
	
	const weeklyOverview = $derived(() => {
		return DAYS_OF_WEEK.map(day => ({
			...day,
			schedule: businessHours[day.key],
			isOpen: businessHours[day.key].isOpen,
			totalHours: calculateDayHours(businessHours[day.key]),
			slots: businessHours[day.key].timeSlots.length
		}));
	});

	const totalWeeklyHours = $derived(() => {
		return Object.values(businessHours).reduce((total, day) => {
			return total + calculateDayHours(day);
		}, 0);
	});

	const upcomingHolidays = $derived(() => {
		const today = new Date();
		const upcoming = [...SAUDI_HOLIDAYS, ...holidayExceptions]
			.filter(holiday => new Date(holiday.date) > today)
			.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
			.slice(0, 5);
		return upcoming;
	});

	const conflictingSchedules = $derived(() => {
		// Check for overlapping time slots
		const conflicts: Array<{ day: string; message: string }> = [];
		
		Object.entries(businessHours).forEach(([day, schedule]) => {
			if (!schedule.isOpen) return;
			
			const slots = [...schedule.timeSlots, ...schedule.breakTimes].sort((a, b) => 
				a.startTime.localeCompare(b.startTime)
			);
			
			for (let i = 0; i < slots.length - 1; i++) {
				const current = slots[i];
				const next = slots[i + 1];
				
				if (current.endTime > next.startTime) {
					conflicts.push({
						day,
						message: `Overlapping slots: ${formatTime(current.startTime)}-${formatTime(current.endTime)} and ${formatTime(next.startTime)}-${formatTime(next.endTime)}`
					});
				}
			}
		});
		
		return conflicts;
	});

	// Utility functions
	const formatTime = (time: string): string => {
		if (timeFormat === '12h') {
			const [hours, minutes] = time.split(':');
			const hour = parseInt(hours);
			const ampm = hour >= 12 ? 'PM' : 'AM';
			const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
			return `${displayHour}:${minutes} ${ampm}`;
		}
		return time;
	};

	const calculateDayHours = (schedule: DaySchedule): number => {
		if (!schedule.isOpen) return 0;
		
		return schedule.timeSlots.reduce((total, slot) => {
			const start = new Date(`2000-01-01T${slot.startTime}`);
			const end = new Date(`2000-01-01T${slot.endTime}`);
			const diff = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
			return total + diff;
		}, 0);
	};

	const generateTimeSlots = (startTime: string, endTime: string, duration: number): TimeSlot[] => {
		const slots: TimeSlot[] = [];
		const start = new Date(`2000-01-01T${startTime}`);
		const end = new Date(`2000-01-01T${endTime}`);
		
		let current = new Date(start);
		let slotIndex = 0;
		
		while (current < end) {
			const slotEnd = new Date(current.getTime() + duration * 60000);
			if (slotEnd > end) break;
			
			slots.push({
				id: `slot-${Date.now()}-${slotIndex}`,
				startTime: current.toTimeString().slice(0, 5),
				endTime: slotEnd.toTimeString().slice(0, 5),
				capacity: settings.enableCapacityManagement ? Math.floor(businessHours[selectedDay].capacity / 2) : undefined
			});
			
			current = new Date(slotEnd.getTime() + settings.bufferTime * 60000);
			slotIndex++;
		}
		
		return slots;
	};

	const addTimeSlot = (day: string) => {
		const schedule = businessHours[day];
		const lastSlot = schedule.timeSlots[schedule.timeSlots.length - 1];
		const startTime = lastSlot ? lastSlot.endTime : '09:00';
		const endTime = addMinutesToTime(startTime, settings.slotDuration);
		
		const newSlot: TimeSlot = {
			id: `slot-${Date.now()}`,
			startTime,
			endTime,
			capacity: settings.enableCapacityManagement ? Math.floor(schedule.capacity / 2) : undefined
		};
		
		schedule.timeSlots.push(newSlot);
		isDirty = true;
	};

	const removeTimeSlot = (day: string, slotId: string) => {
		const schedule = businessHours[day];
		schedule.timeSlots = schedule.timeSlots.filter(slot => slot.id !== slotId);
		isDirty = true;
	};

	const addBreakTime = (day: string) => {
		const schedule = businessHours[day];
		const newBreak: TimeSlot = {
			id: `break-${Date.now()}`,
			startTime: '12:00',
			endTime: '13:00',
			isBreak: true,
			notes: 'Lunch break'
		};
		
		schedule.breakTimes.push(newBreak);
		isDirty = true;
	};

	const addMinutesToTime = (time: string, minutes: number): string => {
		const [hours, mins] = time.split(':').map(Number);
		const date = new Date(2000, 0, 1, hours, mins + minutes);
		return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
	};

	const copySchedule = (fromDay: string, toDay: string) => {
		businessHours[toDay] = JSON.parse(JSON.stringify(businessHours[fromDay]));
		isDirty = true;
		toast.success(`Schedule copied from ${fromDay} to ${toDay}`);
	};

	const saveTemplate = (name: string) => {
		templates[name] = JSON.parse(JSON.stringify(businessHours));
		toast.success(`Template "${name}" saved`);
	};

	const loadTemplate = (name: string) => {
		if (templates[name]) {
			businessHours = JSON.parse(JSON.stringify(templates[name]));
			isDirty = true;
			toast.success(`Template "${name}" loaded`);
		}
	};

	// Actions
	const handleSave = async () => {
		isLoading = true;
		try {
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 1000));
			isDirty = false;
			toast.success('Business hours updated successfully');
		} catch (error) {
			toast.error('Failed to save business hours');
		} finally {
			isLoading = false;
		}
	};

	const handleReset = () => {
		if (confirm('Are you sure you want to reset all changes?')) {
			// Reset to default schedule
			Object.keys(businessHours).forEach(day => {
				if (day === 'friday') {
					businessHours[day] = { isOpen: false, timeSlots: [], breakTimes: [], capacity: 10, notes: 'Closed for Friday prayers' };
				} else {
					businessHours[day] = {
						isOpen: true,
						timeSlots: [{ id: `default-${day}`, startTime: '09:00', endTime: '17:00' }],
						breakTimes: [{ id: `break-${day}`, startTime: '12:00', endTime: '13:00', isBreak: true }],
						capacity: 10,
						notes: ''
					};
				}
			});
			isDirty = false;
			toast.success('Schedule reset to default');
		}
	};

	const exportSchedule = () => {
		const data = {
			businessHours,
			seasonalSchedules,
			holidayExceptions,
			settings,
			templates,
			exportDate: new Date().toISOString()
		};
		
		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `business-hours-${new Date().toISOString().slice(0, 10)}.json`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
		
		toast.success('Schedule exported successfully');
	};

	const importSchedule = (event: Event) => {
		const file = (event.target as HTMLInputElement).files?.[0];
		if (!file) return;
		
		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const data = JSON.parse(e.target?.result as string);
				businessHours = data.businessHours || businessHours;
				seasonalSchedules = data.seasonalSchedules || [];
				holidayExceptions = data.holidayExceptions || [];
				settings = { ...settings, ...data.settings };
				templates = { ...templates, ...data.templates };
				isDirty = true;
				toast.success('Schedule imported successfully');
			} catch (error) {
				toast.error('Invalid file format');
			}
		};
		reader.readAsText(file);
	};

	// Load data on mount
	onMount(() => {
		if (authStore.isAuthenticated) {
			// Load services for service-specific hours
			services = [
				{ id: 1, name: 'Haircut', duration: 60 },
				{ id: 2, name: 'Beard Trim', duration: 30 },
				{ id: 3, name: 'Hair Wash', duration: 15 }
			];
			
			// Initialize default schedule
			handleReset();
		}
	});

	// Drag and drop handlers
	const handleDragStart = (slot: TimeSlot) => {
		draggedSlot = slot;
	};

	const handleDragOver = (event: DragEvent, day: string) => {
		event.preventDefault();
		dropZone = day;
	};

	const handleDrop = (event: DragEvent, day: string) => {
		event.preventDefault();
		if (draggedSlot && day !== selectedDay) {
			// Move slot to different day
			businessHours[selectedDay].timeSlots = businessHours[selectedDay].timeSlots.filter(
				slot => slot.id !== draggedSlot!.id
			);
			businessHours[day].timeSlots.push({ ...draggedSlot, id: `slot-${Date.now()}` });
			isDirty = true;
			toast.success(`Time slot moved to ${day}`);
		}
		draggedSlot = null;
		dropZone = null;
	};
</script>

<!-- Business Hours Manager Interface -->
<div class="space-y-6" class:compact={compactMode}>
	{#if showHeader}
		<!-- Header Section -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight flex items-center gap-2">
					<Clock class="h-8 w-8 text-primary" />
					Business Hours
				</h1>
				<p class="text-muted-foreground">Configure your operating schedule and availability</p>
			</div>
			
			<div class="flex items-center gap-2">
				<!-- Language Toggle -->
				<Button
					variant="outline"
					size="sm"
					onclick={() => language = language === 'en' ? 'ar' : 'en'}
				>
					<Globe class="h-4 w-4" />
					{language === 'en' ? 'العربية' : 'English'}
				</Button>
				
				<!-- Time Format Toggle -->
				<Button
					variant="outline"
					size="sm"
					onclick={() => timeFormat = timeFormat === '12h' ? '24h' : '12h'}
				>
					<Clock class="h-4 w-4" />
					{timeFormat === '12h' ? '24H' : '12H'}
				</Button>
				
				<!-- Preview Toggle -->
				<Button
					variant="outline"
					size="sm"
					onclick={() => showPreview = !showPreview}
				>
					{showPreview ? <EyeOff class="h-4 w-4" /> : <Eye class="h-4 w-4" />}
					Preview
				</Button>
				
				<!-- Export/Import -->
				<div class="flex items-center gap-1">
					<Button variant="outline" size="sm" onclick={exportSchedule}>
						<Download class="h-4 w-4" />
					</Button>
					<label class="cursor-pointer">
						<Button variant="outline" size="sm" as="div">
							<Upload class="h-4 w-4" />
						</Button>
						<input 
							type="file" 
							accept=".json" 
							onchange={importSchedule} 
							class="hidden"
						/>
					</label>
				</div>
				
				<!-- Save Button -->
				<Button 
					class="btn-premium hover-lift" 
					onclick={handleSave}
					disabled={!isDirty || isLoading}
				>
					{#if isLoading}
						<RefreshCw class="h-4 w-4 animate-spin" />
					{:else}
						<Save class="h-4 w-4" />
					{/if}
					Save Changes
				</Button>
			</div>
		</div>
	{/if}

	<!-- Main Tabs -->
	<Tabs bind:value={activeTab} class="w-full">
		<TabsList class="grid w-full grid-cols-5 glass-effect">
			<TabsTrigger value="weekly" class="flex items-center gap-2">
				<CalendarDays class="h-4 w-4" />
				Weekly
			</TabsTrigger>
			<TabsTrigger value="seasonal" class="flex items-center gap-2">
				<Sun class="h-4 w-4" />
				Seasonal
			</TabsTrigger>
			<TabsTrigger value="holidays" class="flex items-center gap-2">
				<Star class="h-4 w-4" />
				Holidays
			</TabsTrigger>
			<TabsTrigger value="templates" class="flex items-center gap-2">
				<Archive class="h-4 w-4" />
				Templates
			</TabsTrigger>
			<TabsTrigger value="settings" class="flex items-center gap-2">
				<Settings class="h-4 w-4" />
				Settings
			</TabsTrigger>
		</TabsList>

		<!-- Weekly Schedule Tab -->
		<TabsContent value="weekly" class="space-y-6">
			<!-- Status Bar -->
			{#if conflictingSchedules.length > 0}
				<Card class="border-warning bg-warning/5">
					<CardContent class="p-4">
						<div class="flex items-start gap-3">
							<AlertTriangle class="h-5 w-5 text-warning mt-0.5" />
							<div>
								<h4 class="font-medium text-warning">Schedule Conflicts Detected</h4>
								<ul class="mt-2 space-y-1 text-sm text-warning/80">
									{#each conflictingSchedules as conflict}
										<li>• {conflict.day}: {conflict.message}</li>
									{/each}
								</ul>
							</div>
						</div>
					</CardContent>
				</Card>
			{/if}

			<!-- Quick Stats -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<Card class="card-premium">
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">Total Hours/Week</p>
								<p class="text-2xl font-bold">{totalWeeklyHours.toFixed(1)}h</p>
							</div>
							<TrendingUp class="h-8 w-8 text-primary/20" />
						</div>
					</CardContent>
				</Card>
				
				<Card class="card-premium">
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">Open Days</p>
								<p class="text-2xl font-bold">
									{Object.values(businessHours).filter(day => day.isOpen).length}/7
								</p>
							</div>
							<CalendarDays class="h-8 w-8 text-success/20" />
						</div>
					</CardContent>
				</Card>
				
				<Card class="card-premium">
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">Time Slots</p>
								<p class="text-2xl font-bold">
									{Object.values(businessHours).reduce((total, day) => total + day.timeSlots.length, 0)}
								</p>
							</div>
							<Timer class="h-8 w-8 text-info/20" />
						</div>
					</CardContent>
				</Card>
				
				<Card class="card-premium">
					<CardContent class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-muted-foreground">Capacity/Day</p>
								<p class="text-2xl font-bold">
									{Math.round(Object.values(businessHours).reduce((total, day) => total + day.capacity, 0) / 7)}
								</p>
							</div>
							<Users class="h-8 w-8 text-brand/20" />
						</div>
					</CardContent>
				</Card>
			</div>

			<!-- Main Schedule Editor -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Days Sidebar -->
				<Card class="card-premium">
					<CardHeader>
						<CardTitle class="flex items-center gap-2">
							<CalendarDays class="h-5 w-5" />
							Weekly Overview
						</CardTitle>
					</CardHeader>
					<CardContent class="space-y-2">
						{#each weeklyOverview as day}
							<button
								class="w-full p-3 rounded-lg border transition-all hover:bg-muted/50 {selectedDay === day.key ? 'bg-primary/10 border-primary' : 'border-border'}"
								onclick={() => selectedDay = day.key}
								ondragover={(e) => handleDragOver(e, day.key)}
								ondrop={(e) => handleDrop(e, day.key)}
							>
								<div class="flex items-center justify-between">
									<div class="text-left">
										<p class="font-medium">
											{language === 'en' ? day.label : day.labelAr}
										</p>
										<p class="text-xs text-muted-foreground">
											{day.isOpen ? `${day.totalHours.toFixed(1)}h` : 'Closed'}
										</p>
									</div>
									<div class="flex items-center gap-2">
										{#if day.isOpen}
											<Badge variant="success" class="text-xs">
												{day.slots} slots
											</Badge>
										{:else}
											<Badge variant="secondary" class="text-xs">
												Closed
											</Badge>
										{/if}
									</div>
								</div>
							</button>
						{/each}
					</CardContent>
				</Card>

				<!-- Day Schedule Editor -->
				<Card class="lg:col-span-2 card-premium">
					<CardHeader>
						<div class="flex items-center justify-between">
							<CardTitle class="flex items-center gap-2">
								<Clock class="h-5 w-5" />
								{DAYS_OF_WEEK.find(d => d.key === selectedDay)?.label} Schedule
							</CardTitle>
							<div class="flex items-center gap-2">
								<Switch
									checked={currentDaySchedule.isOpen}
									onCheckedChange={(checked) => {
										businessHours[selectedDay].isOpen = checked;
										isDirty = true;
									}}
								/>
								<Label class="text-sm">Open</Label>
							</div>
						</div>
					</CardHeader>
					
					{#if currentDaySchedule.isOpen}
						<CardContent class="space-y-6">
							<!-- Quick Actions -->
							<div class="flex items-center gap-2 flex-wrap">
								<Button
									variant="outline"
									size="sm"
									onclick={() => addTimeSlot(selectedDay)}
								>
									<Plus class="h-4 w-4" />
									Add Slot
								</Button>
								<Button
									variant="outline"
									size="sm"
									onclick={() => addBreakTime(selectedDay)}
								>
									<Coffee class="h-4 w-4" />
									Add Break
								</Button>
								<Select>
									<SelectTrigger class="w-32">
										<SelectValue placeholder="Copy from..." />
									</SelectTrigger>
									<SelectContent>
										{#each DAYS_OF_WEEK.filter(d => d.key !== selectedDay) as day}
											<SelectItem 
												value={day.key}
												onclick={() => copySchedule(day.key, selectedDay)}
											>
												{day.label}
											</SelectItem>
										{/each}
									</SelectContent>
								</Select>
							</div>

							<!-- Time Slots -->
							<div class="space-y-4">
								<div class="flex items-center justify-between">
									<h4 class="font-medium">Working Hours</h4>
									<Badge variant="outline">
										{currentDaySchedule.timeSlots.length} slots
									</Badge>
								</div>
								
								{#if currentDaySchedule.timeSlots.length === 0}
									<div class="text-center py-8 text-muted-foreground">
										<Clock class="h-12 w-12 mx-auto mb-2 opacity-50" />
										<p>No time slots configured</p>
										<Button
											variant="outline"
											size="sm"
											class="mt-2"
											onclick={() => addTimeSlot(selectedDay)}
										>
											<Plus class="h-4 w-4" />
											Add First Slot
										</Button>
									</div>
								{:else}
									<div class="space-y-2">
										{#each currentDaySchedule.timeSlots as slot, index}
											<div 
												class="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors"
												draggable="true"
												ondragstart={() => handleDragStart(slot)}
											>
												<div class="flex-1 grid grid-cols-2 gap-2">
													<Input
														type="time"
														bind:value={slot.startTime}
														class="text-sm"
														onchange={() => isDirty = true}
													/>
													<Input
														type="time"
														bind:value={slot.endTime}
														class="text-sm"
														onchange={() => isDirty = true}
													/>
												</div>
												
												{#if settings.enableCapacityManagement}
													<div class="flex items-center gap-2">
														<Users class="h-4 w-4 text-muted-foreground" />
														<Input
															type="number"
															bind:value={slot.capacity}
															min="1"
															max="50"
															class="w-16 text-sm"
															onchange={() => isDirty = true}
														/>
													</div>
												{/if}
												
												<div class="flex items-center gap-1">
													<Button
														variant="ghost"
														size="sm"
														onclick={() => removeTimeSlot(selectedDay, slot.id)}
													>
														<Trash2 class="h-4 w-4" />
													</Button>
												</div>
											</div>
										{/each}
									</div>
								{/if}
							</div>

							<!-- Break Times -->
							{#if currentDaySchedule.breakTimes.length > 0}
								<div class="space-y-4">
									<div class="flex items-center justify-between">
										<h4 class="font-medium">Break Times</h4>
										<Badge variant="outline" class="bg-orange-50">
											{currentDaySchedule.breakTimes.length} breaks
										</Badge>
									</div>
									
									<div class="space-y-2">
										{#each currentDaySchedule.breakTimes as breakTime}
											<div class="flex items-center gap-3 p-3 border rounded-lg bg-orange-50/50">
												<Coffee class="h-4 w-4 text-orange-600" />
												<div class="flex-1 grid grid-cols-2 gap-2">
													<Input
														type="time"
														bind:value={breakTime.startTime}
														class="text-sm"
														onchange={() => isDirty = true}
													/>
													<Input
														type="time"
														bind:value={breakTime.endTime}
														class="text-sm"
														onchange={() => isDirty = true}
													/>
												</div>
												<Input
													bind:value={breakTime.notes}
													placeholder="Break notes..."
													class="flex-1 text-sm"
													onchange={() => isDirty = true}
												/>
												<Button
													variant="ghost"
													size="sm"
													onclick={() => {
														currentDaySchedule.breakTimes = currentDaySchedule.breakTimes.filter(b => b.id !== breakTime.id);
														isDirty = true;
													}}
												>
													<Trash2 class="h-4 w-4" />
												</Button>
											</div>
										{/each}
									</div>
								</div>
							{/if}

							<!-- Day Settings -->
							<div class="space-y-4 pt-4 border-t border-border">
								<h4 class="font-medium">Day Settings</h4>
								
								<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
									{#if settings.enableCapacityManagement}
										<div class="space-y-2">
											<Label>Daily Capacity</Label>
											<Input
												type="number"
												bind:value={currentDaySchedule.capacity}
												min="1"
												max="100"
												onchange={() => isDirty = true}
											/>
										</div>
									{/if}
									
									<div class="space-y-2">
										<Label>Notes</Label>
										<Input
											bind:value={currentDaySchedule.notes}
											placeholder="Special notes for this day..."
											onchange={() => isDirty = true}
										/>
									</div>
								</div>
							</div>
						</CardContent>
					{:else}
						<CardContent class="text-center py-12">
							<XCircle class="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
							<h3 class="text-lg font-medium mb-2">Closed</h3>
							<p class="text-muted-foreground mb-4">
								This day is marked as closed. Enable the toggle above to set operating hours.
							</p>
							{#if currentDaySchedule.notes}
								<Badge variant="outline" class="bg-yellow-50">
									{currentDaySchedule.notes}
								</Badge>
							{/if}
						</CardContent>
					{/if}
				</Card>
			</div>

			<!-- Prayer Time Integration -->
			{#if settings.enablePrayerTimeIntegration}
				<Card class="card-premium">
					<CardHeader>
						<CardTitle class="flex items-center gap-2">
							<Moon class="h-5 w-5" />
							Prayer Time Integration
						</CardTitle>
						<CardDescription>
							Automatically avoid scheduling during prayer times
						</CardDescription>
					</CardHeader>
					<CardContent>
						<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
							{#each PRAYER_TIMES as prayer}
								<div class="text-center p-3 border rounded-lg">
									<p class="text-sm font-medium">{prayer.name}</p>
									<p class="text-xs text-muted-foreground" dir="rtl">{prayer.nameAr}</p>
									<p class="text-sm font-mono mt-1">{formatTime(prayer.time)}</p>
								</div>
							{/each}
						</div>
					</CardContent>
				</Card>
			{/if}
		</TabsContent>

		<!-- Seasonal Schedules Tab -->
		<TabsContent value="seasonal" class="space-y-6">
			<div class="flex items-center justify-between">
				<div>
					<h3 class="text-lg font-semibold">Seasonal Schedules</h3>
					<p class="text-sm text-muted-foreground">
						Configure different schedules for different seasons or periods
					</p>
				</div>
				<Button
					onclick={() => showSeasonalDialog = true}
					class="btn-premium"
				>
					<Plus class="h-4 w-4" />
					Add Seasonal Schedule
				</Button>
			</div>

			{#if seasonalSchedules.length === 0}
				<Card class="text-center py-12">
					<CardContent>
						<Sun class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
						<h3 class="text-lg font-medium mb-2">No seasonal schedules</h3>
						<p class="text-muted-foreground mb-4">
							Create seasonal schedules for Ramadan, summer hours, or special periods
						</p>
						<Button onclick={() => showSeasonalDialog = true}>
							<Plus class="h-4 w-4" />
							Create First Schedule
						</Button>
					</CardContent>
				</Card>
			{:else}
				<div class="grid gap-4">
					{#each seasonalSchedules as schedule}
						<Card class="card-premium">
							<CardContent class="p-6">
								<div class="flex items-center justify-between">
									<div>
										<h4 class="font-semibold">{schedule.name}</h4>
										{#if schedule.nameAr}
											<p class="text-sm text-muted-foreground" dir="rtl">{schedule.nameAr}</p>
										{/if}
										<p class="text-sm text-muted-foreground mt-1">
											{schedule.startDate} to {schedule.endDate}
										</p>
									</div>
									<div class="flex items-center gap-2">
										<Badge variant={schedule.isActive ? 'success' : 'secondary'}>
											{schedule.isActive ? 'Active' : 'Inactive'}
										</Badge>
										<Button variant="ghost" size="sm">
											<Edit class="h-4 w-4" />
										</Button>
										<Button variant="ghost" size="sm">
											<Trash2 class="h-4 w-4" />
										</Button>
									</div>
								</div>
							</CardContent>
						</Card>
					{/each}
				</div>
			{/if}
		</TabsContent>

		<!-- Holidays Tab -->
		<TabsContent value="holidays" class="space-y-6">
			<div>
				<h3 class="text-lg font-semibold">Holiday Management</h3>
				<p class="text-sm text-muted-foreground">
					Manage Saudi national holidays and custom exceptions
				</p>
			</div>

			<!-- Upcoming Holidays -->
			<Card class="card-premium">
				<CardHeader>
					<CardTitle class="flex items-center gap-2">
						<Star class="h-5 w-5" />
						Upcoming Holidays
					</CardTitle>
				</CardHeader>
				<CardContent>
					{#if upcomingHolidays.length === 0}
						<p class="text-muted-foreground text-center py-4">No upcoming holidays</p>
					{:else}
						<div class="space-y-3">
							{#each upcomingHolidays as holiday}
								<div class="flex items-center justify-between p-3 border rounded-lg">
									<div>
										<p class="font-medium">{holiday.name}</p>
										{#if holiday.nameAr}
											<p class="text-sm text-muted-foreground" dir="rtl">{holiday.nameAr}</p>
										{/if}
									</div>
									<div class="text-right">
										<p class="text-sm font-medium">{holiday.date}</p>
										{#if holiday.duration}
											<p class="text-xs text-muted-foreground">{holiday.duration} days</p>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>

			<!-- Custom Exceptions -->
			<Card class="card-premium">
				<CardHeader>
					<div class="flex items-center justify-between">
						<CardTitle class="flex items-center gap-2">
							<CalendarIcon class="h-5 w-5" />
							Custom Exceptions
						</CardTitle>
						<Button
							onclick={() => showHolidayDialog = true}
							variant="outline"
						>
							<Plus class="h-4 w-4" />
							Add Exception
						</Button>
					</div>
				</CardHeader>
				<CardContent>
					{#if holidayExceptions.length === 0}
						<p class="text-muted-foreground text-center py-8">
							No custom exceptions configured
						</p>
					{:else}
						<div class="space-y-2">
							{#each holidayExceptions as exception}
								<div class="flex items-center justify-between p-3 border rounded-lg">
									<div>
										<p class="font-medium">{exception.name}</p>
										<p class="text-sm text-muted-foreground">{exception.date}</p>
									</div>
									<div class="flex items-center gap-2">
										<Badge variant={exception.isClosed ? 'destructive' : 'warning'}>
											{exception.isClosed ? 'Closed' : 'Modified'}
										</Badge>
										<Button variant="ghost" size="sm">
											<Edit class="h-4 w-4" />
										</Button>
										<Button variant="ghost" size="sm">
											<Trash2 class="h-4 w-4" />
										</Button>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</CardContent>
			</Card>
		</TabsContent>

		<!-- Templates Tab -->
		<TabsContent value="templates" class="space-y-6">
			<div>
				<h3 class="text-lg font-semibold">Schedule Templates</h3>
				<p class="text-sm text-muted-foreground">
					Save and reuse common schedule configurations
				</p>
			</div>

			<!-- Template Actions -->
			<Card class="card-premium">
				<CardHeader>
					<CardTitle>Quick Templates</CardTitle>
				</CardHeader>
				<CardContent>
					<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
						<Button
							variant="outline"
							class="p-4 h-auto flex-col gap-2"
							onclick={() => {
								// Apply standard business hours template
								Object.keys(businessHours).forEach(day => {
									if (day === 'friday') {
										businessHours[day] = { isOpen: false, timeSlots: [], breakTimes: [], capacity: 10, notes: 'Closed for Friday prayers' };
									} else {
										businessHours[day] = {
											isOpen: true,
											timeSlots: [{ id: `standard-${day}`, startTime: '09:00', endTime: '17:00' }],
											breakTimes: [{ id: `break-${day}`, startTime: '12:00', endTime: '13:00', isBreak: true }],
											capacity: 10,
											notes: ''
										};
									}
								});
								isDirty = true;
								toast.success('Standard hours template applied');
							}}
						>
							<Clock class="h-6 w-6" />
							<span class="text-sm">Standard Hours</span>
							<span class="text-xs text-muted-foreground">9 AM - 5 PM</span>
						</Button>

						<Button
							variant="outline"
							class="p-4 h-auto flex-col gap-2"
							onclick={() => {
								// Apply extended hours template
								Object.keys(businessHours).forEach(day => {
									if (day === 'friday') {
										businessHours[day] = { isOpen: false, timeSlots: [], breakTimes: [], capacity: 10, notes: 'Closed for Friday prayers' };
									} else {
										businessHours[day] = {
											isOpen: true,
											timeSlots: [{ id: `extended-${day}`, startTime: '08:00', endTime: '20:00' }],
											breakTimes: [
												{ id: `break1-${day}`, startTime: '12:00', endTime: '13:00', isBreak: true },
												{ id: `break2-${day}`, startTime: '16:00', endTime: '16:30', isBreak: true }
											],
											capacity: 15,
											notes: ''
										};
									}
								});
								isDirty = true;
								toast.success('Extended hours template applied');
							}}
						>
							<Sun class="h-6 w-6" />
							<span class="text-sm">Extended Hours</span>
							<span class="text-xs text-muted-foreground">8 AM - 8 PM</span>
						</Button>

						<Button
							variant="outline"
							class="p-4 h-auto flex-col gap-2"
							onclick={() => {
								// Apply weekend only template
								Object.keys(businessHours).forEach(day => {
									if (['saturday', 'sunday'].includes(day)) {
										businessHours[day] = {
											isOpen: true,
											timeSlots: [{ id: `weekend-${day}`, startTime: '10:00', endTime: '22:00' }],
											breakTimes: [{ id: `break-${day}`, startTime: '15:00', endTime: '16:00', isBreak: true }],
											capacity: 20,
											notes: 'Weekend hours'
										};
									} else {
										businessHours[day] = { isOpen: false, timeSlots: [], breakTimes: [], capacity: 10, notes: 'Weekday closed' };
									}
								});
								isDirty = true;
								toast.success('Weekend only template applied');
							}}
						>
							<Calendar class="h-6 w-6" />
							<span class="text-sm">Weekend Only</span>
							<span class="text-xs text-muted-foreground">Sat-Sun Only</span>
						</Button>

						<Button
							variant="outline"
							class="p-4 h-auto flex-col gap-2"
							onclick={() => showTemplateDialog = true}
						>
							<Plus class="h-6 w-6" />
							<span class="text-sm">Save Current</span>
							<span class="text-xs text-muted-foreground">As Template</span>
						</Button>
					</div>
				</CardContent>
			</Card>

			<!-- Saved Templates -->
			{#if Object.keys(templates).length > 0}
				<Card class="card-premium">
					<CardHeader>
						<CardTitle>Saved Templates</CardTitle>
					</CardHeader>
					<CardContent>
						<div class="space-y-2">
							{#each Object.entries(templates) as [name, template]}
								<div class="flex items-center justify-between p-3 border rounded-lg">
									<div>
										<p class="font-medium">{name}</p>
										<p class="text-sm text-muted-foreground">
											{Object.values(template).filter(day => day.isOpen).length} open days
										</p>
									</div>
									<div class="flex items-center gap-2">
										<Button
											variant="outline"
											size="sm"
											onclick={() => loadTemplate(name)}
										>
											<Download class="h-4 w-4" />
											Load
										</Button>
										<Button
											variant="ghost"
											size="sm"
											onclick={() => {
												delete templates[name];
												toast.success(`Template "${name}" deleted`);
											}}
										>
											<Trash2 class="h-4 w-4" />
										</Button>
									</div>
								</div>
							{/each}
						</div>
					</CardContent>
				</Card>
			{/if}
		</TabsContent>

		<!-- Settings Tab -->
		<TabsContent value="settings" class="space-y-6">
			<div>
				<h3 class="text-lg font-semibold">Advanced Settings</h3>
				<p class="text-sm text-muted-foreground">
					Configure advanced business hours features and integrations
				</p>
			</div>

			<!-- General Settings -->
			<Card class="card-premium">
				<CardHeader>
					<CardTitle class="flex items-center gap-2">
						<Settings class="h-5 w-5" />
						General Settings
					</CardTitle>
				</CardHeader>
				<CardContent class="space-y-6">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div class="space-y-2">
							<Label>Slot Duration (minutes)</Label>
							<Input
								type="number"
								bind:value={settings.slotDuration}
								min="15"
								max="480"
								step="15"
							/>
						</div>
						
						<div class="space-y-2">
							<Label>Buffer Time (minutes)</Label>
							<Input
								type="number"
								bind:value={settings.bufferTime}
								min="0"
								max="60"
								step="5"
							/>
						</div>
						
						<div class="space-y-2">
							<Label>Minimum Booking Notice (minutes)</Label>
							<Input
								type="number"
								bind:value={settings.minimumBookingNotice}
								min="0"
								max="1440"
								step="15"
							/>
						</div>
						
						<div class="space-y-2">
							<Label>Maximum Advance Booking (days)</Label>
							<Input
								type="number"
								bind:value={settings.maximumAdvanceBooking}
								min="1"
								max="365"
							/>
						</div>
					</div>
				</CardContent>
			</Card>

			<!-- Feature Toggles -->
			<Card class="card-premium">
				<CardHeader>
					<CardTitle class="flex items-center gap-2">
						<Zap class="h-5 w-5" />
						Feature Controls
					</CardTitle>
				</CardHeader>
				<CardContent class="space-y-4">
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Prayer Time Integration</Label>
							<p class="text-sm text-muted-foreground">Automatically avoid prayer times when scheduling</p>
						</div>
						<Switch
							bind:checked={settings.enablePrayerTimeIntegration}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Ramadan Schedule</Label>
							<p class="text-sm text-muted-foreground">Apply special Ramadan working hours</p>
						</div>
						<Switch
							bind:checked={settings.enableRamadanSchedule}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Capacity Management</Label>
							<p class="text-sm text-muted-foreground">Enable per-slot capacity limits</p>
						</div>
						<Switch
							bind:checked={settings.enableCapacityManagement}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Service-Specific Hours</Label>
							<p class="text-sm text-muted-foreground">Different hours for different services</p>
						</div>
						<Switch
							bind:checked={settings.enableServiceSpecificHours}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Auto-Close on Holidays</Label>
							<p class="text-sm text-muted-foreground">Automatically close on national holidays</p>
						</div>
						<Switch
							bind:checked={settings.autoCloseOnHolidays}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Seasonal Adjustments</Label>
							<p class="text-sm text-muted-foreground">Enable automatic seasonal schedule changes</p>
						</div>
						<Switch
							bind:checked={settings.enableSeasonalAdjustments}
						/>
					</div>
				</CardContent>
			</Card>

			<!-- Notification Settings -->
			<Card class="card-premium">
				<CardHeader>
					<CardTitle class="flex items-center gap-2">
						<Bell class="h-5 w-5" />
						Notifications
					</CardTitle>
				</CardHeader>
				<CardContent class="space-y-4">
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Break Reminders</Label>
							<p class="text-sm text-muted-foreground">Notify staff of upcoming breaks</p>
						</div>
						<Switch
							bind:checked={settings.enableBreakReminders}
						/>
					</div>
					
					<div class="flex items-center justify-between">
						<div>
							<Label class="text-base">Holiday Notifications</Label>
							<p class="text-sm text-muted-foreground">Alert about upcoming holidays</p>
						</div>
						<Switch
							bind:checked={settings.enableHolidayNotifications}
						/>
					</div>
				</CardContent>
			</Card>
		</TabsContent>
	</Tabs>

	<!-- Preview Panel -->
	{#if showPreview}
		<Card class="card-premium">
			<CardHeader>
				<CardTitle class="flex items-center gap-2">
					<Eye class="h-5 w-5" />
					Schedule Preview
				</CardTitle>
				<CardDescription>
					How your schedule will appear to customers
				</CardDescription>
			</CardHeader>
			<CardContent>
				<div class="grid grid-cols-1 md:grid-cols-7 gap-4">
					{#each DAYS_OF_WEEK as day}
						<div class="text-center p-4 border rounded-lg {businessHours[day.key].isOpen ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}">
							<h4 class="font-medium text-sm mb-2">
								{language === 'en' ? day.label : day.labelAr}
							</h4>
							
							{#if businessHours[day.key].isOpen}
								<div class="space-y-1 text-xs">
									{#each businessHours[day.key].timeSlots as slot}
										<div class="bg-white rounded px-2 py-1">
											{formatTime(slot.startTime)} - {formatTime(slot.endTime)}
										</div>
									{/each}
									{#if businessHours[day.key].timeSlots.length === 0}
										<p class="text-muted-foreground">No slots</p>
									{/if}
								</div>
							{:else}
								<Badge variant="secondary" class="text-xs">Closed</Badge>
							{/if}
						</div>
					{/each}
				</div>
			</CardContent>
		</Card>
	{/if}

	<!-- Sticky Action Bar -->
	{#if isDirty}
		<div class="fixed bottom-6 right-6 z-50">
			<Card class="card-premium shadow-2xl">
				<CardContent class="p-4">
					<div class="flex items-center gap-3">
						<div class="flex items-center gap-2 text-sm text-muted-foreground">
							<Activity class="h-4 w-4" />
							Unsaved changes
						</div>
						<div class="flex items-center gap-2">
							<Button
								variant="outline"
								size="sm"
								onclick={handleReset}
							>
								Reset
							</Button>
							<Button
								size="sm"
								onclick={handleSave}
								disabled={isLoading}
								class="btn-premium"
							>
								{#if isLoading}
									<RefreshCw class="h-4 w-4 animate-spin" />
								{:else}
									<Save class="h-4 w-4" />
								{/if}
								Save Changes
							</Button>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	{/if}
</div>

<!-- Save Template Dialog -->
<Dialog bind:open={showTemplateDialog}>
	<DialogContent>
		<DialogHeader>
			<DialogTitle>Save as Template</DialogTitle>
		</DialogHeader>
		
		<form
			class="space-y-4"
			onsubmit={(e) => {
				e.preventDefault();
				const formData = new FormData(e.target as HTMLFormElement);
				const templateName = formData.get('templateName') as string;
				if (templateName) {
					saveTemplate(templateName);
					showTemplateDialog = false;
				}
			}}
		>
			<div class="space-y-2">
				<Label for="templateName">Template Name</Label>
				<Input
					id="templateName"
					name="templateName"
					placeholder="e.g., Summer Hours"
					required
				/>
			</div>
			
			<div class="flex items-center justify-end space-x-2">
				<Button variant="outline" type="button" onclick={() => showTemplateDialog = false}>
					Cancel
				</Button>
				<Button type="submit" class="btn-premium">
					Save Template
				</Button>
			</div>
		</form>
	</DialogContent>
</Dialog>

<style>
	.glass-effect {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}
	
	.compact {
		--radius: 0.375rem;
	}
	
	.compact .card-premium {
		padding: 1rem;
	}
	
	.hover-lift {
		transition: transform 0.2s ease-in-out;
	}
	
	.hover-lift:hover {
		transform: translateY(-2px);
	}
	
	.btn-premium {
		background: var(--gradient-primary);
		border: none;
		color: white;
	}
	
	.card-premium {
		background: var(--card);
		border: 1px solid var(--border);
		box-shadow: var(--shadow-md);
		border-radius: var(--radius-lg);
	}
	
	.card-premium:hover {
		box-shadow: var(--shadow-lg);
	}
	
	/* Arabic text support */
	[dir="rtl"] {
		text-align: right;
		font-family: 'Cairo', 'Tajawal', sans-serif;
	}
	
	/* Drag and drop styles */
	[draggable="true"] {
		cursor: grab;
	}
	
	[draggable="true"]:active {
		cursor: grabbing;
	}
	
	/* Animation for loading states */
	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}
	
	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
	
	/* Custom scrollbar */
	.custom-scrollbar::-webkit-scrollbar {
		width: 6px;
	}
	
	.custom-scrollbar::-webkit-scrollbar-track {
		background: var(--muted);
		border-radius: 3px;
	}
	
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: var(--muted-foreground);
		border-radius: 3px;
	}
	
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: var(--primary);
	}
</style>