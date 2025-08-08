/**
 * Wagtee Frontend Agent Configuration
 * 
 * Configuration for MCP server integration and agent capabilities
 */

export const AGENT_CONFIG = {
  // Agent Identity
  name: 'wagtee-frontend-agent',
  version: '1.0.0',
  framework: 'svelte5',
  
  // MCP Server Configuration
  mcpServers: {
    magic: {
      priority: 1,
      capabilities: [
        'ui-generation',
        'component-creation',
        'design-systems',
        'responsive-layouts',
        'accessibility-compliance'
      ],
      settings: {
        framework: 'svelte',
        version: '5.0',
        designSystem: 'shadcn-inspired',
        accessibility: 'wcag-aa',
        responsive: true
      }
    },
    superclaude: {
      priority: 2,
      capabilities: [
        'code-analysis',
        'performance-optimization',
        'best-practices',
        'design-suggestions',
        'documentation-generation'
      ],
      settings: {
        analysisDepth: 'comprehensive',
        optimizationLevel: 'aggressive',
        codeQuality: 'enterprise',
        suggestions: 'detailed'
      }
    }
  },

  // Agent Capabilities
  capabilities: {
    componentGeneration: {
      enabled: true,
      frameworks: ['svelte5'],
      features: [
        'runes-integration',
        'typescript-support',
        'accessibility',
        'responsive-design',
        'rtl-support',
        'dark-mode'
      ]
    },
    designSystem: {
      enabled: true,
      baseSystem: 'shadcn-inspired',
      customizations: [
        'saudi-market',
        'arabic-typography',
        'cultural-colors',
        'prayer-time-integration'
      ]
    },
    codeAnalysis: {
      enabled: true,
      metrics: [
        'performance',
        'accessibility',
        'maintainability',
        'security',
        'bundle-size'
      ]
    },
    optimization: {
      enabled: true,
      targets: [
        'bundle-size',
        'runtime-performance',
        'accessibility',
        'seo',
        'core-web-vitals'
      ]
    }
  },

  // Saudi Market Specific Configuration
  saudiMarket: {
    enabled: true,
    features: {
      rtlSupport: true,
      arabicTypography: true,
      hijriCalendar: true,
      prayerTimes: true,
      culturalColors: true,
      localPaymentMethods: ['sadad', 'mada', 'stc-pay'],
      businessHours: {
        weekend: ['friday', 'saturday'],
        prayerBreaks: true,
        ramadanHours: true
      }
    },
    localization: {
      primaryLanguage: 'ar',
      secondaryLanguage: 'en',
      numberFormat: 'arabic',
      dateFormat: 'hijri',
      currency: 'SAR'
    }
  },

  // Component Templates
  componentTemplates: {
    basic: {
      structure: 'script-template-style',
      runes: ['state', 'derived', 'effect'],
      accessibility: true,
      responsive: true
    },
    advanced: {
      structure: 'modular-composition',
      runes: ['state', 'derived', 'effect', 'inspect'],
      features: ['slots', 'events', 'context'],
      testing: true,
      documentation: true
    },
    saudi: {
      structure: 'culturally-aware',
      runes: ['state', 'derived', 'effect'],
      features: ['rtl', 'arabic-text', 'cultural-ux'],
      accessibility: 'enhanced',
      localization: true
    }
  },

  // Design System Configuration
  designSystem: {
    tokens: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a'
        },
        saudi: {
          green: '#0d7377',
          gold: '#daa520',
          brown: '#8b4513'
        }
      },
      spacing: {
        scale: 'modular',
        base: 16,
        ratio: 1.25
      },
      typography: {
        arabic: {
          family: 'Noto Sans Arabic',
          weights: [300, 400, 500, 700],
          features: ['contextual-alternates', 'ligatures']
        },
        latin: {
          family: 'Inter',
          weights: [300, 400, 500, 600, 700],
          features: ['tabular-nums', 'case-sensitive-forms']
        }
      }
    },
    components: {
      button: {
        variants: ['primary', 'secondary', 'outline', 'ghost'],
        sizes: ['sm', 'md', 'lg'],
        states: ['default', 'hover', 'active', 'disabled', 'loading']
      },
      input: {
        types: ['text', 'email', 'password', 'search', 'tel'],
        variants: ['default', 'filled', 'outline'],
        states: ['default', 'focus', 'error', 'success', 'disabled']
      }
    }
  },

  // Performance Configuration
  performance: {
    bundleSize: {
      target: 'minimal',
      treeshaking: true,
      codesplitting: true,
      lazyLoading: true
    },
    runtime: {
      reactivity: 'fine-grained',
      rendering: 'optimized',
      hydration: 'selective'
    },
    metrics: {
      lcp: 2.5,
      fid: 100,
      cls: 0.1,
      fcp: 1.8
    }
  },

  // Development Configuration
  development: {
    hotReload: true,
    sourceMap: true,
    debugging: true,
    logging: {
      level: 'info',
      components: true,
      performance: true,
      mcp: true
    }
  },

  // Testing Configuration
  testing: {
    unit: {
      framework: 'vitest',
      coverage: 80,
      components: true
    },
    integration: {
      framework: 'playwright',
      browsers: ['chromium', 'firefox', 'webkit'],
      mobile: true
    },
    accessibility: {
      tool: 'axe-core',
      level: 'wcag-aa',
      automated: true
    },
    visual: {
      tool: 'playwright',
      regression: true,
      responsive: true
    }
  },

  // Documentation Configuration
  documentation: {
    components: {
      auto: true,
      format: 'mdx',
      examples: true,
      props: true,
      events: true
    },
    designSystem: {
      tokens: true,
      guidelines: true,
      examples: true,
      accessibility: true
    }
  }
};

// MCP Communication Protocols
export const MCP_PROTOCOLS = {
  magic: {
    generateComponent: {
      method: 'POST',
      endpoint: '/component/generate',
      timeout: 30000,
      retries: 3
    },
    analyzeDesign: {
      method: 'POST',
      endpoint: '/design/analyze',
      timeout: 15000,
      retries: 2
    },
    createTokens: {
      method: 'POST',
      endpoint: '/tokens/create',
      timeout: 10000,
      retries: 2
    }
  },
  superclaude: {
    analyzeCode: {
      method: 'POST',
      endpoint: '/code/analyze',
      timeout: 20000,
      retries: 3
    },
    optimize: {
      method: 'POST',
      endpoint: '/code/optimize',
      timeout: 25000,
      retries: 2
    },
    suggest: {
      method: 'POST',
      endpoint: '/suggestions/generate',
      timeout: 15000,
      retries: 3
    }
  }
};

// Agent Workflow Templates
export const WORKFLOWS = {
  componentCreation: [
    'analyzeRequirements',
    'generateStructure',
    'implementLogic',
    'optimizePerformance',
    'ensureAccessibility',
    'validateDesign',
    'generateDocumentation'
  ],
  designSystemCreation: [
    'analyzeMarketRequirements',
    'createDesignTokens',
    'generateBaseComponents',
    'implementVariants',
    'optimizeSystem',
    'validateConsistency',
    'generateGuidelines'
  ],
  codeOptimization: [
    'analyzeExistingCode',
    'identifyBottlenecks',
    'suggestImprovements',
    'implementOptimizations',
    'validatePerformance',
    'updateDocumentation'
  ]
};

export default AGENT_CONFIG;