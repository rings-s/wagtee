import { tv, type VariantProps } from "tailwind-variants";
import Root from "./card.svelte";
import Content from "./card-content.svelte";
import Description from "./card-description.svelte";
import Footer from "./card-footer.svelte";
import Header from "./card-header.svelte";
import Title from "./card-title.svelte";

const cardVariants = tv({
	base: "rounded-lg border bg-card text-card-foreground shadow-sm transition-all duration-300",
	variants: {
		variant: {
			default: "border-border bg-card shadow-sm",
			elevated: "card-elevated hover:shadow-xl hover:-translate-y-1 hover:scale-101",
			glass: "card-glass backdrop-blur-lg border-white/20",
			premium: "card-premium hover:shadow-xl hover:-translate-y-1 border-border/50",
			interactive: "hover:shadow-md hover:-translate-y-0.5 cursor-pointer active:scale-98 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
			outline: "border-2 border-dashed border-border/60 bg-transparent hover:border-border hover:bg-card/50",
			gradient: "bg-gradient-to-br from-card via-card/90 to-card/80 border-border/30 shadow-md",
		},
	},
	defaultVariants: {
		variant: "default",
	},
});

type Variant = VariantProps<typeof cardVariants>["variant"];

type Props = {
	variant?: Variant;
	interactive?: boolean;
	hover?: boolean;
	class?: string;
	children?: import('svelte').Snippet;
	onclick?: (event: MouseEvent) => void;
};

export {
	Root,
	Content,
	Description,
	Footer,
	Header,
	Title,
	cardVariants,
	type Props,
	//
	Root as Card,
	Content as CardContent,
	Description as CardDescription,
	Footer as CardFooter,
	Header as CardHeader,
	Title as CardTitle,
	type Props as CardProps,
};