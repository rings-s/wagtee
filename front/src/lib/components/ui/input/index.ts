import { tv, type VariantProps } from "tailwind-variants";
import Root from "./input.svelte";

const inputVariants = tv({
	base: "flex w-full rounded-md border bg-background text-sm transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
	variants: {
		variant: {
			default: "border-input focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			filled: "border-transparent bg-muted focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-ring",
			underlined: "border-0 border-b-2 border-input rounded-none focus-visible:border-ring px-0",
			ghost: "border-transparent bg-transparent focus-visible:bg-muted focus-visible:ring-0",
		},
		size: {
			sm: "h-8 px-2 py-1 text-xs",
			default: "h-10 px-3 py-2",
			lg: "h-12 px-4 py-3 text-base",
		},
		state: {
			default: "",
			focused: "ring-2 ring-ring ring-offset-2 border-ring",
			error: "border-destructive focus-visible:ring-destructive focus-visible:border-destructive",
			success: "border-success focus-visible:ring-success focus-visible:border-success",
		},
	},
	compoundVariants: [
		{
			variant: "underlined",
			state: "focused",
			class: "ring-0 ring-offset-0 border-b-ring",
		},
		{
			variant: "underlined",
			state: "error",
			class: "border-b-destructive",
		},
		{
			variant: "underlined",
			state: "success",
			class: "border-b-success",
		},
	],
	defaultVariants: {
		variant: "default",
		size: "default",
		state: "default",
	},
});

type Variant = VariantProps<typeof inputVariants>["variant"];
type Size = VariantProps<typeof inputVariants>["size"];
type State = VariantProps<typeof inputVariants>["state"];

type Props = {
	variant?: Variant;
	size?: Size;
	type?: string;
	value?: string;
	label?: string;
	error?: string;
	success?: string;
	helperText?: string;
	placeholder?: string;
	disabled?: boolean;
	readonly?: boolean;
	required?: boolean;
	floatingLabel?: boolean;
	class?: string;
	leftIcon?: import('svelte').Snippet;
	rightIcon?: import('svelte').Snippet;
};

export {
	Root,
	inputVariants,
	type Props,
	//
	Root as Input,
	type Props as InputProps,
};