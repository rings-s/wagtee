<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Badge } from '$lib/components/ui/badge';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { 
    ChevronLeft, 
    ChevronRight, 
    ChevronsLeft, 
    ChevronsRight,
    Search,
    Filter,
    Download,
    RefreshCw,
    ArrowUpDown,
    ArrowUp,
    ArrowDown,
    MoreHorizontal,
    Trash2,
    Edit,
    Eye
  } from '@lucide/svelte';

  // Props using Svelte 5 $props rune
  let {
    data = [],
    columns = [],
    loading = false,
    searchable = true,
    filterable = true,
    sortable = true,
    selectable = false,
    pagination = true,
    pageSize = 20,
    totalItems = 0,
    currentPage = 1,
    searchQuery = '',
    sortField = '',
    sortDirection = '',
    actions = [],
    bulkActions = [],
    emptyMessage = 'لا توجد بيانات للعرض',
    showExport = true,
    exportFormats = ['csv', 'excel', 'pdf'],
    ...restProps
  }: {
    data?: any[];
    columns?: DataTableColumn[];
    loading?: boolean;
    searchable?: boolean;
    filterable?: boolean;
    sortable?: boolean;
    selectable?: boolean;
    pagination?: boolean;
    pageSize?: number;
    totalItems?: number;
    currentPage?: number;
    searchQuery?: string;
    sortField?: string;
    sortDirection?: 'asc' | 'desc' | '';
    actions?: DataTableAction[];
    bulkActions?: DataTableBulkAction[];
    emptyMessage?: string;
    showExport?: boolean;
    exportFormats?: string[];
  } = $props();

  // Types
  interface DataTableColumn {
    key: string;
    title: string;
    sortable?: boolean;
    searchable?: boolean;
    render?: (value: any, row: any) => string;
    width?: string;
    align?: 'left' | 'center' | 'right';
    type?: 'text' | 'number' | 'date' | 'badge' | 'currency' | 'boolean';
  }

  interface DataTableAction {
    key: string;
    label: string;
    icon?: any;
    variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost';
    onClick: (row: any) => void;
    show?: (row: any) => boolean;
  }

  interface DataTableBulkAction {
    key: string;
    label: string;
    icon?: any;
    variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost';
    onClick: (selectedRows: any[]) => void;
    confirmMessage?: string;
  }

  // State using Svelte 5 runes
  let selectedRows = $state<Set<any>>(new Set());
  let isAllSelected = $state(false);
  let showFilters = $state(false);
  let filterValues = $state<Record<string, any>>({});
  let searchTimeout: number;

  // Computed using Svelte 5 $derived
  const totalPages = $derived(Math.ceil(totalItems / pageSize));
  const hasSelection = $derived(selectedRows.size > 0);
  const isAllCurrentPageSelected = $derived(data.length > 0 && data.every(row => selectedRows.has(row.id)));

  // Events
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  // Functions
  function handleSort(column: DataTableColumn) {
    if (!column.sortable) return;
    
    let newDirection: 'asc' | 'desc' = 'asc';
    if (sortField === column.key) {
      newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    }
    
    sortField = column.key;
    sortDirection = newDirection;
    dispatch('sort', { field: sortField, direction: sortDirection });
  }

  function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      dispatch('search', searchQuery);
    }, 300);
  }

  function handleRowSelect(row: any, selected: boolean) {
    if (selected) {
      selectedRows.add(row.id);
    } else {
      selectedRows.delete(row.id);
    }
    selectedRows = selectedRows;
    updateSelectAllState();
  }

  function handleSelectAll(selected: boolean) {
    if (selected) {
      data.forEach(row => selectedRows.add(row.id));
    } else {
      selectedRows.clear();
    }
    selectedRows = selectedRows;
    isAllSelected = selected;
  }

  function updateSelectAllState() {
    isAllSelected = data.length > 0 && data.every(row => selectedRows.has(row.id));
  }

  function handleBulkAction(action: DataTableBulkAction) {
    const selectedData = data.filter(row => selectedRows.has(row.id));
    if (action.confirmMessage) {
      if (confirm(action.confirmMessage)) {
        action.onClick(selectedData);
        selectedRows.clear();
        selectedRows = selectedRows;
      }
    } else {
      action.onClick(selectedData);
      selectedRows.clear();
      selectedRows = new Set();
    }
  }

  function renderCellValue(column: DataTableColumn, row: any) {
    const value = row[column.key];
    
    if (column.render) {
      return column.render(value, row);
    }
    
    switch (column.type) {
      case 'currency':
        return new Intl.NumberFormat('ar-SA', {
          style: 'currency',
          currency: 'SAR'
        }).format(value || 0);
      case 'date':
        return value ? new Date(value).toLocaleDateString('ar-SA') : '-';
      case 'boolean':
        return value ? '✓' : '✗';
      case 'badge':
        return value;
      default:
        return value || '-';
    }
  }

  function getBadgeVariant(value: string) {
    const variants: Record<string, string> = {
      'active': 'default',
      'inactive': 'secondary',
      'pending': 'outline',
      'confirmed': 'default',
      'completed': 'default',
      'cancelled': 'destructive',
      'high': 'destructive',
      'medium': 'outline',
      'low': 'secondary'
    };
    return variants[value?.toLowerCase()] || 'secondary';
  }

  // Initialize component using Svelte 5 effect
  $effect(() => {
    updateSelectAllState();
  });
