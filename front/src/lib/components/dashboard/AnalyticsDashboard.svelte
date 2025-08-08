<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
  import { Badge } from '$lib/components/ui/badge';
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
  import { 
    TrendingUp, 
    TrendingDown, 
    Users, 
    Calendar, 
    DollarSign, 
    Star,
    Clock,
    Target,
    BarChart3,
    PieChart,
    Activity,
    RefreshCw,
    Download,
    Filter
  } from '@lucide/svelte';
  import { api } from '$lib/services/api-client.js';

  // FIXED: Use Svelte 5 props syntax
  interface Props {
    period?: 'today' | 'week' | 'month' | 'year';
  }
  
  let { period = 'month' }: Props = $props();

  // FIXED: Use Svelte 5 runes
  let dashboardData = $state<any>(null);
  let analyticsData = $state<any>(null);
  let loading = $state(true);
  let selectedMetric = $state('revenue');
  let chartType = $state('line');

  // FIXED: Use $derived instead of $:
  const periodLabels = $derived(() => ({
    today: 'اليوم',
    week: 'هذا الأسبوع', 
    month: 'هذا الشهر',
    year: 'هذا العام'
  }));

  // Functions
  async function loadDashboardData() {
    loading = true;
    try {
      // FIXED: Use real API client
      const dashboardResponse = await api.business.getDashboardStats(period);

      if (dashboardResponse.success) {
        dashboardData = dashboardResponse.data;
        // For now, use dashboard data as analytics data
        analyticsData = dashboardResponse.data;
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      loading = false;
    }
  }

  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'SAR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount || 0);
  }

  function formatNumber(num: number): string {
    return new Intl.NumberFormat('ar-SA').format(num || 0);
  }

  function formatPercentage(num: number): string {
    const formatted = (num || 0).toFixed(1);
    return `${formatted}%`;
  }

  function getGrowthIcon(growth: number) {
    return growth >= 0 ? TrendingUp : TrendingDown;
  }

  function getGrowthColor(growth: number): string {
    if (growth > 0) return 'text-green-600';
    if (growth < 0) return 'text-red-600';
    return 'text-gray-600';
  }

  function exportData(format: 'csv' | 'excel' | 'pdf') {
    // Implement export functionality
    console.log(`Exporting as ${format}`);
  }

  // FIXED: Use $effect instead of onMount
  $effect(() => {
    loadDashboardData();
  });

  // FIXED: Use $effect to watch period changes
  $effect(() => {
    if (period) {
      loadDashboardData();
    }
  });
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold">لوحة التحليلات</h1>
      <p class="text-muted-foreground">نظرة شاملة على أداء عملك - {periodLabels[period]}</p>
    </div>
    
    <div class="flex items-center gap-2">
      <Button variant="outline" size="sm" on:click={() => exportData('excel')}>
        <Download class="h-4 w-4 ml-2" />
        تصدير البيانات
      </Button>
      
      <Button variant="outline" size="sm" on:click={loadDashboardData}>
        <RefreshCw class="h-4 w-4 ml-2" />
        تحديث
      </Button>
    </div>
  </div>

  <!-- Period Selector -->
  <Tabs bind:value={period}>
    <TabsList class="grid w-full grid-cols-4">
      <TabsTrigger value="today">اليوم</TabsTrigger>
      <TabsTrigger value="week">الأسبوع</TabsTrigger>
      <TabsTrigger value="month">الشهر</TabsTrigger>
      <TabsTrigger value="year">السنة</TabsTrigger>
    </TabsList>
  </Tabs>

  {#if loading}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each Array(8) as _}
        <Card>
          <CardContent class="p-6">
            <div class="animate-pulse">
              <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div class="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {:else if dashboardData}
    <!-- Key Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Revenue Card -->
      <Card>
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-muted-foreground">إجمالي الإيرادات</p>
              <p class="text-2xl font-bold">{formatCurrency(dashboardData.period_revenue)}</p>
              {#if dashboardData.revenue_growth !== undefined}
                <p class="text-xs {getGrowthColor(dashboardData.revenue_growth)} flex items-center mt-1">
                  <svelte:component this={getGrowthIcon(dashboardData.revenue_growth)} class="h-3 w-3 ml-1" />
                  {formatPercentage(dashboardData.revenue_growth)}
                </p>
              {/if}
            </div>
            <div class="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
              <DollarSign class="h-4 w-4 text-green-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Bookings Card -->
      <Card>
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-muted-foreground">إجمالي الحجوزات</p>
              <p class="text-2xl font-bold">{formatNumber(dashboardData.period_bookings)}</p>
              {#if dashboardData.booking_growth !== undefined}
                <p class="text-xs {getGrowthColor(dashboardData.booking_growth)} flex items-center mt-1">
                  <svelte:component this={getGrowthIcon(dashboardData.booking_growth)} class="h-3 w-3 ml-1" />
                  {formatPercentage(dashboardData.booking_growth)}
                </p>
              {/if}
            </div>
            <div class="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Calendar class="h-4 w-4 text-blue-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Customers Card -->
      <Card>
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-muted-foreground">إجمالي العملاء</p>
              <p class="text-2xl font-bold">{formatNumber(dashboardData.total_customers)}</p>
              <p class="text-xs text-muted-foreground">
                {formatPercentage(dashboardData.customer_retention_rate)} معدل الإحتفاظ
              </p>
            </div>
            <div class="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
              <Users class="h-4 w-4 text-purple-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Rating Card -->
      <Card>
        <CardContent class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-muted-foreground">التقييم المتوسط</p>
              <p class="text-2xl font-bold">{dashboardData.average_rating}</p>
              <p class="text-xs text-muted-foreground">
                {formatNumber(dashboardData.total_reviews)} تقييم
              </p>
            </div>
            <div class="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <Star class="h-4 w-4 text-yellow-600" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Status Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <Card>
        <CardContent class="p-6 text-center">
          <div class="text-2xl font-bold text-orange-600 mb-2">
            {formatNumber(dashboardData.pending_bookings)}
          </div>
          <p class="text-sm text-muted-foreground">حجوزات قيد الانتظار</p>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-6 text-center">
          <div class="text-2xl font-bold text-green-600 mb-2">
            {formatNumber(dashboardData.confirmed_bookings)}
          </div>
          <p class="text-sm text-muted-foreground">حجوزات مؤكدة</p>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-6 text-center">
          <div class="text-2xl font-bold text-blue-600 mb-2">
            {formatNumber(dashboardData.completed_bookings)}
          </div>
          <p class="text-sm text-muted-foreground">حجوزات مكتملة</p>
        </CardContent>
      </Card>

      <Card>
        <CardContent class="p-6 text-center">
          <div class="text-2xl font-bold text-red-600 mb-2">
            {formatNumber(dashboardData.cancelled_bookings)}
          </div>
          <p class="text-sm text-muted-foreground">حجوزات ملغية</p>
        </CardContent>
      </Card>
    </div>

    <!-- Charts and Analytics -->
    {#if analyticsData}
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Revenue Trend Chart -->
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center">
              <BarChart3 class="h-5 w-5 ml-2" />
              اتجاه الإيرادات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="h-64 flex items-center justify-center bg-muted/20 rounded">
              <p class="text-muted-foreground">مخطط الإيرادات</p>
              <!-- Replace with actual chart component -->
            </div>
          </CardContent>
        </Card>

        <!-- Service Performance -->
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center">
              <PieChart class="h-5 w-5 ml-2" />
              أداء الخدمات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              {#each analyticsData.service_performance?.slice(0, 5) || [] as service}
                <div class="flex items-center justify-between p-3 bg-muted/20 rounded">
                  <div class="flex-1">
                    <p class="font-medium">{service.service__name}</p>
                    <p class="text-sm text-muted-foreground">
                      {formatNumber(service.bookings)} حجز
                    </p>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-green-600">
                      {formatCurrency(service.revenue)}
                    </p>
                    {#if service.avg_rating}
                      <div class="flex items-center text-sm text-yellow-600">
                        <Star class="h-3 w-3 ml-1" />
                        {service.avg_rating.toFixed(1)}
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          </CardContent>
        </Card>

        <!-- Peak Hours -->
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center">
              <Clock class="h-5 w-5 ml-2" />
              أوقات الذروة
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              {#each analyticsData.peak_hours?.slice(0, 5) || [] as hour}
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium">
                    {hour.hour}:00 - {hour.hour + 1}:00
                  </span>
                  <div class="flex items-center">
                    <div class="w-20 bg-muted rounded-full h-2 ml-3">
                      <div 
                        class="bg-primary h-2 rounded-full" 
                        style="width: {(hour.count / analyticsData.peak_hours[0]?.count) * 100}%"
                      ></div>
                    </div>
                    <span class="text-sm text-muted-foreground min-w-0">
                      {formatNumber(hour.count)} حجز
                    </span>
                  </div>
                </div>
              {/each}
            </div>
          </CardContent>
        </Card>

        <!-- Customer Insights -->
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center">
              <Target class="h-5 w-5 ml-2" />
              رؤى العملاء
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-3 bg-green-50 rounded">
                <span class="font-medium">عملاء جدد</span>
                <span class="text-lg font-bold text-green-700">
                  {formatNumber(analyticsData.customer_insights?.new_customers)}
                </span>
              </div>
              
              <div class="flex items-center justify-between p-3 bg-blue-50 rounded">
                <span class="font-medium">عملاء متكررون</span>
                <span class="text-lg font-bold text-blue-700">
                  {formatNumber(analyticsData.customer_insights?.repeat_rate)}
                </span>
              </div>
              
              <div class="flex items-center justify-between p-3 bg-purple-50 rounded">
                <span class="font-medium">متوسط الحجوزات/العميل</span>
                <span class="text-lg font-bold text-purple-700">
                  {(analyticsData.customer_insights?.avg_bookings_per_customer || 0).toFixed(1)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Cancellation Analysis -->
      {#if analyticsData.cancellation_rate > 0}
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center">
              <Activity class="h-5 w-5 ml-2" />
              تحليل الإلغاءات
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="flex items-center justify-between p-4 bg-red-50 rounded-lg">
              <div>
                <p class="text-sm text-muted-foreground">معدل الإلغاء</p>
                <p class="text-2xl font-bold text-red-700">
                  {formatPercentage(analyticsData.cancellation_rate)}
                </p>
              </div>
              <div class="text-left">
                <p class="text-sm text-muted-foreground">إجمالي الحجوزات الملغية</p>
                <p class="text-lg font-semibold">
                  {formatNumber(analyticsData.status_breakdown?.cancelled || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      {/if}
    {/if}

    <!-- Recent Activity -->
    {#if dashboardData.recent_bookings?.length > 0}
      <Card>
        <CardHeader>
          <CardTitle>النشاط الأخير</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-3">
            {#each dashboardData.recent_bookings.slice(0, 5) as booking}
              <div class="flex items-center justify-between p-3 border rounded">
                <div class="flex-1">
                  <p class="font-medium">{booking.customer?.name}</p>
                  <p class="text-sm text-muted-foreground">
                    {booking.service?.name} - {new Date(booking.appointment_date).toLocaleDateString('ar-SA')}
                  </p>
                </div>
                <div class="text-left">
                  <Badge variant={booking.status === 'completed' ? 'default' : 
                                booking.status === 'pending' ? 'outline' :
                                booking.status === 'cancelled' ? 'destructive' : 'secondary'}>
                    {booking.status === 'completed' ? 'مكتمل' :
                     booking.status === 'pending' ? 'قيد الانتظار' :
                     booking.status === 'confirmed' ? 'مؤكد' :
                     booking.status === 'cancelled' ? 'ملغي' : booking.status}
                  </Badge>
                  <p class="text-sm font-semibold mt-1">
                    {formatCurrency(booking.total_price)}
                  </p>
                </div>
              </div>
            {/each}
          </div>
        </CardContent>
      </Card>
    {/if}
  {/if}
</div>