import { tv, type VariantProps } from "tailwind-variants";
import Root from "./dialog.svelte";
import Content from "./dialog-content.svelte";
import Description from "./dialog-description.svelte";
import Footer from "./dialog-footer.svelte";
import Header from "./dialog-header.svelte";
import Title from "./dialog-title.svelte";
import Trigger from "./dialog-trigger.svelte";

const dialogContentVariants = tv({
	base: "grid w-full gap-4 border bg-background p-6 shadow-lg sm:rounded-lg",
	variants: {
		variant: {
			default: "border-border bg-background shadow-lg",
			glass: "glass-card backdrop-blur-xl border-white/20 bg-background/90",
			premium: "card-premium shadow-2xl border-border/50",
			dark: "bg-card border-border/30 shadow-2xl",
			minimal: "border-0 shadow-none bg-background",
		},
		size: {
			sm: "max-w-sm",
			default: "max-w-lg",
			lg: "max-w-2xl",
			xl: "max-w-4xl",
			full: "max-w-[95vw] max-h-[95vh] m-4",
			mobile: "max-w-[95vw] max-h-[80vh] m-4 sm:max-w-lg sm:max-h-none sm:m-0",
		},
	},
	compoundVariants: [
		{
			variant: "glass",
			class: "backdrop-blur-xl saturate-150",
		},
		{
			size: "full",
			class: "overflow-auto",
		},
	],
	defaultVariants: {
		variant: "default",
		size: "default",
	},
});

type DialogContentVariant = VariantProps<typeof dialogContentVariants>["variant"];
type DialogContentSize = VariantProps<typeof dialogContentVariants>["size"];

type DialogContentProps = {
	variant?: DialogContentVariant;
	size?: DialogContentSize;
	showCloseButton?: boolean;
	closeOnBackdropClick?: boolean;
	closeOnEscape?: boolean;
	class?: string;
	children?: import('svelte').Snippet;
};

export {
	Root,
	Content,
	Description,
	Footer,
	Header,
	Title,
	Trigger,
	dialogContentVariants,
	type DialogContentProps,
	//
	Root as Dialog,
	Content as DialogContent,
	Description as DialogDescription,
	Footer as DialogFooter,
	Header as DialogHeader,
	Title as DialogTitle,
	Trigger as DialogTrigger,
	type DialogContentProps as DialogContentProps,
};