</script>

<Card class="w-full">
  <CardHeader class="pb-4">
    <div class="flex items-center justify-between">
      <CardTitle class="text-lg font-semibold">البيانات</CardTitle>
      <div class="flex items-center gap-2">
        {#if showExport}
          <div class="relative inline-block text-left">
            <Button variant="outline" size="sm">
              <Download class="h-4 w-4 ml-2" />
              تصدير
            </Button>
          </div>
        {/if}
        
        <Button variant="outline" size="sm" onclick={() => dispatch('refresh')}>
          <RefreshCw class="h-4 w-4 ml-2" />
          تحديث
        </Button>
        
        {#if filterable}
          <Button 
            variant="outline" 
            size="sm" 
            onclick={() => showFilters = !showFilters}
          >
            <Filter class="h-4 w-4 ml-2" />
            فلترة
          </Button>
        {/if}
      </div>
    </div>

    <!-- Search and Bulk Actions -->
    <div class="flex items-center justify-between gap-4 mt-4">
      {#if searchable}
        <div class="relative flex-1 max-w-sm">
          <Search class="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="البحث..."
            bind:value={searchQuery}
            oninput={handleSearch}
            class="pr-10"
          />
        </div>
      {/if}

      {#if hasSelection && bulkActions.length > 0}
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">
            تم تحديد {selectedRows.size} عنصر
          </span>
          {#each bulkActions as action}
            <Button
              variant={action.variant || 'outline'}
              size="sm"
              onclick={() => handleBulkAction(action)}
            >
              {#if action.icon}
                <svelte:component this={action.icon} class="h-4 w-4 ml-2" />
              {/if}
              {action.label}
            </Button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Filters -->
    {#if showFilters && filterable}
      <div class="border-t pt-4 mt-4">
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {#each columns.filter(col => col.searchable) as column}
            <div>
              <label class="block text-sm font-medium mb-2">{column.title}</label>
              {#if column.type === 'boolean'}
                <select 
                  bind:value={filterValues[column.key]}
                  onchange={() => dispatch('filter', filterValues)}
                  class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">الكل</option>
                  <option value="true">نعم</option>
                  <option value="false">لا</option>
                </select>
              {:else}
                <Input
                  placeholder="فلترة {column.title}"
                  bind:value={filterValues[column.key]}
                  oninput={() => dispatch('filter', filterValues)}
                />
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </CardHeader>

  <CardContent class="p-0">
    {#if loading}
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <span class="mr-2">جاري التحميل...</span>
      </div>
    {:else if data.length === 0}
      <div class="flex flex-col items-center justify-center py-12 text-center">
        <div class="text-muted-foreground mb-2">{emptyMessage}</div>
      </div>
    {:else}
      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="border-b bg-muted/50">
            <tr>
              {#if selectable}
                <th class="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                  <input
                    type="checkbox"
                    checked={isAllCurrentPageSelected}
                    onchange={(e) => handleSelectAll(e.target.checked)}
                    class="rounded border-gray-300"
                  />
                </th>
              {/if}
              
              {#each columns as column}
                <th 
                  class="h-12 px-4 text-right align-middle font-medium text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                  class:cursor-pointer={column.sortable}
                  style={column.width ? `width: ${column.width}` : ''}
                  onclick={() => handleSort(column)}
                >
                  <div class="flex items-center justify-between">
                    <span>{column.title}</span>
                    {#if column.sortable}
                      <div class="ml-2">
                        {#if sortField === column.key}
                          {#if sortDirection === 'asc'}
                            <ArrowUp class="h-4 w-4" />
                          {:else}
                            <ArrowDown class="h-4 w-4" />
                          {/if}
                        {:else}
                          <ArrowUpDown class="h-4 w-4 opacity-50" />
                        {/if}
                      </div>
                    {/if}
                  </div>
                </th>
              {/each}
              
              {#if actions.length > 0}
                <th class="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                  الإجراءات
                </th>
              {/if}
            </tr>
          </thead>
          
          <tbody>
            {#each data as row, index}
              <tr class="border-b transition-colors hover:bg-muted/50">
                {#if selectable}
                  <td class="p-4 align-middle">
                    <input
                      type="checkbox"
                      checked={selectedRows.has(row.id)}
                      onchange={(e) => handleRowSelect(row, e.target.checked)}
                      class="rounded border-gray-300"
                    />
                  </td>
                {/if}
                
                {#each columns as column}
                  <td 
                    class="p-4 align-middle"
                    class:text-center={column.align === 'center'}
                    class:text-left={column.align === 'left'}
                  >
                    {#if column.type === 'badge'}
                      <Badge variant={getBadgeVariant(row[column.key])}>
                        {renderCellValue(column, row)}
                      </Badge>
                    {:else}
                      {renderCellValue(column, row)}
                    {/if}
                  </td>
                {/each}
                
                {#if actions.length > 0}
                  <td class="p-4 align-middle">
                    <div class="flex items-center gap-2">
                      {#each actions as action}
                        {#if !action.show || action.show(row)}
                          <Button
                            variant={action.variant || 'ghost'}
                            size="sm"
                            onclick={() => action.onClick(row)}
                          >
                            {#if action.icon}
                              <svelte:component this={action.icon} class="h-4 w-4" />
                            {/if}
                            {action.label}
                          </Button>
                        {/if}
                      {/each}
                    </div>
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      {#if pagination && totalPages > 1}
        <div class="flex items-center justify-between px-4 py-4 border-t">
          <div class="text-sm text-muted-foreground">
            عرض {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalItems)} من {totalItems}
          </div>
          
          <div class="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onclick={() => dispatch('pageChange', 1)}
            >
              <ChevronsRight class="h-4 w-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onclick={() => dispatch('pageChange', currentPage - 1)}
            >
              <ChevronRight class="h-4 w-4" />
            </Button>
            
            <span class="mx-4 text-sm">
              الصفحة {currentPage} من {totalPages}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onclick={() => dispatch('pageChange', currentPage + 1)}
            >
              <ChevronLeft class="h-4 w-4" />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onclick={() => dispatch('pageChange', totalPages)}
            >
              <ChevronsLeft class="h-4 w-4" />
            </Button>
          </div>
        </div>
      {/if}
    {/if}
  </CardContent>
</Card>