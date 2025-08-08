import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = "SAR"): string {
	return new Intl.NumberFormat("ar-SA", {
		style: "currency",
		currency: currency,
	}).format(amount);
}

export function formatDate(date: Date | string, locale: string = "ar-SA"): string {
	const dateObj = typeof date === "string" ? new Date(date) : date;
	return new Intl.DateTimeFormat(locale, {
		year: "numeric",
		month: "long",
		day: "numeric",
	}).format(dateObj);
}

export function formatTime(time: string): string {
	return new Date(`1970-01-01T${time}`).toLocaleTimeString("ar-SA", {
		hour: "2-digit",
		minute: "2-digit",
		hour12: true,
	});
}

export function formatPhone(phone: string): string {
	// Format Saudi phone number +966xxxxxxxxx
	if (phone.startsWith("+966")) {
		const number = phone.slice(4);
		return `+966 ${number.slice(0, 2)} ${number.slice(2, 5)} ${number.slice(5)}`;
	}
	return phone;
}

export function generateBookingId(): string {
	return Math.random().toString(36).substr(2, 9).toUpperCase();
}