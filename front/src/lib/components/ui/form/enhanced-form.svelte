<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Badge } from '$lib/components/ui/badge';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { 
    AlertCircle, 
    CheckCircle, 
    Eye, 
    EyeOff, 
    Upload, 
    X, 
    Calendar,
    Clock,
    Phone,
    Mail,
    User,
    Building,
    CreditCard,
    Hash
  } from '@lucide/svelte';

  // Props
  export let schema: FormSchema;
  export let values: Record<string, any> = {};
  export let errors: Record<string, string[]> = {};
  export let loading = false;
  export let disabled = false;
  export let showValidation = true;
  export let submitText = 'حفظ';
  export let cancelText = 'إلغاء';
  export let showCancel = true;
  export let direction: 'rtl' | 'ltr' = 'rtl';

  // Types
  interface FormField {
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

  interface FormSchema {
    title?: string;
    description?: string;
    fields: FormField[];
    sections?: {
      title: string;
      fields: string[];
    }[];
  }

  // State
  let fieldValues: Record<string, any> = { ...values };
  let fieldErrors: Record<string, string[]> = { ...errors };
  let touched: Record<string, boolean> = {};
  let showPasswords: Record<string, boolean> = {};
  let uploadedFiles: Record<string, File[]> = {};

  const dispatch = createEventDispatcher();

  // Validation patterns
  const patterns = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone_sa: /^\+966[0-9]{9}$/,
    cr_number: /^[1-9][0-9]{9}$/,
    vat_number: /^[0-9]{15}$/,
    arabic: /^[\u0600-\u06FF\s]+$/,
    english: /^[a-zA-Z\s]+$/
  };

  // Functions
  function validateField(field: FormField, value: any): string[] {
    const errors: string[] = [];
    
    // Required validation
    if (field.required && (!value || (typeof value === 'string' && !value.trim()))) {
      errors.push(`${field.label} مطلوب`);
      return errors;
    }
    
    // Skip other validations if field is empty and not required
    if (!value && !field.required) return errors;
    
    const validation = field.validation;
    if (!validation) return errors;
    
    // String length validations
    if (typeof value === 'string') {
      if (validation.minLength && value.length < validation.minLength) {
        errors.push(`${field.label} يجب أن يكون ${validation.minLength} أحرف على الأقل`);
      }
      if (validation.maxLength && value.length > validation.maxLength) {
        errors.push(`${field.label} يجب أن يكون ${validation.maxLength} أحرف كحد أقصى`);
      }
    }
    
    // Number validations
    if (field.type === 'number' && typeof value === 'number') {
      if (validation.min !== undefined && value < validation.min) {
        errors.push(`${field.label} يجب أن يكون ${validation.min} أو أكثر`);
      }
      if (validation.max !== undefined && value > validation.max) {
        errors.push(`${field.label} يجب أن يكون ${validation.max} أو أقل`);
      }
    }
    
    // Pattern validations
    if (validation.pattern && typeof value === 'string') {
      const regex = new RegExp(validation.pattern);
      if (!regex.test(value)) {
        errors.push(`${field.label} غير صحيح`);
      }
    }
    
    // Built-in pattern validations
    if (field.type === 'email' && typeof value === 'string' && !patterns.email.test(value)) {
      errors.push('البريد الإلكتروني غير صحيح');
    }
    
    // Saudi phone validation
    if (field.type === 'tel' && typeof value === 'string' && !patterns.phone_sa.test(value)) {
      errors.push('رقم الهاتف يجب أن يكون بالصيغة +966xxxxxxxxx');
    }
    
    // Custom validation
    if (validation.custom) {
      const customError = validation.custom(value);
      if (customError) {
        errors.push(customError);
      }
    }
    
    return errors;
  }

  function validateForm(): boolean {
    const newErrors: Record<string, string[]> = {};
    let isValid = true;
    
    schema.fields.forEach(field => {
      if (!shouldShowField(field)) return;
      
      const fieldErrors = validateField(field, fieldValues[field.name]);
      if (fieldErrors.length > 0) {
        newErrors[field.name] = fieldErrors;
        isValid = false;
      }
    });
    
    fieldErrors = newErrors;
    return isValid;
  }

  function handleFieldChange(field: FormField, value: any) {
    fieldValues[field.name] = value;
    touched[field.name] = true;
    
    // Real-time validation
    if (showValidation && touched[field.name]) {
      const errors = validateField(field, value);
      if (errors.length > 0) {
        fieldErrors[field.name] = errors;
      } else {
        delete fieldErrors[field.name];
      }
      fieldErrors = { ...fieldErrors };
    }
    
    dispatch('change', { field: field.name, value, values: fieldValues });
  }

  function handleSubmit() {
    // Mark all fields as touched
    schema.fields.forEach(field => {
      touched[field.name] = true;
    });
    
    if (validateForm()) {
      dispatch('submit', fieldValues);
    } else {
      dispatch('invalid', fieldErrors);
    }
  }

  function handleCancel() {
    dispatch('cancel');
  }

  function handleFileUpload(field: FormField, event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files) {
      const files = Array.from(target.files);
      uploadedFiles[field.name] = files;
      fieldValues[field.name] = field.multiple ? files : files[0];
      handleFieldChange(field, fieldValues[field.name]);
    }
  }

  function removeFile(field: FormField, index: number) {
    if (uploadedFiles[field.name]) {
      uploadedFiles[field.name].splice(index, 1);
      fieldValues[field.name] = field.multiple ? uploadedFiles[field.name] : null;
      handleFieldChange(field, fieldValues[field.name]);
    }
  }

  function shouldShowField(field: FormField): boolean {
    if (field.showIf) {
      return field.showIf(fieldValues);
    }
    return true;
  }

  function getFieldIcon(field: FormField) {
    if (field.icon) return field.icon;
    
    const iconMap = {
      email: Mail,
      tel: Phone,
      password: User,
      date: Calendar,
      time: Clock,
      'datetime-local': Calendar,
      number: Hash
    };
    
    return iconMap[field.type];
  }

  // Initialize values
  onMount(() => {
    schema.fields.forEach(field => {
      if (values[field.name] !== undefined) {
        fieldValues[field.name] = values[field.name];
      }
    });
  });

  // Watch for external value changes
  $: {
    Object.keys(values).forEach(key => {
      if (fieldValues[key] !== values[key]) {
        fieldValues[key] = values[key];
      }
    });
  }

  // Watch for external error changes
  $: {
    fieldErrors = { ...errors };
  }
