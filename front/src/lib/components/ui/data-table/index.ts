export { default as DataTable } from './data-table.svelte';

export interface DataTableColumn {
  key: string;
  title: string;
  sortable?: boolean;
  searchable?: boolean;
  render?: (value: any, row: any) => string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  type?: 'text' | 'number' | 'date' | 'badge' | 'currency' | 'boolean';
}

export interface DataTableAction {
  key: string;
  label: string;
  icon?: any;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost';
  onClick: (row: any) => void;
  show?: (row: any) => boolean;
}

export interface DataTableBulkAction {
  key: string;
  label: string;
  icon?: any;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost';
  onClick: (selectedRows: any[]) => void;
  confirmMessage?: string;
}