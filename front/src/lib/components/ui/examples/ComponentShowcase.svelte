<script lang="ts">
	import { Button } from "../button/index.js";
	import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../card/index.js";
	import { Input } from "../input/index.js";
	import { Badge } from "../badge/index.js";
	import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../dialog/index.js";
	import { cn } from "$lib/utils/index.js";

	// Reactive states using Svelte 5 runes
	let buttonLoading = $state(false);
	let inputValue = $state("");
	let inputValueFloating = $state("");
	let dialogOpen = $state(false);
	let badgeCount = $state(5);

	// Demo functions
	const simulateButtonAction = async () => {
		buttonLoading = true;
		await new Promise(resolve => setTimeout(resolve, 2000));
		buttonLoading = false;
	};

	const incrementBadge = () => {
		badgeCount++;
	};

	// Icons as snippets
	const HeartIcon = () => `
		<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
			<path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"></path>
		</svg>
	`;

	const SearchIcon = () => `
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
		</svg>
	`;

	const UserIcon = () => `
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
		</svg>
	`;

	const PlusIcon = () => `
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
		</svg>
	`;
</script>

<div class="container mx-auto py-10 space-y-12">
	<div class="text-center space-y-4">
		<h1 class="text-4xl font-bold gradient-text">Enhanced UI Components</h1>
		<p class="text-lg text-muted-foreground">Modern Svelte 5 components with enhanced interactions and 2025 design patterns</p>
	</div>

	<!-- Enhanced Buttons Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">Enhanced Buttons</h2>
			<p class="text-muted-foreground mb-6">Buttons with modern variants, loading states, and micro-interactions</p>
		</div>

		<!-- Button Variants -->
		<Card>
			<CardHeader>
				<CardTitle>Button Variants</CardTitle>
				<CardDescription>All available button styles and variants</CardDescription>
			</CardHeader>
			<CardContent class="space-y-4">
				<!-- Standard variants -->
				<div class="flex flex-wrap gap-3">
					<Button>Default</Button>
					<Button variant="secondary">Secondary</Button>
					<Button variant="outline">Outline</Button>
					<Button variant="ghost">Ghost</Button>
					<Button variant="link">Link</Button>
					<Button variant="destructive">Destructive</Button>
				</div>

				<!-- Premium variants -->
				<div class="flex flex-wrap gap-3">
					<Button variant="premium">Premium</Button>
					<Button variant="gradient">Gradient</Button>
					<Button variant="glass">Glass</Button>
					<Button variant="floating">Floating</Button>
				</div>

				<!-- Sizes -->
				<div class="flex flex-wrap gap-3 items-center">
					<Button size="xs">Extra Small</Button>
					<Button size="sm">Small</Button>
					<Button size="default">Default</Button>
					<Button size="lg">Large</Button>
					<Button size="xl">Extra Large</Button>
				</div>

				<!-- With icons -->
				<div class="flex flex-wrap gap-3">
					<Button variant="premium">
						{#snippet leftIcon()}{@html HeartIcon()}{/snippet}
						With Left Icon
					</Button>
					<Button variant="outline">
						Add User
						{#snippet rightIcon()}{@html PlusIcon()}{/snippet}
					</Button>
					<Button size="icon-lg" variant="gradient">
						{@html HeartIcon()}
					</Button>
				</div>

				<!-- Loading states -->
				<div class="flex flex-wrap gap-3">
					<Button 
						loading={buttonLoading} 
						onclick={simulateButtonAction}
						variant="premium"
					>
						{buttonLoading ? "Processing..." : "Simulate Loading"}
					</Button>
					<Button loading={true} variant="secondary">Always Loading</Button>
				</div>

				<!-- Interactive features -->
				<div class="flex flex-wrap gap-3">
					<Button variant="floating" ripple={true}>With Ripple Effect</Button>
					<Button variant="glow">Glow Effect</Button>
				</div>
			</CardContent>
		</Card>
	</section>

	<!-- Enhanced Cards Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">Enhanced Cards</h2>
			<p class="text-muted-foreground mb-6">Cards with modern variants and interactive states</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			<!-- Default Card -->
			<Card>
				<CardHeader>
					<CardTitle>Default Card</CardTitle>
					<CardDescription>Standard card design</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">This is a standard card with default styling.</p>
				</CardContent>
			</Card>

			<!-- Premium Card -->
			<Card variant="premium">
				<CardHeader>
					<CardTitle>Premium Card</CardTitle>
					<CardDescription>Enhanced with premium styling</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">Premium card with enhanced shadows and transitions.</p>
				</CardContent>
			</Card>

			<!-- Glass Card -->
			<Card variant="glass">
				<CardHeader>
					<CardTitle>Glass Card</CardTitle>
					<CardDescription>Modern glassmorphism effect</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">Card with glass morphism and backdrop blur.</p>
				</CardContent>
			</Card>

			<!-- Interactive Card -->
			<Card variant="interactive" interactive={true} onclick={() => alert("Card clicked!")}>
				<CardHeader>
					<CardTitle>Interactive Card</CardTitle>
					<CardDescription>Click me!</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">This card responds to clicks and has hover effects.</p>
				</CardContent>
			</Card>

			<!-- Elevated Card -->
			<Card variant="elevated">
				<CardHeader>
					<CardTitle>Elevated Card</CardTitle>
					<CardDescription>Enhanced elevation on hover</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">Card with enhanced elevation and hover effects.</p>
				</CardContent>
			</Card>

			<!-- Gradient Card -->
			<Card variant="gradient">
				<CardHeader>
					<CardTitle>Gradient Card</CardTitle>
					<CardDescription>Subtle gradient background</CardDescription>
				</CardHeader>
				<CardContent>
					<p class="text-sm text-muted-foreground">Card with gradient background effects.</p>
				</CardContent>
			</Card>
		</div>
	</section>

	<!-- Enhanced Inputs Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">Enhanced Inputs</h2>
			<p class="text-muted-foreground mb-6">Input fields with floating labels, validation states, and modern variants</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Input Variants & Features</CardTitle>
				<CardDescription>Different input styles and interactive features</CardDescription>
			</CardHeader>
			<CardContent class="space-y-6">
				<!-- Basic inputs -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Input 
						placeholder="Default input"
						bind:value={inputValue}
					/>
					<Input 
						variant="filled"
						placeholder="Filled variant"
					/>
				</div>

				<!-- Floating label inputs -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Input 
						floatingLabel={true}
						label="Floating Label"
						bind:value={inputValueFloating}
					/>
					<Input 
						variant="underlined"
						floatingLabel={true}
						label="Underlined with floating label"
					/>
				</div>

				<!-- With icons -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Input 
						placeholder="Search..."
						label="Search"
					>
						{#snippet leftIcon()}{@html SearchIcon()}{/snippet}
					</Input>
					<Input 
						placeholder="Username"
						label="User Account"
					>
						{#snippet leftIcon()}{@html UserIcon()}{/snippet}
					</Input>
				</div>

				<!-- Validation states -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Input 
						placeholder="Error state"
						error="This field is required"
						label="Error Example"
					/>
					<Input 
						placeholder="Success state"
						success="Looks good!"
						label="Success Example"
					/>
				</div>

				<!-- Different sizes -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<Input 
						size="sm"
						placeholder="Small input"
						label="Small"
					/>
					<Input 
						size="default"
						placeholder="Default size"
						label="Default"
					/>
					<Input 
						size="lg"
						placeholder="Large input"
						label="Large"
					/>
				</div>
			</CardContent>
		</Card>
	</section>

	<!-- Enhanced Badges Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">Enhanced Badges</h2>
			<p class="text-muted-foreground mb-6">Badges with status indicators, animations, and interactive features</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Badge Variants & Features</CardTitle>
				<CardDescription>Different badge styles and interactive features</CardDescription>
			</CardHeader>
			<CardContent class="space-y-6">
				<!-- Standard variants -->
				<div class="flex flex-wrap gap-3">
					<Badge>Default</Badge>
					<Badge variant="secondary">Secondary</Badge>
					<Badge variant="outline">Outline</Badge>
					<Badge variant="success">Success</Badge>
					<Badge variant="warning">Warning</Badge>
					<Badge variant="info">Info</Badge>
					<Badge variant="destructive">Error</Badge>
				</div>

				<!-- Modern variants -->
				<div class="flex flex-wrap gap-3">
					<Badge variant="gradient">Gradient</Badge>
					<Badge variant="glass">Glass</Badge>
					<Badge variant="pulse">Pulse</Badge>
					<Badge variant="glow">Glow</Badge>
					<Badge variant="minimal">Minimal</Badge>
				</div>

				<!-- Sizes -->
				<div class="flex flex-wrap gap-3 items-center">
					<Badge size="xs">XS</Badge>
					<Badge size="sm">Small</Badge>
					<Badge size="default">Default</Badge>
					<Badge size="lg">Large</Badge>
					<Badge size="xl">Extra Large</Badge>
				</div>

				<!-- With icons and features -->
				<div class="flex flex-wrap gap-3">
					<Badge variant="success" dot={true}>Online</Badge>
					<Badge variant="warning" count={badgeCount}>Notifications</Badge>
					<Badge 
						variant="gradient" 
						interactive={true}
						onclick={incrementBadge}
					>
						{#snippet leftIcon()}{@html PlusIcon()}{/snippet}
						Click me
					</Badge>
					<Badge variant="info" notification={true}>New Message</Badge>
				</div>
			</CardContent>
		</Card>
	</section>

	<!-- Enhanced Dialog Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">Enhanced Dialogs</h2>
			<p class="text-muted-foreground mb-6">Modal dialogs with modern animations and variants</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Dialog Examples</CardTitle>
				<CardDescription>Different dialog styles and configurations</CardDescription>
			</CardHeader>
			<CardContent class="space-y-4">
				<div class="flex flex-wrap gap-3">
					<!-- Default Dialog -->
					<Dialog bind:open={dialogOpen}>
						<DialogTrigger>
							<Button>Default Dialog</Button>
						</DialogTrigger>
						<DialogContent>
							<DialogHeader>
								<DialogTitle>Default Dialog</DialogTitle>
								<DialogDescription>
									This is a standard dialog with default styling and animations.
								</DialogDescription>
							</DialogHeader>
							<div class="py-4">
								<p class="text-sm text-muted-foreground">Dialog content goes here.</p>
							</div>
						</DialogContent>
					</Dialog>

					<!-- Glass Dialog -->
					<Dialog>
						<DialogTrigger>
							<Button variant="glass">Glass Dialog</Button>
						</DialogTrigger>
						<DialogContent variant="glass">
							<DialogHeader>
								<DialogTitle>Glass Effect Dialog</DialogTitle>
								<DialogDescription>
									Modern glassmorphism effect with backdrop blur.
								</DialogDescription>
							</DialogHeader>
							<div class="py-4">
								<p class="text-sm text-muted-foreground">This dialog uses glassmorphism design.</p>
							</div>
						</DialogContent>
					</Dialog>

					<!-- Premium Dialog -->
					<Dialog>
						<DialogTrigger>
							<Button variant="premium">Premium Dialog</Button>
						</DialogTrigger>
						<DialogContent variant="premium" size="lg">
							<DialogHeader>
								<DialogTitle>Premium Dialog</DialogTitle>
								<DialogDescription>
									Enhanced premium styling with better shadows and animations.
								</DialogDescription>
							</DialogHeader>
							<div class="py-4">
								<p class="text-sm text-muted-foreground">Premium dialog with enhanced visual effects.</p>
							</div>
						</DialogContent>
					</Dialog>

					<!-- Mobile-Optimized Dialog -->
					<Dialog>
						<DialogTrigger>
							<Button variant="outline">Mobile Dialog</Button>
						</DialogTrigger>
						<DialogContent size="mobile">
							<DialogHeader>
								<DialogTitle>Mobile Optimized</DialogTitle>
								<DialogDescription>
									Optimized for mobile devices with responsive sizing.
								</DialogDescription>
							</DialogHeader>
							<div class="py-4">
								<p class="text-sm text-muted-foreground">This dialog adapts to mobile screens.</p>
							</div>
						</DialogContent>
					</Dialog>
				</div>
			</CardContent>
		</Card>
	</section>

	<!-- RTL Support Section -->
	<section class="space-y-6">
		<div>
			<h2 class="text-2xl font-semibold mb-4">RTL Support</h2>
			<p class="text-muted-foreground mb-6">All components support RTL (Arabic) layout</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Arabic Layout Example</CardTitle>
				<CardDescription>Components automatically adapt to RTL direction</CardDescription>
			</CardHeader>
			<CardContent dir="rtl" class="space-y-4">
				<div class="flex flex-wrap gap-3">
					<Button variant="premium">
						{#snippet leftIcon()}{@html HeartIcon()}{/snippet}
						زر متميز
					</Button>
					<Badge variant="success" dot={true}>متاح</Badge>
				</div>
				<Input 
					placeholder="البحث..."
					label="البحث"
					floatingLabel={true}
				>
					{#snippet leftIcon()}{@html SearchIcon()}{/snippet}
				</Input>
			</CardContent>
		</Card>
	</section>
</div>