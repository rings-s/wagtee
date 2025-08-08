# Wagtee Frontend Agent System

🤖 **Advanced AI-powered frontend development with Svelte 5 + MCP integration**

## Overview

The Wagtee Frontend Agent System is an intelligent development assistant that combines the power of Svelte 5 runes with Magic MCP and SuperClaude MCP servers to create sophisticated, culturally-aware components for the Saudi market.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Wagtee Frontend Agent                    │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐    ┌─────────────────┐    ┌───────────┐  │
│  │   Magic MCP   │    │  SuperClaude    │    │  Svelte 5 │  │
│  │ UI Generation │    │   AI Analysis   │    │   Runes   │  │
│  └───────────────┘    └─────────────────┘    └───────────┘  │
├─────────────────────────────────────────────────────────────┤
│         Saudi Market Optimizations + Accessibility         │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 🎯 **Core Capabilities**
- **Svelte 5 Runes Integration**: Advanced reactive patterns with `$state`, `$derived`, `$effect`
- **Magic MCP**: AI-powered UI component generation and design systems
- **SuperClaude MCP**: Intelligent code analysis and optimization suggestions
- **Saudi Market Focus**: RTL support, Arabic typography, cultural adaptations

### 🌟 **Advanced Features**
- **Component Generation**: Auto-create Svelte 5 components with best practices
- **Design System**: Shadcn-inspired component library with Saudi customizations
- **Performance Optimization**: Bundle size reduction and runtime optimization
- **Accessibility**: WCAG AA compliance built-in
- **Cultural Intelligence**: Prayer time integration, Hijri calendar, local payments

## File Structure

```
.mcp/
├── servers.json           # MCP server configuration
├── frontend-agent.js      # Main frontend agent class
├── svelte5-agent.js       # Specialized Svelte 5 agent
├── agent-config.js        # Comprehensive configuration
└── README.md             # This documentation
```

## Quick Start

### 1. Initialize the Agent

```javascript
import { svelte5Agent } from './.mcp/svelte5-agent.js';

// Initialize the agent
await svelte5Agent.initialize();
```

### 2. Generate a Component

```javascript
// Generate a basic component
const buttonComponent = await svelte5Agent.generateSvelte5Component({
  name: 'Button',
  type: 'button',
  features: {
    variants: ['primary', 'secondary', 'outline'],
    sizes: ['sm', 'md', 'lg'],
    states: ['default', 'hover', 'active', 'disabled']
  },
  accessibility: true,
  responsive: true
});

// Generate Saudi market component
const prayerWidget = await svelte5Agent.generateSvelte5Component({
  name: 'PrayerTimeWidget',
  type: 'widget',
  saudi: true,
  features: {
    hijriCalendar: true,
    prayerAlerts: true,
    qiblaDirection: true
  }
});
```

### 3. Create Complete Design System

```javascript
// Generate comprehensive design system
const designSystem = await svelte5Agent.createDesignSystem({
  market: 'saudi',
  components: [
    'Button', 'Input', 'Card', 'Modal', 'Select',
    'PrayerTimeWidget', 'BookingCalendar', 'PaymentSelector'
  ],
  features: [
    'rtl-support',
    'arabic-typography',
    'dark-mode',
    'accessibility',
    'responsive'
  ]
});
```

## Agent Capabilities

### 🔮 **Magic MCP Integration**
- **UI Generation**: Create modern, responsive components
- **Design Tokens**: Generate comprehensive design token systems
- **Accessibility**: Built-in WCAG AA compliance
- **Responsive Design**: Mobile-first, adaptive layouts

### 🧠 **SuperClaude MCP Integration**
- **Code Analysis**: Comprehensive code quality analysis
- **Performance Optimization**: Bundle size and runtime optimization
- **Best Practices**: Industry-standard recommendations
- **Documentation**: Auto-generated component documentation

### 🇸🇦 **Saudi Market Specialization**
- **RTL Support**: Right-to-left layout optimization
- **Arabic Typography**: Proper Arabic font rendering
- **Cultural Colors**: Saudi market color preferences
- **Prayer Integration**: Prayer time awareness and scheduling
- **Local Payments**: SADAD, mada, STC Pay integration

## Component Templates

### Basic Svelte 5 Component

