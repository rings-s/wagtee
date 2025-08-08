# Enhanced UI Components Guide

## Overview

This guide covers the enhanced UI components built with Svelte 5 runes, featuring modern 2025 design patterns, improved accessibility, and smooth micro-interactions. All components support RTL/Arabic layouts and follow the enhanced design system.

## 🔥 Enhanced Button Component

### New Features
- **Modern Variants**: `premium`, `gradient`, `glass`, `floating`
- **Loading States**: With spinners and custom loading text
- **Interactive Effects**: Ripple effects, hover animations
- **Icon Support**: Left/right icons with proper spacing
- **Enhanced Sizes**: `xs`, `xl`, and icon variants
- **Micro-interactions**: Scale animations, hover lifts

### Usage Examples

```svelte
<script>
  import { Button } from "$lib/components/ui/button";
  let loading = $state(false);
</script>

<!-- Premium button with loading -->
<Button 
  variant="premium" 
  {loading} 
  loadingText="Processing..."
  onclick={() => /* action */}
>
  {#snippet leftIcon()}
    <Icon name="heart" />
  {/snippet}
  Premium Action
</Button>

<!-- Glass button with ripple effect -->
<Button variant="glass" ripple={true}>
  Glass Button
</Button>

<!-- Floating button with right icon -->
<Button variant="floating" size="lg">
  Add Item
  {#snippet rightIcon()}
    <Icon name="plus" />
  {/snippet}
</Button>
```

### Available Variants
- `default` - Standard primary button
- `secondary` - Secondary styling
- `outline` - Outlined button
- `ghost` - Transparent background
- `link` - Link-styled button
- `destructive` - Destructive/danger button
- `premium` - Premium gradient with shine effect
- `gradient` - Modern gradient background
- `glass` - Glassmorphism effect
- `floating` - Elevated floating button

### Available Sizes
- `xs` - Extra small (h-8)
- `sm` - Small (h-9)
- `default` - Default (h-10)
- `lg` - Large (h-11)
- `xl` - Extra large (h-12)
- `icon` - Square icon button (h-10 w-10)
- `icon-sm` - Small icon (h-8 w-8)
- `icon-lg` - Large icon (h-12 w-12)

## 🎨 Enhanced Card Component

### New Features
- **Modern Variants**: `glass`, `elevated`, `premium`, `interactive`
- **Interactive States**: Click handling with animations
- **Hover Effects**: Enhanced hover animations
- **Better Accessibility**: Proper ARIA attributes

### Usage Examples

```svelte
<script>
  import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
</script>

<!-- Interactive card -->
<Card 
  variant="interactive" 
  interactive={true}
  onclick={() => console.log("Card clicked")}
>
  <CardHeader>
    <CardTitle>Interactive Card</CardTitle>
  </CardHeader>
  <CardContent>
    This card responds to clicks and has hover effects.
  </CardContent>
</Card>

<!-- Glass morphism card -->
<Card variant="glass">
  <CardHeader>
    <CardTitle>Glass Card</CardTitle>
  </CardHeader>
  <CardContent>
    Modern glassmorphism design.
  </CardContent>
</Card>
```

### Available Variants
- `default` - Standard card styling
- `elevated` - Enhanced elevation on hover
- `glass` - Glassmorphism effect with backdrop blur
- `premium` - Premium styling with enhanced shadows
- `interactive` - Interactive with hover/click states
- `outline` - Dashed outline style
- `gradient` - Subtle gradient background

## 📝 Enhanced Input Component

### New Features
- **Floating Labels**: Smooth label animations
- **Validation States**: Error/success states with icons
- **Icon Support**: Left/right icons
- **Multiple Variants**: `filled`, `underlined`, `ghost`
- **Enhanced Focus**: Modern focus rings and animations

### Usage Examples

```svelte
<script>
  import { Input } from "$lib/components/ui/input";
  let email = $state("");
</script>

<!-- Floating label input -->
<Input 
  bind:value={email}
  type="email"
  label="Email Address"
  floatingLabel={true}
  required={true}
/>

<!-- Input with validation -->
<Input 
  label="Username"
  error="Username is required"
  required={true}
/>

<!-- Input with icons -->
<Input 
  placeholder="Search..."
  label="Search"
>
  {#snippet leftIcon()}
    <Icon name="search" />
  {/snippet}
</Input>

<!-- Underlined variant -->
<Input 
  variant="underlined"
  label="Modern Input"
  floatingLabel={true}
/>
```

### Available Variants
- `default` - Standard bordered input
- `filled` - Filled background style
- `underlined` - Bottom border only
- `ghost` - Transparent background

### Available Sizes
- `sm` - Small (h-8)
- `default` - Default (h-10)
- `lg` - Large (h-12)

## 🏷️ Enhanced Badge Component

### New Features
- **Status Indicators**: Dot indicators and pulse animations
- **Notification Badges**: Count indicators with animations
- **Interactive Badges**: Click handling and hover effects
- **Modern Variants**: `gradient`, `glass`, `pulse`, `glow`

### Usage Examples

