import { tv, type VariantProps } from "tailwind-variants";
import Root from "./badge.svelte";

const badgeVariants = tv({
	base: "inline-flex items-center rounded-full text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground hover:bg-primary/80 shadow-sm",
			secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-sm",
			destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/80 shadow-sm",
			outline: "border border-input text-foreground hover:bg-accent hover:text-accent-foreground",
			success: "bg-success/10 text-success border border-success/20 hover:bg-success/20",
			warning: "bg-warning/10 text-warning-foreground border border-warning/20 hover:bg-warning/20",
			info: "bg-info/10 text-info border border-info/20 hover:bg-info/20",
			// New modern variants
			gradient: "bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-md",
			glass: "glass-effect text-foreground backdrop-blur-sm border border-white/20",
			pulse: "bg-primary text-primary-foreground animate-pulse shadow-sm",
			glow: "bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40",
			minimal: "bg-muted text-muted-foreground hover:bg-muted/80",
		},
		size: {
			xs: "px-1.5 py-0.5 text-xs h-4",
			sm: "px-2 py-0.5 text-xs h-5",
			default: "px-2.5 py-0.5 text-xs h-6",
			lg: "px-3 py-1 text-sm h-7",
			xl: "px-4 py-1.5 text-base h-8",
		},
		interactive: {
			true: "cursor-pointer hover:scale-105 active:scale-95",
			false: "",
		},
		notification: {
			true: "relative animate-bounce",
			false: "",
		},
	},
	compoundVariants: [
		{
			variant: "pulse",
			notification: true,
			class: "animate-pulse",
		},
		{
			interactive: true,
			class: "select-none transition-transform duration-150",
		},
	],
	defaultVariants: {
		variant: "default",
		size: "default",
		interactive: false,
		notification: false,
	},
});

type Variant = VariantProps<typeof badgeVariants>["variant"];
type Size = VariantProps<typeof badgeVariants>["size"];
type Interactive = VariantProps<typeof badgeVariants>["interactive"];
type Notification = VariantProps<typeof badgeVariants>["notification"];

type Props = {
	variant?: Variant;
	size?: Size;
	interactive?: Interactive;
	notification?: Notification;
	count?: number;
	dot?: boolean;
	class?: string;
	children?: import('svelte').Snippet;
	leftIcon?: import('svelte').Snippet;
	rightIcon?: import('svelte').Snippet;
	onclick?: (event: MouseEvent) => void;
};

export {
	Root,
	type Props,
	badgeVariants,
	//
	Root as Badge,
	type Props as BadgeProps,
};