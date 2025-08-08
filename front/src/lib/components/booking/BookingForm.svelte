<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Service, BookingForm } from '$lib/types/index.js';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Calendar, Clock, User, Phone, Mail } from '@lucide/svelte';
	import { formatSaudiPhone, validateSaudiPhone } from '$lib/utils/saudi-validation.js';

	interface Props {
		service: Service;
		selectedDate?: string;
		selectedTime?: string;
		availableSlots?: string[];
		isLoading?: boolean;
	}

	let {
		service,
		selectedDate = '',
		selectedTime = '',
		availableSlots = [],
		isLoading = false
	}: Props = $props();

	const dispatch = createEventDispatcher<{
		submit: BookingForm;
		dateChange: string;
		timeChange: string;
	}>();

	// Form state
	let customerName = $state('');
	let customerPhone = $state('');
	let customerEmail = $state('');
	let notes = $state('');

	// Validation state
	let phoneError = $state('');
	let nameError = $state('');

	// Get today's date for minimum date selection
	const today = new Date().toISOString().split('T')[0];

	// Handle form submission
	function handleSubmit() {
		// Reset errors
		phoneError = '';
		nameError = '';

		// Validate required fields
		if (!customerName.trim()) {
			nameError = 'Name is required';
			return;
		}

		if (!customerPhone.trim()) {
			phoneError = 'Phone number is required';
			return;
		}

		// Format and validate phone
		const formattedPhone = formatSaudiPhone(customerPhone);
		if (!validateSaudiPhone(formattedPhone)) {
			phoneError = 'Please enter a valid Saudi phone number';
			return;
		}

		if (!selectedDate) {
			alert('Please select a date');
			return;
		}

		if (!selectedTime) {
			alert('Please select a time');
			return;
		}

		// Dispatch booking data
		const bookingData: BookingForm = {
			service_id: service.id,
			customer_name: customerName.trim(),
			customer_phone: formattedPhone,
			customer_email: customerEmail.trim() || undefined,
			appointment_date: selectedDate,
			appointment_time: selectedTime,
			notes: notes.trim() || undefined
		};

		dispatch('submit', bookingData);
	}

	// Handle date change
	function handleDateChange(event: Event) {
		const target = event.target as HTMLInputElement;
		selectedDate = target.value;
		selectedTime = ''; // Reset time when date changes
		dispatch('dateChange', selectedDate);
	}

	// Handle time selection
	function handleTimeSelect(time: string) {
		selectedTime = time;
		dispatch('timeChange', time);
	}

	// Format service duration for display
	function formatDuration(duration: string): string {
		// Parse ISO 8601 duration (e.g., "PT1H30M" for 1 hour 30 minutes)
		const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
		if (!match) return duration;

		const hours = parseInt(match[1] || '0');
		const minutes = parseInt(match[2] || '0');

		if (hours && minutes) {
			return `${hours}h ${minutes}m`;
		} else if (hours) {
			return `${hours}h`;
		} else if (minutes) {
			return `${minutes}m`;
		}
		return duration;
	}
</script>

<div class="max-w-2xl mx-auto space-y-6">
	<!-- Service Information -->
	<Card>
		<CardHeader>
			<CardTitle class="flex items-center gap-2">
				<Calendar class="h-5 w-5" />
				Book {service.name}
			</CardTitle>
		</CardHeader>
		<CardContent class="space-y-4">
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div class="flex items-center gap-2">
					<Clock class="h-4 w-4 text-muted-foreground" />
					<span class="text-sm">{formatDuration(service.duration)}</span>
				</div>
				<div class="text-sm">
					<Badge variant="secondary" class="text-green-600">
						{service.price} SAR
					</Badge>
				</div>
				{#if service.description}
					<div class="md:col-span-3 text-sm text-muted-foreground">
						{service.description}
					</div>
				{/if}
			</div>
		</CardContent>
	</Card>

	<!-- Date and Time Selection -->
	<Card>
		<CardHeader>
			<CardTitle>Select Date and Time</CardTitle>
		</CardHeader>
		<CardContent class="space-y-4">
			<!-- Date Selection -->
			<div class="space-y-2">
				<Label for="booking-date">Date</Label>
				<Input
					id="booking-date"
					type="date"
					min={today}
					value={selectedDate}
					onchange={handleDateChange}
					required
				/>
			</div>

			<!-- Time Selection -->
			{#if selectedDate && availableSlots.length > 0}
				<div class="space-y-2">
					<Label>Available Times</Label>
					<div class="grid grid-cols-3 md:grid-cols-4 gap-2">
						{#each availableSlots as slot}
							<Button
								variant={selectedTime === slot ? 'default' : 'outline'}
								size="sm"
								class="text-sm"
								onclick={() => handleTimeSelect(slot)}
							>
								{slot}
							</Button>
						{/each}
					</div>
				</div>
			{:else if selectedDate}
				<div class="text-center text-muted-foreground py-4">
					Loading available times...
				</div>
			{/if}
		</CardContent>
	</Card>

	<!-- Customer Information -->
	<Card>
		<CardHeader>
			<CardTitle class="flex items-center gap-2">
				<User class="h-5 w-5" />
				Your Information
			</CardTitle>
		</CardHeader>
		<CardContent class="space-y-4">
			<!-- Name -->
			<div class="space-y-2">
				<Label for="customer-name">Full Name *</Label>
				<Input
					id="customer-name"
					type="text"
					placeholder="Enter your full name"
					bind:value={customerName}
					class={nameError ? 'border-red-500' : ''}
					required
				/>
				{#if nameError}
					<p class="text-sm text-red-500">{nameError}</p>
				{/if}
			</div>

			<!-- Phone -->
			<div class="space-y-2">
				<Label for="customer-phone">Phone Number *</Label>
				<div class="relative">
					<Phone class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						id="customer-phone"
						type="tel"
						placeholder="05xxxxxxxx or +966xxxxxxxxx"
						bind:value={customerPhone}
						class={`pl-10 ${phoneError ? 'border-red-500' : ''}`}
						required
					/>
				</div>
				{#if phoneError}
					<p class="text-sm text-red-500">{phoneError}</p>
				{:else}
					<p class="text-xs text-muted-foreground">
						Enter your Saudi phone number (e.g., 0512345678)
					</p>
				{/if}
			</div>

			<!-- Email (Optional) -->
			<div class="space-y-2">
				<Label for="customer-email">Email (Optional)</Label>
				<div class="relative">
					<Mail class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
					<Input
						id="customer-email"
						type="email"
						placeholder="your.email@example.com"
						bind:value={customerEmail}
						class="pl-10"
					/>
				</div>
			</div>

			<!-- Notes (Optional) -->
			<div class="space-y-2">
				<Label for="notes">Special Requests (Optional)</Label>
				<textarea
					id="notes"
					class="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
					placeholder="Any special requests or notes..."
					bind:value={notes}
					rows="3"
				></textarea>
			</div>
		</CardContent>
	</Card>

	<!-- Submit Button -->
	<div class="text-center">
		<Button
			size="lg"
			class="w-full md:w-auto px-8"
			disabled={isLoading || !selectedDate || !selectedTime}
			onclick={handleSubmit}
		>
			{#if isLoading}
				<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
			{/if}
			Confirm Booking
		</Button>
	</div>
</div>

<style>
	textarea {
		resize: vertical;
		min-height: 80px;
	}
</style>