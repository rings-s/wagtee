<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
  import { Badge } from '$lib/components/ui/badge';
  import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '$lib/components/ui/dialog';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { 
    ChevronLeft, 
    ChevronRight,
    Plus,
    Calendar,
    Clock,
    User,
    Phone,
    MapPin,
    DollarSign,
    Edit,
    Trash2,
    Check,
    X,
    Filter,
    Search
  } from '@lucide/svelte';
  import { api } from '$lib/services/api-client.js';

  // FIXED: Use Svelte 5 props syntax
  interface Props {
    view?: 'month' | 'week' | 'day';
    selectedDate?: Date;
  }
  
  let { view = 'week', selectedDate = new Date() }: Props = $props();

  // FIXED: Use Svelte 5 runes
  let bookings = $state<any[]>([]);
  let services = $state<any[]>([]);
  let loading = $state(true);
  let draggedBooking = $state<any>(null);
  let showBookingDialog = $state(false);
  let selectedBooking = $state<any>(null);
  let showNewBookingDialog = $state(false);
  let filterStatus = $state('');
  let searchQuery = $state('');
  let hoveredSlot = $state<{ date: Date; time: string } | null>(null);

  // Calendar state
  let currentDate = $state(new Date(selectedDate));
  let calendarDays = $state<Date[]>([]);
  let timeSlots = $state(generateTimeSlots());

  const dispatch = createEventDispatcher();

  // FIXED: Use $derived instead of $:
  const monthNames = $derived(() => [
    'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
  ]);

  const dayNames = $derived(() => ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']);

  const filteredBookings = $derived(() => bookings.filter(booking => {
    const matchesStatus = !filterStatus || booking.status === filterStatus;
    const matchesSearch = !searchQuery || 
      booking.customer?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      booking.service?.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  }));

  // Functions
  function generateTimeSlots(): string[] {
    const slots = [];
    for (let hour = 8; hour <= 20; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`);
      slots.push(`${hour.toString().padStart(2, '0')}:30`);
    }
    return slots;
  }

  function generateCalendarDays() {
    calendarDays = [];
    
    if (view === 'week') {
      const startOfWeek = new Date(currentDate);
      startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek);
        date.setDate(startOfWeek.getDate() + i);
        calendarDays.push(date);
      }
    } else if (view === 'day') {
      calendarDays = [new Date(currentDate)];
    } else {
      // Month view
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      
      // Start from Sunday of the week containing the first day
      const startDate = new Date(firstDay);
      startDate.setDate(firstDay.getDate() - firstDay.getDay());
      
      // Generate 42 days (6 weeks)
      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        calendarDays.push(date);
      }
    }
  }

  async function loadBookings() {
    loading = true;
    try {
      const startDate = new Date(Math.min(...calendarDays.map(d => d.getTime())));
      const endDate = new Date(Math.max(...calendarDays.map(d => d.getTime())));
      
      const response = await bookingsService.getAll({
        date_from: startDate.toISOString().split('T')[0],
        date_to: endDate.toISOString().split('T')[0],
        ordering: 'appointment_date,appointment_time'
      });

      if (response.success) {
        bookings = response.data.results || [];
      }
    } catch (error) {
      console.error('Error loading bookings:', error);
    } finally {
      loading = false;
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

  function getBookingsForDateAndTime(date: Date, time: string): any[] {
    const dateString = date.toISOString().split('T')[0];
    return filteredBookings.filter(booking => {
      const bookingDate = booking.appointment_date;
      const bookingTime = booking.appointment_time.substring(0, 5);
      return bookingDate === dateString && bookingTime === time;
    });
  }

  function getBookingStatusClass(status: string): string {
    const classes = {
      pending: 'bg-yellow-100 border-yellow-300 text-yellow-800',
      confirmed: 'bg-blue-100 border-blue-300 text-blue-800',
      completed: 'bg-green-100 border-green-300 text-green-800',
      cancelled: 'bg-red-100 border-red-300 text-red-800',
      in_progress: 'bg-purple-100 border-purple-300 text-purple-800'
    };
    return classes[status] || 'bg-gray-100 border-gray-300 text-gray-800';
  }

  function getStatusLabel(status: string): string {
    const labels = {
      pending: 'قيد الانتظار',
      confirmed: 'مؤكد',
      completed: 'مكتمل',
      cancelled: 'ملغي',
      in_progress: 'قيد التنفيذ'
    };
    return labels[status] || status;
  }

  // Drag and Drop Functions
  function handleDragStart(event: DragEvent, booking: any) {
    if (event.dataTransfer) {
      draggedBooking = booking;
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/html', '');
    }
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move';
    }
  }

  function handleDrop(event: DragEvent, date: Date, time: string) {
    event.preventDefault();
    if (draggedBooking) {
      moveBooking(draggedBooking, date, time);
      draggedBooking = null;
    }
  }

  async function moveBooking(booking: any, newDate: Date, newTime: string) {
    try {
      const response = await bookingsService.updateStatus(booking.id, {
        appointment_date: newDate.toISOString().split('T')[0],
        appointment_time: newTime
      });

      if (response.success) {
        await loadBookings();
        dispatch('bookingMoved', { booking, newDate, newTime });
      }
    } catch (error) {
      console.error('Error moving booking:', error);
    }
  }

  function navigateCalendar(direction: 'prev' | 'next') {
    const newDate = new Date(currentDate);
    
    if (view === 'month') {
      newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1));
    } else if (view === 'week') {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setDate(currentDate.getDate() + (direction === 'next' ? 1 : -1));
    }
    
    currentDate = newDate;
    generateCalendarDays();
    loadBookings();
  }

  function selectBooking(booking: any) {
    selectedBooking = booking;
    showBookingDialog = true;
  }

  async function updateBookingStatus(bookingId: number, status: string) {
    try {
      const response = await bookingsService.updateStatus(bookingId, status);
      if (response.success) {
        await loadBookings();
        showBookingDialog = false;
        dispatch('bookingUpdated', { bookingId, status });
      }
    } catch (error) {
      console.error('Error updating booking status:', error);
    }
  }

  function createNewBooking(date: Date, time: string) {
    selectedBooking = {
      appointment_date: date.toISOString().split('T')[0],
      appointment_time: time,
      status: 'pending'
    };
    showNewBookingDialog = true;
  }

  onMount(() => {
    generateCalendarDays();
    loadBookings();
    loadServices();
  });

  // Watch for view or date changes
  $: if (view || currentDate) {
    generateCalendarDays();
    loadBookings();
  }
</script>

<div class="space-y-4">
  <!-- Header Controls -->
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2">
        <Button variant="outline" size="sm" on:click={() => navigateCalendar('prev')}>
          <ChevronRight class="h-4 w-4" />
        </Button>
        
        <h2 class="text-lg font-semibold">
          {#if view === 'month'}
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          {:else if view === 'week'}
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          {:else}
            {dayNames[currentDate.getDay()]} {currentDate.getDate()} {monthNames[currentDate.getMonth()]}
          {/if}
        </h2>
        
        <Button variant="outline" size="sm" on:click={() => navigateCalendar('next')}>
          <ChevronLeft class="h-4 w-4" />
        </Button>
      </div>

      <!-- View Selector -->
      <div class="flex border rounded-lg">
        <Button 
          variant={view === 'day' ? 'default' : 'ghost'} 
          size="sm"
          on:click={() => view = 'day'}
        >
          يوم
        </Button>
        <Button 
          variant={view === 'week' ? 'default' : 'ghost'} 
          size="sm"
          on:click={() => view = 'week'}
        >
          أسبوع
        </Button>
        <Button 
          variant={view === 'month' ? 'default' : 'ghost'} 
          size="sm"
          on:click={() => view = 'month'}
        >
          شهر
        </Button>
      </div>
    </div>

    <!-- Filters and Actions -->
    <div class="flex items-center gap-2">
      <div class="flex items-center gap-2">
        <Input
          placeholder="البحث..."
          bind:value={searchQuery}
          class="w-48"
        />
        
        <select 
          bind:value={filterStatus}
          class="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">كل الحالات</option>
          <option value="pending">قيد الانتظار</option>
          <option value="confirmed">مؤكد</option>
          <option value="completed">مكتمل</option>
          <option value="cancelled">ملغي</option>
        </select>
      </div>
      
      <Button size="sm" on:click={() => showNewBookingDialog = true}>
        <Plus class="h-4 w-4 ml-2" />
        حجز جديد
      </Button>
    </div>
  </div>

  <!-- Calendar Grid -->
  {#if view === 'month'}
    <!-- Month View -->
    <Card>
      <CardContent class="p-0">
        <!-- Month Header -->
        <div class="grid grid-cols-7 border-b">
          {#each dayNames as dayName}
            <div class="p-3 text-center font-medium text-sm border-l last:border-l-0">
              {dayName}
            </div>
          {/each}
        </div>
        
        <!-- Month Days -->
        <div class="grid grid-cols-7">
          {#each calendarDays as date, index}
            <div 
              class="min-h-[100px] border-b border-l last:border-l-0 p-2 relative"
              class:bg-muted={date.getMonth() !== currentDate.getMonth()}
            >
              <div class="text-sm font-medium mb-2">
                {date.getDate()}
              </div>
              
              <!-- Day's bookings -->
              <div class="space-y-1">
                {#each getBookingsForDateAndTime(date, '').slice(0, 3) as booking}
                  <div 
                    class="text-xs p-1 rounded cursor-pointer {getBookingStatusClass(booking.status)}"
                    on:click={() => selectBooking(booking)}
                  >
                    {booking.customer?.name} - {booking.appointment_time?.substring(0, 5)}
                  </div>
                {/each}
                
                {#if getBookingsForDateAndTime(date, '').length > 3}
                  <div class="text-xs text-muted-foreground">
                    +{getBookingsForDateAndTime(date, '').length - 3} المزيد
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </CardContent>
    </Card>
  {:else}
    <!-- Week/Day View -->
    <Card>
      <CardContent class="p-0">
        <div class="flex">
          <!-- Time Column -->
          <div class="w-20 border-l">
            <div class="h-12 border-b flex items-center justify-center text-sm font-medium">
              الوقت
            </div>
            {#each timeSlots as time}
              <div class="h-16 border-b flex items-center justify-center text-sm text-muted-foreground">
                {time}
              </div>
            {/each}
          </div>
          
          <!-- Days Columns -->
          {#each calendarDays as date}
            <div class="flex-1 border-l last:border-l-0">
              <!-- Day Header -->
              <div class="h-12 border-b flex items-center justify-center text-sm font-medium bg-muted/20">
                <div class="text-center">
                  <div>{dayNames[date.getDay()]}</div>
                  <div class="text-lg font-bold">{date.getDate()}</div>
                </div>
              </div>
              
              <!-- Time Slots -->
              {#each timeSlots as time}
                <div 
                  class="h-16 border-b relative group"
                  class:bg-blue-50={hoveredSlot?.date.getTime() === date.getTime() && hoveredSlot?.time === time}
                  on:dragover={handleDragOver}
                  on:drop={(e) => handleDrop(e, date, time)}
                  on:mouseenter={() => hoveredSlot = { date, time }}
                  on:mouseleave={() => hoveredSlot = null}
                >
                  <!-- Bookings in this slot -->
                  {#each getBookingsForDateAndTime(date, time) as booking}
                    <div 
                      class="absolute inset-x-1 top-1 bottom-1 rounded text-xs p-1 cursor-move select-none {getBookingStatusClass(booking.status)}"
                      draggable="true"
                      on:dragstart={(e) => handleDragStart(e, booking)}
                      on:click={() => selectBooking(booking)}
                    >
                      <div class="font-medium truncate">{booking.customer?.name}</div>
                      <div class="truncate">{booking.service?.name}</div>
                    </div>
                  {/each}
                  
                  <!-- Add booking button -->
                  {#if getBookingsForDateAndTime(date, time).length === 0}
                    <button 
                      class="absolute inset-0 w-full h-full opacity-0 group-hover:opacity-100 bg-primary/10 flex items-center justify-center transition-opacity"
                      on:click={() => createNewBooking(date, time)}
                    >
                      <Plus class="h-4 w-4 text-primary" />
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          {/each}
        </div>
      </CardContent>
    </Card>
  {/if}

  <!-- Loading State -->
  {#if loading}
    <div class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      <span class="mr-2">جاري تحميل الحجوزات...</span>
    </div>
  {/if}
</div>

<!-- Booking Details Dialog -->
<Dialog bind:open={showBookingDialog}>
  <DialogContent class="max-w-md">
    <DialogHeader>
      <DialogTitle>تفاصيل الحجز</DialogTitle>
    </DialogHeader>
    
    {#if selectedBooking}
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label class="text-sm font-medium">العميل</Label>
            <div class="flex items-center mt-1">
              <User class="h-4 w-4 ml-2 text-muted-foreground" />
              {selectedBooking.customer?.name}
            </div>
          </div>
          
          <div>
            <Label class="text-sm font-medium">الهاتف</Label>
            <div class="flex items-center mt-1">
              <Phone class="h-4 w-4 ml-2 text-muted-foreground" />
              {selectedBooking.customer?.phone_number}
            </div>
          </div>
        </div>
        
        <div>
          <Label class="text-sm font-medium">الخدمة</Label>
          <div class="mt-1">{selectedBooking.service?.name}</div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <Label class="text-sm font-medium">التاريخ</Label>
            <div class="flex items-center mt-1">
              <Calendar class="h-4 w-4 ml-2 text-muted-foreground" />
              {new Date(selectedBooking.appointment_date).toLocaleDateString('ar-SA')}
            </div>
          </div>
          
          <div>
            <Label class="text-sm font-medium">الوقت</Label>
            <div class="flex items-center mt-1">
              <Clock class="h-4 w-4 ml-2 text-muted-foreground" />
              {selectedBooking.appointment_time?.substring(0, 5)}
            </div>
          </div>
        </div>
        
        <div>
          <Label class="text-sm font-medium">السعر</Label>
          <div class="flex items-center mt-1">
            <DollarSign class="h-4 w-4 ml-2 text-muted-foreground" />
            {new Intl.NumberFormat('ar-SA', { style: 'currency', currency: 'SAR' }).format(selectedBooking.total_price)}
          </div>
        </div>
        
        <div>
          <Label class="text-sm font-medium">الحالة</Label>
          <div class="mt-1">
            <Badge variant={selectedBooking.status === 'completed' ? 'default' : 
                          selectedBooking.status === 'pending' ? 'outline' :
                          selectedBooking.status === 'cancelled' ? 'destructive' : 'secondary'}>
              {getStatusLabel(selectedBooking.status)}
            </Badge>
          </div>
        </div>
        
        {#if selectedBooking.notes}
          <div>
            <Label class="text-sm font-medium">ملاحظات</Label>
            <div class="mt-1 text-sm">{selectedBooking.notes}</div>
          </div>
        {/if}
        
        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 pt-4 border-t">
          {#if selectedBooking.status === 'pending'}
            <Button 
              size="sm" 
              on:click={() => updateBookingStatus(selectedBooking.id, 'confirmed')}
            >
              <Check class="h-4 w-4 ml-2" />
              تأكيد
            </Button>
          {/if}
          
          {#if selectedBooking.status === 'confirmed'}
            <Button 
              size="sm" 
              on:click={() => updateBookingStatus(selectedBooking.id, 'completed')}
            >
              <Check class="h-4 w-4 ml-2" />
              إكمال
            </Button>
          {/if}
          
          {#if ['pending', 'confirmed'].includes(selectedBooking.status)}
            <Button 
              size="sm" 
              variant="destructive"
              on:click={() => updateBookingStatus(selectedBooking.id, 'cancelled')}
            >
              <X class="h-4 w-4 ml-2" />
              إلغاء
            </Button>
          {/if}
          
          <Button variant="outline" size="sm">
            <Edit class="h-4 w-4 ml-2" />
            تعديل
          </Button>
        </div>
      </div>
    {/if}
  </DialogContent>
</Dialog>