import os
import typing
from pathlib import Path
from urllib.parse import ParseResult, parse_qsl, urlparse

from dotenv import load_dotenv

from .utils import parse_comma_sep_str

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = parse_comma_sep_str(os.getenv('ALLOWED_HOSTS', ''))
print('Allowed Hosts:', ALLOWED_HOSTS)

ALLOWED_ORIGINS = parse_comma_sep_str(os.getenv('ALLOWED_ORIGINS', ''))
CSRF_ALLOWED_ORIGINS = ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
print('Allowed Origins:', CORS_ALLOWED_ORIGINS)

INSTALLED_APPS = [
    'main',
    'accounts',
    'monotext',
    'provetrina',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'corsheaders',
    'drf_spectacular',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'

parsed_pg_url = typing.cast(ParseResult, urlparse(os.getenv('DATABASE_URL')))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed_pg_url.path.replace('/', ''),
        'USER': parsed_pg_url.username,
        'PASSWORD': parsed_pg_url.password,
        'HOST': parsed_pg_url.hostname,
        'PORT': 5432,
        'OPTIONS': dict(parse_qsl(parsed_pg_url.query)),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

AUTH_USER_MODEL = 'accounts.User'

# Redirect to monotext URL after log-in/out (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/monotext'
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Backend API',
    'DESCRIPTION': 'A back-end web application built with Django'
    ' to support multiple front-end applications.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
