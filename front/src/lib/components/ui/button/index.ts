import { tv, type VariantProps } from "tailwind-variants";
import Root from "./button.svelte";

const buttonVariants = tv({
	base: "inline-flex items-center justify-center rounded-md text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden",
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm hover:shadow-md active:scale-95",
			destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm hover:shadow-md active:scale-95",
			outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground shadow-sm hover:shadow-md hover:border-accent active:scale-95",
			secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-sm hover:shadow-md active:scale-95",
			ghost: "hover:bg-accent hover:text-accent-foreground active:scale-95",
			link: "text-primary underline-offset-4 hover:underline active:scale-95",
			// New premium variants using design tokens
			premium: "btn-premium text-primary-foreground font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-sm",
			gradient: "btn-gradient text-white font-semibold shadow-md hover:shadow-lg transform hover:-translate-y-0.5 active:translate-y-0 active:shadow-sm",
			glass: "glass-effect text-foreground backdrop-blur-lg font-medium shadow-lg hover:shadow-xl border border-white/20 hover:border-white/30 transform hover:-translate-y-0.5 active:translate-y-0",
			floating: "bg-card text-card-foreground shadow-premium hover:shadow-2xl border border-border/50 hover:border-border transform hover:-translate-y-1 hover:scale-105 active:scale-100 active:translate-y-0",
		},
		size: {
			xs: "h-8 px-2 py-1 text-xs rounded-md",
			sm: "h-9 px-3 py-2 text-sm rounded-md",
			default: "h-10 px-4 py-2 text-sm rounded-md",
			lg: "h-11 px-8 py-3 text-base rounded-lg",
			xl: "h-12 px-10 py-4 text-lg rounded-lg",
			icon: "h-10 w-10 rounded-md",
			"icon-sm": "h-8 w-8 rounded-md",
			"icon-lg": "h-12 w-12 rounded-lg",
		},
		loading: {
			true: "cursor-wait",
			false: "",
		},
	},
	compoundVariants: [
		{
			variant: ["premium", "gradient", "glass", "floating"],
			class: "transition-all duration-300 ease-out",
		},
		{
			variant: "premium",
			loading: true,
			class: "animate-pulse",
		},
	],
	defaultVariants: {
		variant: "default",
		size: "default",
		loading: false,
	},
});

type Variant = VariantProps<typeof buttonVariants>["variant"];
type Size = VariantProps<typeof buttonVariants>["size"];
type Loading = VariantProps<typeof buttonVariants>["loading"];

type Props = {
	variant?: Variant;
	size?: Size;
	loading?: Loading;
	loadingText?: string;
	disabled?: boolean;
	class?: string;
	children?: import('svelte').Snippet;
	leftIcon?: import('svelte').Snippet;
	rightIcon?: import('svelte').Snippet;
	ripple?: boolean;
	href?: string;
	target?: string;
	onclick?: (event: MouseEvent) => void;
};

type Events = {
	click: MouseEvent;
	mouseenter: MouseEvent;
	mouseleave: MouseEvent;
	focus: FocusEvent;
	blur: FocusEvent;
};

export {
	Root,
	type Props,
	type Events,
	//
	Root as Button,
	type Props as ButtonProps,
	type Events as ButtonEvents,
	buttonVariants,
};