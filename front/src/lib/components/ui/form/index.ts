export { default as EnhancedForm } from './enhanced-form.svelte';

export interface FormField {
  name: string;
  type: 'text' | 'email' | 'password' | 'tel' | 'number' | 'date' | 'datetime-local' | 'time' | 'select' | 'multiselect' | 'textarea' | 'file' | 'checkbox' | 'radio' | 'range';
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  options?: { value: any; label: string }[];
  validation?: {
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    custom?: (value: any) => string | null;
  };
  hint?: string;
  icon?: any;
  prefix?: string;
  suffix?: string;
  multiple?: boolean;
  accept?: string;
  step?: number;
  cols?: number;
  rows?: number;
  dependsOn?: string;
  showIf?: (values: Record<string, any>) => boolean;
}

export interface FormSchema {
  title?: string;
  description?: string;
  fields: FormField[];
  sections?: {
    title: string;
    fields: string[];
  }[];
}