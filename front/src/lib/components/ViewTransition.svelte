<script lang="ts">
	import { onNavigate } from '$app/navigation';
	import { onMount } from 'svelte';

	// Enhanced view transition with fallback animations
	onNavigate((navigation) => {
		// Check if browser supports View Transitions API
		if (!document.startViewTransition) {
			// Fallback animation for browsers without View Transitions support
			return addFallbackTransition();
		}

		return new Promise((resolve) => {
			document.startViewTransition(async () => {
				resolve();
				await navigation.complete;
			});
		});
	});

	// Fallback transition for non-supporting browsers
	function addFallbackTransition() {
		const body = document.body;
		
		// Add transition classes
		body.style.opacity = '0.95';
		body.style.transform = 'scale(0.99)';
		body.style.transition = 'opacity 0.2s ease-out, transform 0.2s ease-out';
		
		// Reset after a short delay
		setTimeout(() => {
			body.style.opacity = '1';
			body.style.transform = 'scale(1)';
			
			// Remove styles after transition
			setTimeout(() => {
				body.style.removeProperty('opacity');
				body.style.removeProperty('transform');
				body.style.removeProperty('transition');
			}, 200);
		}, 50);
	}

	// Add custom view transition styles
	onMount(() => {
		// Inject CSS for view transitions
		const style = document.createElement('style');
		style.textContent = `
			/* Custom View Transition Styles */
			::view-transition-old(root) {
				animation: slideOutRight 0.3s ease-in-out;
			}
			
			::view-transition-new(root) {
				animation: slideInLeft 0.3s ease-in-out;
			}
			
			/* Dashboard specific transitions */
			::view-transition-old(dashboard) {
				animation: fadeScaleOut 0.25s ease-in-out;
			}
			
			::view-transition-new(dashboard) {
				animation: fadeScaleIn 0.25s ease-in-out;
			}
			
			/* Form transitions */
			::view-transition-old(form) {
				animation: slideDown 0.3s ease-in-out;
			}
			
			::view-transition-new(form) {
				animation: slideUp 0.3s ease-in-out;
			}
			
			@keyframes slideOutRight {
				from {
					transform: translateX(0);
					opacity: 1;
				}
				to {
					transform: translateX(20px);
					opacity: 0;
				}
			}
			
			@keyframes slideInLeft {
				from {
					transform: translateX(-20px);
					opacity: 0;
				}
				to {
					transform: translateX(0);
					opacity: 1;
				}
			}
			
			@keyframes fadeScaleOut {
				from {
					transform: scale(1);
					opacity: 1;
				}
				to {
					transform: scale(0.95);
					opacity: 0;
				}
			}
			
			@keyframes fadeScaleIn {
				from {
					transform: scale(1.05);
					opacity: 0;
				}
				to {
					transform: scale(1);
					opacity: 1;
				}
			}
			
			@keyframes slideDown {
				from {
					transform: translateY(0);
					opacity: 1;
				}
				to {
					transform: translateY(10px);
					opacity: 0;
				}
			}
			
			@keyframes slideUp {
				from {
					transform: translateY(-10px);
					opacity: 0;
				}
				to {
					transform: translateY(0);
					opacity: 1;
				}
			}
			
			/* Loading skeleton animations */
			@keyframes shimmer {
				0% {
					background-position: -200px 0;
				}
				100% {
					background-position: calc(200px + 100%) 0;
				}
			}
			
			.skeleton {
				display: inline-block;
				height: 1em;
				position: relative;
				overflow: hidden;
				background-color: #eee;
				background-image: linear-gradient(90deg, #eee, #f5f5f5, #eee);
				background-size: 200px 100%;
				background-repeat: no-repeat;
				border-radius: 4px;
				animation: shimmer 1.3s ease-in-out infinite;
			}
			
			.dark .skeleton {
				background-color: #374151;
				background-image: linear-gradient(90deg, #374151, #4b5563, #374151);
			}
			
			/* Micro-interactions */
			.hover-lift {
				transition: transform 0.2s ease-out, box-shadow 0.2s ease-out;
			}
			
			.hover-lift:hover {
				transform: translateY(-2px);
				box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
			}
			
			.hover-scale {
				transition: transform 0.2s ease-out;
			}
			
			.hover-scale:hover {
				transform: scale(1.02);
			}
			
			.button-press {
				transition: transform 0.1s ease-out;
			}
			
			.button-press:active {
				transform: scale(0.98);
			}
			
			/* Enhanced form animations */
			.form-field-focus {
				transition: all 0.2s ease-out;
			}
			
			.form-field-focus:focus-within {
				transform: translateY(-1px);
				box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
			}
			
			/* Progress animations */
			.progress-bar {
				transition: width 0.5s ease-out;
			}
			
			.progress-glow {
				position: relative;
				overflow: hidden;
			}
			
			.progress-glow::before {
				content: '';
				position: absolute;
				top: 0;
				left: -100%;
				width: 100%;
				height: 100%;
				background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
				animation: progress-shine 2s infinite;
			}
			
			@keyframes progress-shine {
				0% {
					left: -100%;
				}
				100% {
					left: 100%;
				}
			}
			
			/* Card entrance animations */
			.card-entrance {
				animation: cardSlideUp 0.4s ease-out;
			}
			
			@keyframes cardSlideUp {
				from {
					opacity: 0;
					transform: translateY(20px);
				}
				to {
					opacity: 1;
					transform: translateY(0);
				}
			}
			
			/* Stagger animation for lists */
			.stagger-item {
				opacity: 0;
				transform: translateY(20px);
				animation: staggerIn 0.4s ease-out forwards;
			}
			
			.stagger-item:nth-child(1) { animation-delay: 0.1s; }
			.stagger-item:nth-child(2) { animation-delay: 0.2s; }
			.stagger-item:nth-child(3) { animation-delay: 0.3s; }
			.stagger-item:nth-child(4) { animation-delay: 0.4s; }
			.stagger-item:nth-child(5) { animation-delay: 0.5s; }
			
			@keyframes staggerIn {
				to {
					opacity: 1;
					transform: translateY(0);
				}
			}
			
			/* Notification animations */
			.notification-enter {
				animation: notificationSlideIn 0.3s ease-out;
			}
			
			.notification-exit {
				animation: notificationSlideOut 0.3s ease-in;
			}
			
			@keyframes notificationSlideIn {
				from {
					transform: translateX(100%);
					opacity: 0;
				}
				to {
					transform: translateX(0);
					opacity: 1;
				}
			}
			
			@keyframes notificationSlideOut {
				from {
					transform: translateX(0);
					opacity: 1;
				}
				to {
					transform: translateX(100%);
					opacity: 0;
				}
			}
		`;
		
		document.head.appendChild(style);
		
		// Cleanup on component destroy
		return () => {
			if (style.parentNode) {
				style.parentNode.removeChild(style);
			}
		};
	});
</script>

<!-- This component doesn't render anything, it just sets up the transitions -->