```svelte
<script>
  import { state, derived, effect } from 'svelte/reactivity';
  
  // Component props
  export let variant = 'primary';
  export let size = 'md';
  export let disabled = false;
  
  // Reactive state
  let buttonState = state({
    pressed: false,
    focused: false
  });
  
  // Derived state
  let buttonClasses = derived(() => {
    return `btn btn-${variant} btn-${size} ${
      disabled ? 'btn-disabled' : ''
    } ${buttonState.pressed ? 'btn-pressed' : ''}`;
  });
  
  // Effects
  effect(() => {
    console.log('Button state changed:', buttonState);
  });
</script>

<button 
  class={buttonClasses}
  {disabled}
  on:mousedown={() => buttonState.pressed = true}
  on:mouseup={() => buttonState.pressed = false}
>
  <slot />
</button>

<style>
  .btn {
    /* Base button styles */
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.375rem;
    font-weight: 500;
    transition: all 150ms ease;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
  }
  
  .btn-md {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
</style>
```

### Saudi Market Component

```svelte
<script>
  import { state, derived, effect } from 'svelte/reactivity';
  
  // Prayer time state
  let prayerState = state({
    times: null,
    nextPrayer: null,
    countdown: null
  });
  
  // RTL support
  let isRTL = derived(() => document.dir === 'rtl');
  
  // Prayer time effect
  effect(async () => {
    const times = await fetchPrayerTimes();
    prayerState.times = times;
    prayerState.nextPrayer = getNextPrayer(times);
  });
</script>

<div class="prayer-widget" class:rtl={isRTL}>
  <h3>أوقات الصلاة</h3>
  {#if prayerState.times}
    <!-- Prayer times display -->
  {/if}
</div>

<style>
  .prayer-widget {
    padding: 1rem;
    border-radius: 0.5rem;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .prayer-widget.rtl {
    direction: rtl;
    text-align: right;
  }
  
  h3 {
    font-family: 'Noto Sans Arabic', sans-serif;
    margin-bottom: 0.5rem;
  }
</style>
```

## Configuration

### MCP Servers

The agent connects to two MCP servers:

1. **Magic MCP**: UI generation and design systems
2. **SuperClaude MCP**: AI analysis and optimization

Configuration is handled automatically through `servers.json`.

### Agent Settings

Customize the agent behavior through `agent-config.js`:

```javascript
export const AGENT_CONFIG = {
  framework: 'svelte5',
  saudiMarket: {
    enabled: true,
    rtlSupport: true,
    arabicTypography: true,
    prayerTimes: true
  },
  performance: {
    bundleSize: 'minimal',
    treeshaking: true,
    lazyLoading: true
  }
};
```

## Development Workflow

### 1. Component Generation
```bash
# Generate component through agent
agent.generateComponent({
  name: 'MyComponent',
  type: 'form',
  saudi: true
})
```

### 2. Design System Creation
```bash
# Create complete design system
agent.createDesignSystem({
  market: 'saudi',
  components: ['Button', 'Input', 'Card']
})
```

### 3. Code Analysis
```bash
# Analyze existing components
agent.analyzeComponent('./src/components/Button.svelte')
```

## Best Practices

### 🎯 **Svelte 5 Runes**
- Use `$state()` for reactive data
- Use `$derived()` for computed values
- Use `$effect()` for side effects
- Use `$inspect()` for debugging

### 🇸🇦 **Saudi Market**
- Always consider RTL layout
- Use appropriate Arabic fonts
- Respect cultural color preferences
- Integrate prayer time considerations

### ♿ **Accessibility**
- Follow WCAG AA guidelines
- Use semantic HTML elements
- Provide proper ARIA labels
- Test with screen readers

### ⚡ **Performance**
- Minimize bundle size
- Use lazy loading
- Optimize images
- Monitor Core Web Vitals

## Testing

The agent generates comprehensive tests for all components:

- **Unit Tests**: Vitest-based component testing
- **Integration Tests**: Component interaction testing
- **Accessibility Tests**: Axe-core automated testing
- **Visual Tests**: Playwright visual regression testing

## Deployment

Components generated by the agent are production-ready and include:

- Optimized bundle configuration
- Accessibility compliance
- Performance optimizations
- Cultural adaptations
- Comprehensive documentation

## Support

For issues and questions:

1. Check the generated component documentation
2. Review the agent configuration
3. Analyze MCP server logs
4. Consult the Svelte 5 documentation

---

**Built with ❤️ for the Saudi market** 🇸🇦