<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import ModeToggle from '$lib/components/mode-toggle.svelte';
	import { authStore } from '$lib/stores/auth.svelte.js';
	
	import { 
		Menu, 
		X, 
		ChevronDown,
		QrCode,
		Calendar,
		Settings,
		User,
		LogOut,
		Crown,
		Zap,
		Home,
		BookOpen,
		Users,
		BarChart3,
		Building,
		CreditCard,
		Shield,
		Clock,
		FileText,
		UserCheck,
		Star,
		HelpCircle
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';

	// Props
	type Props = {
		variant?: 'public' | 'dashboard' | 'landing';
		showAuthButtons?: boolean;
	};

	let { 
		variant = 'landing', 
		showAuthButtons = true
	}: Props = $props();

	// Get auth state reactively
	let authState = $derived({
		user: authStore.user,
		isAuthenticated: authStore.isAuthenticated,
		isLoading: authStore.isLoading
	});

	// Mobile menu state
	let isMobileMenuOpen = $state(false);
	let isProfileDropdownOpen = $state(false);

	// Navigation items based on variant and user role with icons
	const getNavItems = () => {
		const userRole = authState.user?.role;
		
		switch (variant) {
			case 'public':
				return [
					{ label: 'تصفح الخدمات', href: '/services', icon: BookOpen },
					{ label: 'حجز موعد', href: '/booking', icon: Calendar },
					{ label: 'الأسعار', href: '/subscription', icon: CreditCard },
					{ label: 'من نحن', href: '/about', icon: Star },
					{ label: 'تواصل معنا', href: '/contact', icon: HelpCircle }
				];
			case 'dashboard':
				// Base dashboard items for all authenticated users
				const baseItems = [
					{ label: 'لوحة التحكم', href: '/dashboard', icon: Home },
					{ label: 'الحجوزات', href: '/dashboard/bookings', icon: Calendar },
					{ label: 'الخدمات', href: '/dashboard/services', icon: BookOpen },
					{ label: 'العملاء', href: '/dashboard/customers', icon: Users }
				];

				// Role-specific items
				if (userRole === 'super_admin') {
					return [
						...baseItems,
						{ label: 'إدارة الأعمال', href: '/dashboard/businesses', icon: Building },
						{ label: 'المستخدمين', href: '/dashboard/users', icon: UserCheck },
						{ label: 'الاشتراكات', href: '/dashboard/subscriptions', icon: CreditCard },
						{ label: 'التحليلات', href: '/dashboard/analytics', icon: BarChart3 },
						{ label: 'الإعدادات', href: '/dashboard/settings', icon: Settings }
					];
				} else if (userRole === 'admin') {
					return [
						...baseItems,
						{ label: 'إدارة الفريق', href: '/dashboard/team', icon: UserCheck },
						{ label: 'التحليلات', href: '/dashboard/analytics', icon: BarChart3 },
						{ label: 'الإعدادات', href: '/dashboard/settings', icon: Settings }
					];
				} else {
					// business_owner
					return [
						...baseItems,
						{ label: 'ساعات العمل', href: '/dashboard/hours', icon: Clock },
						{ label: 'التقارير', href: '/dashboard/reports', icon: FileText },
						{ label: 'الملف التجاري', href: '/dashboard/profile', icon: Building }
					];
				}
			default: // landing
				return [
					{ label: 'الميزات', href: '#features', icon: Star },
					{ label: 'حلول الأعمال', href: '#solutions', icon: Building },
					{ label: 'الأسعار', href: '/subscription', icon: CreditCard },
					{ label: 'قصص النجاح', href: '/success-stories', icon: Crown },
					{ label: 'المساعدة', href: '/help', icon: HelpCircle }
				];
		}
	};

	const navItems = getNavItems();

	// Handle mobile menu toggle
	const toggleMobileMenu = () => {
		isMobileMenuOpen = !isMobileMenuOpen;
		// Prevent body scroll when menu is open
		if (typeof document !== 'undefined') {
			if (isMobileMenuOpen) {
				document.body.style.overflow = 'hidden';
			} else {
				document.body.style.overflow = 'auto';
			}
		}
	};

	// Close mobile menu when clicking outside
	const closeMobileMenu = () => {
		isMobileMenuOpen = false;
		if (typeof document !== 'undefined') {
			document.body.style.overflow = 'auto';
		}
	};

	// Close mobile menu on escape key
	const handleKeydown = (e: KeyboardEvent) => {
		if (e.key === 'Escape' && isMobileMenuOpen) {
			closeMobileMenu();
		}
	};

	// Handle profile dropdown
	const toggleProfileDropdown = () => {
		isProfileDropdownOpen = !isProfileDropdownOpen;
	};

	// Handle clicking outside to close dropdowns\n\tconst handleOutsideClick = (e: Event) => {\n\t\tif (!e.target.closest('.relative')) {\n\t\t\tisProfileDropdownOpen = false;\n\t\t\tservicesDropdownOpen = false;\n\t\t\tratingsDropdownOpen = false;\n\t\t}\n\t};\n\n\t// Handle logout
	const handleLogout = async () => {
		try {
			await authStore.logout();
			// Close mobile menu and dropdown if open
			closeMobileMenu();
			isProfileDropdownOpen = false;
		} catch (err) {
			console.error('Logout failed:', err);
		}
	};

	// Navigation handlers
	const navigateToLogin = () => {
		goto('/auth/login');
	};

	const navigateToRegister = () => {
		goto('/auth/register');
	};

	const navigateToBooking = () => {
		goto('/book/public');
	};
</script>

<!-- Main Navbar -->
<nav class="bg-card/80 backdrop-blur-xl supports-[backdrop-filter]:bg-card/70 border-b border-border/40 sticky top-0 z-50 transition-all duration-300 shadow-sm"
     style="background: linear-gradient(135deg, hsl(var(--card) / 0.85) 0%, hsl(var(--card) / 0.95) 100%)">
	<div class="container mx-auto px-4">
		<div class="flex items-center justify-between h-16">
			<!-- Logo -->
			<div class="flex items-center gap-3">
				<a href="/" class="flex items-center gap-2 group">
					<div class="w-8 h-8 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 rounded-xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg group-hover:shadow-blue-500/25">
						<span class="text-white font-bold text-sm drop-shadow-sm">W</span>
					</div>
					<h1 class="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent group-hover:from-purple-600 group-hover:to-blue-600 transition-all duration-300">Wagtee</h1>
				</a>
				{#if variant === 'public'}
					<Badge variant="secondary" class="text-xs hidden sm:inline-flex">
						<QrCode class="w-3 h-3 mr-1" />
						احجز بسرعة
					</Badge>
				{:else if variant === 'dashboard'}
					<Badge variant="secondary" class="text-xs hidden sm:inline-flex">
						<Crown class="w-3 h-3 mr-1" />
						لوحة التحكم
					</Badge>
				{:else}
					<Badge variant="secondary" class="text-xs hidden sm:inline-flex">
						<Zap class="w-3 h-3 mr-1" />
						السعودية
					</Badge>
				{/if}
			</div>

			<!-- Desktop Navigation -->
			<div class="hidden md:flex items-center gap-4">
				{#each navItems as item}
					<a 
						href={item.href} 
						class="text-muted-foreground hover:text-primary transition-all duration-200 font-medium relative group px-3 py-2 rounded-lg hover:bg-accent/20 flex items-center gap-2"
					>
						{#if item.icon}
							<svelte:component this={item.icon} class="w-4 h-4" />
						{/if}
						<span class="relative z-10">{item.label}</span>
						<span class="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 group-hover:w-full transition-all duration-300 rounded-full"></span>
						<span class="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500/0 to-purple-500/0 group-hover:from-blue-500/10 group-hover:to-purple-500/10 transition-all duration-300"></span>
					</a>
				{/each}
			</div>

			<!-- Desktop Actions -->
			<div class="hidden md:flex items-center gap-3">
				<ModeToggle />
				
				{#if authState.isAuthenticated && authState.user}
					<!-- Logged in user -->
					<div class="relative">
						<Button
							variant="ghost"
							size="sm"
							onclick={toggleProfileDropdown}
							class="flex items-center space-x-2"
							disabled={authState.isLoading}
						>
							<div class="w-8 h-8 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
								<User class="w-4 h-4 text-blue-600" />
							</div>
							<span class="text-sm font-medium">{authState.user.first_name || authState.user.email}</span>
							<ChevronDown class="w-4 h-4" />
						</Button>

						{#if isProfileDropdownOpen}
							<!-- Profile Dropdown -->
							<div class="absolute left-0 mt-2 w-48 bg-card border rounded-lg shadow-lg py-2 z-50">
								<div class="px-4 py-2 border-b">
									<div class="text-sm font-medium">{authState.user.first_name} {authState.user.last_name}</div>
									<div class="text-xs text-muted-foreground">{authState.user.email}</div>
									<div class="text-xs text-muted-foreground capitalize">{authState.user.role}</div>
								</div>
								<a href="/dashboard" class="flex items-center px-4 py-2 text-sm hover:bg-accent transition-colors">
									<Settings class="w-4 h-4 mr-2" />
									لوحة التحكم
								</a>
								<a href="/profile" class="flex items-center px-4 py-2 text-sm hover:bg-accent transition-colors">
									<User class="w-4 h-4 mr-2" />
									الملف الشخصي
								</a>
								<button 
									onclick={handleLogout} 
									disabled={authState.isLoading}
									class="w-full flex items-center px-4 py-2 text-sm hover:bg-accent transition-colors text-red-600 disabled:opacity-50"
								>
									<LogOut class="w-4 h-4 mr-2" />
									{#if authState.isLoading}
										جاري تسجيل الخروج...
									{:else}
										تسجيل الخروج
									{/if}
								</button>
							</div>
						{/if}
					</div>
				{:else if showAuthButtons && !authState.isLoading}
					<!-- Not logged in -->
					{#if variant === 'public'}
						<Button variant="ghost" size="sm" onclick={navigateToBooking}>
							<QrCode class="w-4 h-4 mr-2" />
							احجز الآن
						</Button>
					{/if}
					
					<Button variant="outline" size="sm" onclick={navigateToLogin}>
						تسجيل الدخول
					</Button>
					
					<Button size="sm" onclick={navigateToRegister} class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
						{variant === 'public' ? 'سجل كصاحب عمل' : 'ابدأ عملك'}
					</Button>
				{:else if authState.isLoading}
					<!-- Loading state -->
					<div class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
				{/if}
			</div>

			<!-- Mobile Menu Button -->
			<div class="md:hidden flex items-center space-x-2">
				<ModeToggle />
				<Button variant="ghost" size="sm" onclick={toggleMobileMenu}>
					{#if isMobileMenuOpen}
						<X class="w-5 h-5" />
					{:else}
						<Menu class="w-5 h-5" />
					{/if}
				</Button>
			</div>
		</div>
	</div>

	<!-- Mobile Menu Overlay -->
	{#if isMobileMenuOpen}
		<div 
			class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-all duration-300" 
			onclick={closeMobileMenu}
			onkeydown={(e) => { if (e.key === 'Escape') closeMobileMenu(); }}
			role="button"
			tabindex="0"
			aria-label="Close mobile menu"
		></div>
	{/if}

	<!-- Mobile Menu -->
	<div class={`fixed top-16 left-0 right-0 bg-card/95 backdrop-blur-xl border-b border-border/50 shadow-2xl z-50 md:hidden transition-all duration-300 ease-out ${
		isMobileMenuOpen ? 'translate-y-0 opacity-100 visible' : '-translate-y-full opacity-0 invisible'
	}`}>
		<div class="px-4 py-6 space-y-4">
			<!-- Mobile Navigation Links -->
			<div class="space-y-2">
				{#each navItems as item}
					{#if item.hasDropdown}
						<!-- Mobile dropdown item -->
						<div class="space-y-1">
							<button 
								onclick={() => {
									if (item.dropdownId === 'services') {
										servicesDropdownOpen = !servicesDropdownOpen;
										ratingsDropdownOpen = false;
									} else if (item.dropdownId === 'ratings') {
										ratingsDropdownOpen = !ratingsDropdownOpen;
										servicesDropdownOpen = false;
									}
								}}
								class="w-full flex items-center justify-between px-4 py-3 text-muted-foreground hover:text-primary hover:bg-accent/50 rounded-xl transition-all duration-200 font-medium group"
							>
								<div class="flex items-center gap-3">
									{#if item.icon}
										<svelte:component this={item.icon} class="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
									{/if}
									<span class="group-hover:translate-x-1 transition-transform duration-200">{item.label}</span>
								</div>
								<ChevronDown class="w-4 h-4 transition-transform duration-200 {
									(item.dropdownId === 'services' && servicesDropdownOpen) || 
									(item.dropdownId === 'ratings' && ratingsDropdownOpen) 
										? 'rotate-180' : ''
								}" />
							</button>

							<!-- Mobile Services Dropdown -->
							{#if item.dropdownId === 'services' && servicesDropdownOpen}
								<div class="ml-8 space-y-1 border-l-2 border-border pl-4">
									<a href="/dashboard/services" onclick={closeMobileMenu} class="block px-3 py-2 text-sm text-muted-foreground hover:text-primary rounded-lg hover:bg-accent/30 transition-colors">
										عرض جميع الخدمات
									</a>
									{#if services.length > 0}
										{#each services.slice(0, 3) as service}
											<div class="px-3 py-2 text-sm border rounded-lg bg-accent/10">
												<div class="font-medium">{service.name}</div>
												<div class="text-xs text-muted-foreground">{service.price} ر.س</div>
											</div>
										{/each}
									{/if}
									<a href="/dashboard/services/new" onclick={closeMobileMenu} class="block px-3 py-2 text-sm text-blue-600 hover:underline rounded-lg hover:bg-blue-50 dark:hover:bg-blue-950/20 transition-colors">
										إضافة خدمة جديدة
									</a>
								</div>
							{/if}

							<!-- Mobile Ratings Dropdown -->
							{#if item.dropdownId === 'ratings' && ratingsDropdownOpen}
								<div class="ml-8 space-y-2 border-l-2 border-border pl-4">
									<div class="grid grid-cols-2 gap-2">
										<div class="bg-yellow-50 dark:bg-yellow-950/20 p-2 rounded-lg text-center">
											<div class="font-bold text-yellow-700">{businessStats?.average_rating || '4.8'}</div>
											<div class="text-xs text-muted-foreground">التقييم</div>
										</div>
										<div class="bg-green-50 dark:bg-green-950/20 p-2 rounded-lg text-center">
											<div class="font-bold text-green-700">{businessStats?.total_reviews || '156'}</div>
											<div class="text-xs text-muted-foreground">مراجعة</div>
										</div>
									</div>
									<a href="/dashboard/reviews" onclick={closeMobileMenu} class="block px-3 py-2 text-sm text-muted-foreground hover:text-primary rounded-lg hover:bg-accent/30 transition-colors">
										عرض جميع التقييمات
									</a>
									<a href="/dashboard/analytics?focus=reviews" onclick={closeMobileMenu} class="block px-3 py-2 text-sm text-purple-600 hover:underline rounded-lg hover:bg-purple-50 dark:hover:bg-purple-950/20 transition-colors">
										تقارير التقييمات
									</a>
								</div>
							{/if}
						</div>
					{:else}
						<!-- Regular mobile nav item -->
						<a 
							href={item.href} 
							onclick={closeMobileMenu}
							class="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:text-primary hover:bg-accent/50 rounded-xl transition-all duration-200 font-medium group"
						>
							{#if item.icon}
								<svelte:component this={item.icon} class="w-5 h-5 group-hover:scale-110 transition-transform duration-200" />
							{/if}
							<span class="group-hover:translate-x-1 transition-transform duration-200">{item.label}</span>
						</a>
					{/if}
				{/each}
			</div>

			<!-- Mobile User Section -->
			{#if authState.isAuthenticated && authState.user}
				<div class="border-t pt-4">
					<div class="flex items-center space-x-3 px-4 py-3 mb-3">
						<div class="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
							<User class="w-5 h-5 text-blue-600" />
						</div>
						<div>
							<div class="font-medium">{authState.user.first_name} {authState.user.last_name}</div>
							<div class="text-sm text-muted-foreground">{authState.user.email}</div>
							<div class="text-xs text-muted-foreground capitalize">{authState.user.role}</div>
						</div>
					</div>
					
					<div class="space-y-2">
						<a href="/dashboard" onclick={closeMobileMenu} class="flex items-center px-4 py-3 text-muted-foreground hover:bg-accent/50 rounded-xl transition-all duration-200 group">
							<Settings class="w-5 h-5 mr-3 group-hover:rotate-90 transition-transform duration-200" />
							لوحة التحكم
						</a>
						<a href="/profile" onclick={closeMobileMenu} class="flex items-center px-4 py-3 text-muted-foreground hover:bg-accent/50 rounded-xl transition-all duration-200 group">
							<User class="w-5 h-5 mr-3 group-hover:scale-110 transition-transform duration-200" />
							الملف الشخصي
						</a>
						<button 
							onclick={handleLogout} 
							disabled={authState.isLoading}
							class="w-full flex items-center px-4 py-3 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-xl transition-all duration-200 group disabled:opacity-50"
						>
							<LogOut class="w-5 h-5 mr-3 group-hover:translate-x-1 transition-transform duration-200" />
							{#if authState.isLoading}
								جاري تسجيل الخروج...
							{:else}
								تسجيل الخروج
							{/if}
						</button>
					</div>
				</div>
			{:else if showAuthButtons && !authState.isLoading}
				<!-- Mobile Auth Buttons -->
				<div class="border-t pt-4 space-y-3">
					{#if variant === 'public'}
						<Button 
							variant="outline" 
							size="sm" 
							class="w-full"
							onclick={() => { closeMobileMenu(); navigateToBooking(); }}
						>
							<QrCode class="w-4 h-4 mr-2" />
							احجز الآن
						</Button>
					{/if}
					
					<Button 
						variant="outline" 
						size="sm" 
						class="w-full"
						onclick={() => { closeMobileMenu(); navigateToLogin(); }}
					>
						تسجيل الدخول
					</Button>
					
					<Button 
						size="sm" 
						class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
						onclick={() => { closeMobileMenu(); navigateToRegister(); }}
					>
						{variant === 'public' ? 'سجل كصاحب عمل' : 'ابدأ عملك'}
					</Button>
				</div>
			{:else if authState.isLoading}
				<!-- Mobile Loading state -->
				<div class="border-t pt-4 flex justify-center">
					<div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
				</div>
			{/if}
		</div>
	</div>
</nav>

<!-- Handle window events -->
<svelte:window 
	onkeydown={handleKeydown}
	onclick={(e) => {
		if (!e.target.closest('.relative')) {
			isProfileDropdownOpen = false;
		}
	}} 
/>

<style>
	/* Add smooth animations */
	.transition-all {
		transition-property: all;
		transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
	}
	
	/* Premium gradient animations */
	@keyframes gradient {
		0% { background-position: 0% 50%; }
		50% { background-position: 100% 50%; }
		100% { background-position: 0% 50%; }
	}
	
	.animate-gradient {
		background-size: 200% 200%;
		animation: gradient 3s ease infinite;
	}
</style>