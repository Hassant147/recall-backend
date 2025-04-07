from .settings import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
# Temporarily set to True for troubleshooting
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Database configuration with better fallback options
try:
    # Try to use DATABASE_URL if provided
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Print some diagnostic info
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        print(f"Using database at {parsed.hostname}:{parsed.port}")
        
        # Parse the DATABASE_URL using dj_database_url correctly
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True
            )
        }
        
        # Set OPTIONS separately after creating the connection
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
            'connect_timeout': 30,
            'options': '-c timezone=UTC'
        }
    else:
        # Explicit PostgreSQL config if DATABASE_URL isn't set
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("POSTGRES_DB"),
                "USER": os.getenv("POSTGRES_USER"),
                "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
                "HOST": os.getenv("POSTGRES_HOST", "db"),
                "PORT": os.getenv("POSTGRES_PORT", "5432"),
                "CONN_MAX_AGE": 600,
                "OPTIONS": {
                    "connect_timeout": 10,
                    "sslmode": "require",
                    "target_session_attrs": "read-write"
                }
            }
        }
except Exception as e:
    print(f"Database configuration error: {str(e)}")
    print("Falling back to SQLite for testing")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Whitenoise for static files - must be first in middleware after SecurityMiddleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Configure static files properly for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Use a simpler storage backend for now
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Enable whitenoise to serve files in debug mode as well
WHITENOISE_USE_FINDERS = DEBUG

# CORS settings for secure connections
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host != '*'
]
# Add specific domain
CORS_ALLOWED_ORIGINS.append("https://recall-web-backend-3cytq.ondigitalocean.app")
CORS_ALLOWED_ORIGINS.append("https://recallguidelines.com")
CORS_ALLOWED_ORIGINS.append("http://localhost:5173")

if os.getenv('FRONTEND_URL'):
    CORS_ALLOWED_ORIGINS.append(os.getenv('FRONTEND_URL'))

# Allow credentials
CORS_ALLOW_CREDENTIALS = True

# SSL/HTTPS Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Force HTTPS for Swagger
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'SessionID': {
            'type': 'apiKey',
            'name': 'X-Session-ID',
            'in': 'header'
        }
    },
    'VALIDATOR_URL': None,
    'OPERATIONS_SORTER': 'alpha',
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
    'JSON_EDITOR': False,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch',
    ],
    'SCHEMES': ['https'],
    # Force relative URLs for all API paths to use HTTPS
    'USE_SESSION_AUTH': False,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DOC_EXPANSION': 'list',
}

# Email - ensure emails work in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '') 