```svelte
<script>
  import { Badge } from "$lib/components/ui/badge";
  let count = $state(5);
</script>

<!-- Status badge with dot -->
<Badge variant="success" dot={true}>
  Online
</Badge>

<!-- Notification badge with count -->
<Badge variant="warning" count={count}>
  Notifications
</Badge>

<!-- Interactive badge -->
<Badge 
  variant="gradient" 
  interactive={true}
  onclick={() => count++}
>
  {#snippet leftIcon()}
    <Icon name="plus" />
  {/snippet}
  Click me
</Badge>

<!-- Animated notification -->
<Badge variant="info" notification={true}>
  New Message
</Badge>
```

### Available Variants
- `default` - Standard badge
- `secondary` - Secondary styling
- `outline` - Outlined badge
- `success` - Success state
- `warning` - Warning state
- `info` - Information state
- `destructive` - Error/destructive state
- `gradient` - Gradient background
- `glass` - Glassmorphism effect
- `pulse` - Pulsing animation
- `glow` - Glowing shadow effect
- `minimal` - Minimal styling

## 🔲 Enhanced Dialog Component

### New Features
- **Modern Animations**: Smooth entrance/exit animations
- **Enhanced Backdrop**: Better blur effects
- **Focus Trapping**: Proper accessibility
- **Multiple Variants**: `glass`, `premium`, `dark`
- **Mobile Optimization**: Responsive sizing

### Usage Examples

```svelte
<script>
  import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "$lib/components/ui/dialog";
  let open = $state(false);
</script>

<!-- Premium dialog -->
<Dialog bind:open>
  <DialogTrigger>
    <Button variant="premium">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent variant="premium" size="lg">
    <DialogHeader>
      <DialogTitle>Premium Dialog</DialogTitle>
    </DialogHeader>
    <div class="py-4">
      <p>Enhanced dialog with premium styling.</p>
    </div>
  </DialogContent>
</Dialog>

<!-- Glass effect dialog -->
<DialogContent 
  variant="glass"
  closeOnBackdropClick={true}
  showCloseButton={true}
>
  <!-- Dialog content -->
</DialogContent>
```

### Available Variants
- `default` - Standard dialog
- `glass` - Glassmorphism effect
- `premium` - Premium styling
- `dark` - Dark theme
- `minimal` - Minimal styling

### Available Sizes
- `sm` - Small (max-w-sm)
- `default` - Default (max-w-lg)
- `lg` - Large (max-w-2xl)
- `xl` - Extra large (max-w-4xl)
- `full` - Full screen (95vw/95vh)
- `mobile` - Mobile optimized

## 🎯 Design Tokens Integration

All components use the enhanced design tokens from `app.css`:

### Colors
- `--gradient-primary` - Premium gradient effects
- `--gradient-glass` - Glass morphism backgrounds
- `--shadow-premium` - Enhanced shadow effects
- `--success`, `--warning`, `--info` - Semantic colors

### Animations
- `--transition-spring` - Spring-like animations
- `--transition-bounce` - Bouncy animations
- `hover-lift`, `hover-glow` - Enhanced hover effects

### Utilities
- `.glass-effect` - Glassmorphism styling
- `.btn-premium` - Premium button effects
- `.card-premium` - Premium card styling

## 🌍 RTL/Arabic Support

All components automatically support RTL layouts:

```svelte
<div dir="rtl">
  <Button variant="premium">
    {#snippet leftIcon()}
      <Icon name="heart" />
    {/snippet}
    زر متميز
  </Button>
  
  <Input 
    label="البحث"
    placeholder="البحث..."
    floatingLabel={true}
  />
</div>
```

## ♿ Accessibility Features

### Enhanced Focus States
- Modern focus rings with proper contrast
- Focus trapping in dialogs
- Keyboard navigation support

### ARIA Attributes
- Proper role attributes for interactive elements
- Screen reader compatible
- Semantic HTML structure

### Color Contrast
- WCAG 2.1 AA compliant colors
- High contrast variants available
- Colorblind-friendly design

## 🔧 TypeScript Support

All components are fully typed with Svelte 5 runes:

```typescript
type ButtonProps = {
  variant?: "default" | "premium" | "gradient" | "glass" | "floating";
  size?: "xs" | "sm" | "default" | "lg" | "xl";
  loading?: boolean;
  loadingText?: string;
  ripple?: boolean;
  leftIcon?: Snippet;
  rightIcon?: Snippet;
  onclick?: (event: MouseEvent) => void;
};
```

## 📱 Mobile Optimization

- Touch-friendly sizes and spacing
- Responsive component variants
- Mobile-specific dialog sizing
- Optimized animations for mobile

## 🚀 Performance Features

- Svelte 5 runes for optimal reactivity
- Minimal bundle impact
- CSS-only animations where possible
- Efficient state management

## 🎨 Theming Support

Components automatically adapt to:
- Light/dark mode
- Custom color schemes
- Brand color overrides
- CSS custom properties

## Usage Tips

1. **Combine Variants**: Mix variants for unique designs
2. **Use Loading States**: Provide feedback during async operations
3. **Leverage Icons**: Enhance UX with meaningful icons
4. **Mobile First**: Test on mobile devices
5. **Accessibility**: Always include proper labels and ARIA attributes

This enhanced component system provides a solid foundation for building modern, accessible, and performant user interfaces with Svelte 5 and the latest design trends.