</script>

<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6" dir={direction}>
  {#if schema.title || schema.description}
    <div class="space-y-2">
      {#if schema.title}
        <h2 class="text-2xl font-bold">{schema.title}</h2>
      {/if}
      {#if schema.description}
        <p class="text-muted-foreground">{schema.description}</p>
      {/if}
    </div>
  {/if}

  {#if schema.sections}
    <!-- Sectioned Form -->
    {#each schema.sections as section}
      <Card>
        <CardHeader>
          <CardTitle>{section.title}</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          {#each section.fields as fieldName}
            {@const field = schema.fields.find(f => f.name === fieldName)}
            {#if field && shouldShowField(field)}
              <div class="space-y-2">
                <Label for={field.name} class="text-sm font-medium">
                  {field.label}
                  {#if field.required}
                    <span class="text-red-500">*</span>
                  {/if}
                </Label>

                <!-- Field Input -->
                <div class="relative">
                  {#if field.type === 'select'}
                    <select
                      id={field.name}
                      bind:value={fieldValues[field.name]}
                      onchange={(e) => handleFieldChange(field, e.target.value)}
                      class={cn("w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", fieldErrors[field.name] && "border-red-500")}
                      disabled={disabled || field.disabled}
                      required={field.required}
                    >
                      <option value="">{field.placeholder || `اختر ${field.label}`}</option>
                      {#each field.options || [] as option}
                        <option value={option.value}>{option.label}</option>
                      {/each}
                    </select>

                  {:else if field.type === 'textarea'}
                    <textarea
                      id={field.name}
                      bind:value={fieldValues[field.name]}
                      oninput={(e) => handleFieldChange(field, e.target.value)}
                      placeholder={field.placeholder}
                      rows={field.rows || 3}
                      cols={field.cols}
                      class={cn("w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none", fieldErrors[field.name] && "border-red-500")}
                      disabled={disabled || field.disabled}
                      readonly={field.readonly}
                      required={field.required}
                    />

                  {:else if field.type === 'file'}
                    <div class="space-y-2">
                      <div class="flex items-center justify-center w-full">
                        <label for={field.name} class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                          <div class="flex flex-col items-center justify-center pt-5 pb-6">
                            <Upload class="w-8 h-8 mb-4 text-gray-500" />
                            <p class="mb-2 text-sm text-gray-500">
                              <span class="font-semibold">اضغط للرفع</span> أو اسحب الملفات هنا
                            </p>
                            <p class="text-xs text-gray-500">{field.accept || 'جميع أنواع الملفات'}</p>
                          </div>
                          <input
                            id={field.name}
                            type="file"
                            class="hidden"
                            accept={field.accept}
                            multiple={field.multiple}
                            onchange={(e) => handleFileUpload(field, e)}
                            disabled={disabled || field.disabled}
                          />
                        </label>
                      </div>
                      
                      <!-- Uploaded Files Display -->
                      {#if uploadedFiles[field.name]?.length > 0}
                        <div class="space-y-2">
                          {#each uploadedFiles[field.name] as file, index}
                            <div class="flex items-center justify-between p-2 bg-muted rounded">
                              <span class="text-sm truncate">{file.name}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onclick={() => removeFile(field, index)}
                              >
                                <X class="h-4 w-4" />
                              </Button>
                            </div>
                          {/each}
                        </div>
                      {/if}
                    </div>

                  {:else if field.type === 'checkbox'}
                    <div class="flex items-center space-x-2 space-x-reverse">
                      <input
                        id={field.name}
                        type="checkbox"
                        bind:checked={fieldValues[field.name]}
                        onchange={(e) => handleFieldChange(field, e.target.checked)}
                        class="rounded border-gray-300 text-primary focus:ring-primary"
                        disabled={disabled || field.disabled}
                      />
                      <Label for={field.name} class="text-sm">
                        {field.placeholder || field.label}
                      </Label>
                    </div>

                  {:else if field.type === 'radio'}
                    <div class="space-y-2">
                      {#each field.options || [] as option}
                        <div class="flex items-center space-x-2 space-x-reverse">
                          <input
                            id="{field.name}-{option.value}"
                            type="radio"
                            bind:group={fieldValues[field.name]}
                            value={option.value}
                            onchange={(e) => handleFieldChange(field, option.value)}
                            class="text-primary focus:ring-primary"
                            disabled={disabled || field.disabled}
                          />
                          <Label for="{field.name}-{option.value}" class="text-sm">
                            {option.label}
                          </Label>
                        </div>
                      {/each}
                    </div>

                  {:else if field.type === 'range'}
                    <div class="space-y-2">
                      <input
                        id={field.name}
                        type="range"
                        bind:value={fieldValues[field.name]}
                        oninput={(e) => handleFieldChange(field, Number(e.target.value))}
                        min={field.validation?.min || 0}
                        max={field.validation?.max || 100}
                        step={field.step || 1}
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        disabled={disabled || field.disabled}
                      />
                      <div class="flex justify-between text-sm text-muted-foreground">
                        <span>{field.validation?.min || 0}</span>
                        <span class="font-medium">{fieldValues[field.name] || 0}</span>
                        <span>{field.validation?.max || 100}</span>
                      </div>
                    </div>

                  {:else if field.type === 'password'}
                    <div class="relative">
                      <Input
                        id={field.name}
                        type={showPasswords[field.name] ? 'text' : 'password'}
                        bind:value={fieldValues[field.name]}
                        oninput={(e) => handleFieldChange(field, e.target.value)}
                        placeholder={field.placeholder}
                        class={cn("pl-10", fieldErrors[field.name] && "border-red-500")}
                        disabled={disabled || field.disabled}
                        readonly={field.readonly}
                        required={field.required}
                      />
                      {#if getFieldIcon(field)}
                        <svelte:component 
                          this={getFieldIcon(field)} 
                          class="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" 
                        />
                      {/if}
                      <button
                        type="button"
                        class="absolute left-3 top-1/2 transform -translate-y-1/2"
                        onclick={() => showPasswords[field.name] = !showPasswords[field.name]}
                      >
                        {#if showPasswords[field.name]}
                          <EyeOff class="h-4 w-4 text-muted-foreground" />
                        {:else}
                          <Eye class="h-4 w-4 text-muted-foreground" />
                        {/if}
                      </button>
                    </div>

                  {:else}
                    <!-- Standard Input Types -->
                    <div class="relative">
                      {#if field.prefix}
                        <span class="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground text-sm">
                          {field.prefix}
                        </span>
                      {/if}
                      
                      <Input
                        id={field.name}
                        type={field.type}
                        bind:value={fieldValues[field.name]}
                        oninput={(e) => handleFieldChange(field, field.type === 'number' ? Number(e.target.value) : e.target.value)}
                        placeholder={field.placeholder}
                        class={cn(
                          field.prefix ? 'pr-12' : field.suffix ? 'pl-12' : getFieldIcon(field) ? 'pr-10' : '',
                          fieldErrors[field.name] && "border-red-500"
                        )}
                        disabled={disabled || field.disabled}
                        readonly={field.readonly}
                        required={field.required}
                        min={field.validation?.min}
                        max={field.validation?.max}
                        step={field.step}
                      />
                      
                      {#if getFieldIcon(field)}
                        <svelte:component 
                          this={getFieldIcon(field)} 
                          class="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" 
                        />
                      {/if}
                      
                      {#if field.suffix}
                        <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground text-sm">
                          {field.suffix}
                        </span>
                      {/if}
                    </div>
                  {/if}
                </div>

                <!-- Field Errors -->
                {#if fieldErrors[field.name]?.length > 0}
                  <div class="flex items-center space-x-1 space-x-reverse text-red-600 text-sm">
                    <AlertCircle class="h-4 w-4" />
                    <span>{fieldErrors[field.name][0]}</span>
                  </div>
                {/if}

                <!-- Field Hint -->
                {#if field.hint && !fieldErrors[field.name]?.length}
                  <p class="text-xs text-muted-foreground">{field.hint}</p>
                {/if}
              </div>
            {/if}
          {/each}
        </CardContent>
      </Card>
    {/each}
  {:else}
    <!-- Flat Form -->
    <div class="space-y-4">
      {#each schema.fields as field}
        {#if shouldShowField(field)}
          <!-- Same field rendering logic as above -->
          <div class="space-y-2">
            <Label for={field.name} class="text-sm font-medium">
              {field.label}
              {#if field.required}
                <span class="text-red-500">*</span>
              {/if}
            </Label>

            <!-- Field implementation would be the same as in sections -->
            <!-- Copy the field rendering logic from above -->
          </div>
        {/if}
      {/each}
    </div>
  {/if}

  <!-- Form Actions -->
  <div class="flex justify-end gap-2 pt-6 border-t">
    {#if showCancel}
      <Button variant="outline" type="button" onclick={handleCancel} disabled={loading}>
        {cancelText}
      </Button>
    {/if}
    
    <Button type="submit" disabled={loading || disabled}>
      {#if loading}
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white ml-2"></div>
      {/if}
      {submitText}
    </Button>
  </div>
</form>