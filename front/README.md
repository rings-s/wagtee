# Wagtee Frontend - Premium Booking Platform

A modern, premium booking platform frontend built with SvelteKit 5, shadcn-svelte, and TypeScript, specifically designed for the Saudi market.

## 🚀 Features

### ✨ Modern Tech Stack
- **SvelteKit 5** with latest runes API for reactive state management
- **shadcn-svelte** component library for premium UI components
- **TypeScript** for type safety throughout the application
- **Tailwind CSS 4** for utility-first styling
- **mode-watcher** for seamless dark/light mode switching

### 🎨 Premium Design System
- **Dark/Light Mode**: System preference detection with manual toggle
- **OKLCH Color Space**: Better accessibility and smoother gradients
- **Responsive Design**: Mobile-first approach with touch-friendly interfaces
- **Arabic Typography**: RTL support preparation and cultural design patterns
- **Premium Animations**: Smooth transitions and micro-interactions

### 🏗️ Component Architecture
- **Modular Components**: Reusable UI components following shadcn design patterns
- **Type-Safe Props**: Full TypeScript integration with proper prop typing
- **Accessibility**: WCAG 2.1 AA compliance with proper ARIA labels
- **Performance**: Optimized bundle size with code splitting

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Modern web browser with ES2022 support

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## 📱 Available Pages

- **Landing Page** (`/`) - Hero section with subscription tiers and featured businesses
- **Login** (`/auth/login`) - Business owner authentication
- **Register** (`/auth/register`) - Multi-step business registration
- **Dashboard** (`/dashboard`) - Business analytics and management
- **Public Booking** (`/book/[businessId]`) - Customer booking interface

## 🎨 Key Components Built

### UI Components (shadcn-svelte)
- **Button** - Multiple variants with loading states
- **Card** - Header, content, footer composition
- **Input** - Form inputs with validation
- **Label** - Accessible form labels
- **Badge** - Status indicators
- **Mode Toggle** - Dark/light theme switcher

### Features Implemented
- **Full Authentication Flow** with Saudi phone validation
- **Business Dashboard** with analytics and stats
- **Public Booking System** with service selection
- **Dark/Light Mode** with system preference detection
- **Responsive Design** optimized for mobile and desktop
- **Type-Safe API Client** ready for backend integration
- **State Management** using Svelte 5 runes

## 🌍 Saudi Market Integration

- **Arabic Content** throughout the interface
- **Saudi Phone Validation** (+966xxxxxxxxx)
- **Business Types** for local market (barber, salon, etc.)
- **Currency Formatting** in Saudi Riyal (SAR)
- **Cultural Design** patterns and RTL preparation

## 📊 Dummy Data Included

Complete mock data structure matching backend models:
- Users with subscription tiers
- Business profiles with working hours
- Services with Arabic translations
- Bookings with multiple statuses
- Dashboard statistics

## 🔗 Backend Integration Ready

- **API Client** with authentication and error handling
- **TypeScript Types** matching Django models exactly
- **State Stores** for auth and business data management
- **Service Functions** for all backend endpoints

---

Built with modern web technologies for the Saudi business community 🇸🇦
