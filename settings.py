def get_settings(installed_apps=[]):
    installed_apps = [f"    \"{i}\"" for i in installed_apps]
    installed_apps_string = ",\n".join(installed_apps)
    return \
"""from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_PROJ = BASE_DIR.parent
if os.getenv("DJANGO_DEBUG", None) is None:
    from dotenv import load_dotenv #download from pip install python-dotenv
    load_dotenv()


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG') == 'True'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
""" + installed_apps_string + \
"""
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("POSTGRES_DB"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST"),
        'PORT': int(os.getenv("POSTGRES_PORT")),
    },
}

USE_SQLITE_DATABASE = os.getenv("USE_SQLITE_DATABASE") == "True"
if USE_SQLITE_DATABASE:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True






DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


HTTP_PROTOCOL = os.getenv("HTTP_PROTOCOL")

BACKEND_NAME = os.getenv("BACKEND_NAME")
BACKEND_URL = HTTP_PROTOCOL + BACKEND_NAME

FRONTEND_NAME = os.getenv("FRONTEND_NAME")
FRONTEND_URL = HTTP_PROTOCOL + FRONTEND_NAME

WILLING_TO_ACCEPT_HTTPS = os.getenv("WILLING_TO_ACCEPT_HTTPS") == 'True'
# dangerous if https is not planned forever
if WILLING_TO_ACCEPT_HTTPS and HTTP_PROTOCOL == 'https://' and DEBUG:
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30 * 12 # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    BACKEND_NAME,
]
if BACKEND_NAME == "127.0.0.1:8000":
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]
    INTERNAL_IPS = [
        "127.0.0.1"
    ]

CSRF_TRUSTED_ORIGINS = [
    BACKEND_URL
]

# django cors header
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL
]

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / 'media'

# rest framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}"""

