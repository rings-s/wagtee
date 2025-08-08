# waqti_backend/settings.py
import os
from datetime import timedelta
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0'] if DEBUG else ['wagtee.sa', 'api.wagtee.sa']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Add token blacklisting
    'drf_spectacular',  # API documentation
    'corsheaders',
    'django_filters',
    'qrcode',
    'accounts',
    'base',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'accounts.middleware.SecurityHeadersMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.AuthenticationLoggingMiddleware',
    'accounts.middleware.RoleBasedAccessMiddleware',
    'accounts.middleware.SubscriptionEnforcementMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'back.wsgi.application'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'otp': '5/hour',
        'login': '10/min',      # Login rate limiting
        'refresh': '20/min',    # Token refresh rate limiting
        'password_reset': '3/hour',  # Password reset protection
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Enhanced JWT Configuration with Maximum Security

SIMPLE_JWT = {
    # Token lifetimes - balanced security and UX
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Shorter for high security
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Weekly rotation for security
    'ROTATE_REFRESH_TOKENS': True,                   # Always rotate refresh tokens
    
    # Security enhancements (following djangorestframework-simplejwt best practices)
    'BLACKLIST_AFTER_ROTATION': True,               # Blacklist old refresh tokens
    'UPDATE_LAST_LOGIN': True,                      # Track user activity
    
    # Cryptographic settings
    'ALGORITHM': 'HS256',                           # HMAC SHA-256 for signing
    'SIGNING_KEY': SECRET_KEY,                      # Use Django secret key
    'VERIFYING_KEY': None,                         # For symmetric algorithms
    'AUDIENCE': None,                              # Audience claim not required
    'ISSUER': 'wagtee.sa',                        # Issuer identification
    'JSON_ENCODER': None,                          # Use default JSON encoder
    'JWK_URL': None,                               # No JWK URL needed
    'LEEWAY': 0,                                   # No clock skew allowance
    
    # Token validation (all verification enabled for security)
    'VERIFY_SIGNATURE': True,                       # Always verify signatures
    'VERIFY_EXP': True,                            # Check expiration
    'VERIFY_NBF': True,                            # Check not-before
    'VERIFY_IAT': True,                            # Check issued-at
    'VERIFY_AUD': None,                            # Audience verification
    'VERIFY_ISS': None,                            # Issuer verification
    
    # Required claims for security
    'REQUIRE_EXP': True,                           # Expiration is mandatory
    'REQUIRE_IAT': True,                           # Issued-at is mandatory
    'REQUIRE_NBF': False,                          # Not-before is optional
    
    # Authentication configuration
    'AUTH_HEADER_TYPES': ('Bearer',),              # Only Bearer tokens
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',      # Standard header
    'USER_ID_FIELD': 'id',                         # User identifier field
    'USER_ID_CLAIM': 'user_id',                    # JWT user claim
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    # Token classes and claims
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',              # Token type in claims
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',                           # JWT ID claim
    
    # Sliding tokens (not used but configured for future)
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    
    # Serializer classes for custom token handling
    'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.CustomTokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
    'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
    'SLIDING_TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
    'SLIDING_TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',
}

# WhatsApp API Configuration
WHATSAPP_API_URL = config('WHATSAPP_API_URL', default=None)
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default=None)

# Payment Configuration (removed for development)

# Saudi Arabia Specific Settings
TIME_ZONE = 'Asia/Riyadh'
LANGUAGE_CODE = 'ar'
USE_I18N = True
USE_TZ = True

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
] if DEBUG else [
    "https://wagtee.sa",
    "https://www.wagtee.sa",
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    } if not DEBUG else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wagtee-cache',
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Enhanced Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# HTTPS Settings (enforced in production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Password Validation Enhancement
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging Configuration for Security
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'wagtee.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# DRF Spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'Wagtee API',
    'DESCRIPTION': 'Advanced SaaS booking platform tailored for the Saudi market',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
    },
    'REDOC_UI_SETTINGS': {
        'theme': {
            'colors': {
                'primary': {
                    'main': '#3b82f6',
                }
            },
            'typography': {
                'fontSize': '14px',
            }
        }
    },
    'CONTACT': {
        'name': 'Wagtee Support',
        'email': 'support@wagtee.sa',
        'url': 'https://wagtee.sa/support',
    },
    'LICENSE': {
        'name': 'Proprietary License',
    },
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Development Server'
        },
        {
            'url': 'https://api.wagtee.sa',
            'description': 'Production Server'
        }
    ],
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'User authentication and authorization endpoints'
        },
        {
            'name': 'Business Management',
            'description': 'Business profile and service management'
        },
        {
            'name': 'Booking System',
            'description': 'Booking creation and management'
        },
        {
            'name': 'Public API',
            'description': 'Public endpoints for customer booking'
        },
        {
            'name': 'Subscription',
            'description': 'Subscription and payment management'
        }
    ]
}