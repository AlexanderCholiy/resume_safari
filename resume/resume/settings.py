from pathlib import Path

from core.config import web_config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = web_config.SECRET_KEY

DEBUG = web_config.DEBUG

ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost', web_config.HOST, web_config.DOMAIN_NAME
]

INTERNAL_IPS = ['127.0.0.1', 'localhost',]

CSRF_TRUSTED_ORIGINS = [
    f'https://{web_config.HOST}',
    f'https://{web_config.DOMAIN_NAME}',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'debug_toolbar',
    'rest_framework',
    'djoser',
    'django_filters',
    'user.apps.UserConfig',
    'pages.apps.PagesConfig',
    'services.apps.ServicesConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'resume.urls'

TEMPLATES_DIR = web_config.TEMPLATES_DIR

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'resume.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': web_config.DB_NAME,
    #     'USER': web_config.DB_USER,
    #     'PASSWORD': web_config.DB_PASSWORD,
    #     'HOST': web_config.DB_HOST,
    #     'PORT': web_config.DB_PORT
    # }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.NumericPasswordValidator'
        ),
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

SWAGGER_USE_COMPAT_RENDERERS = False

AUTH_USER_MODEL = 'user.User'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static-backend/'

STATICFILES_DIRS = [web_config.STATIC_DIR]

STATIC_ROOT = web_config.STATIC_ROOT

MEDIA_URL = '/media/'

MEDIA_ROOT = web_config.MEDIA_DIR

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = web_config.EMAIL_DIR
EMAIL_HOST = web_config.EMAIL_SERVER
EMAIL_PORT = web_config.EMAIL_PORT
EMAIL_USE_TLS = True
EMAIL_HOST_USER = web_config.EMAIL_LOGIN
EMAIL_HOST_PASSWORD = web_config.EMAIL_PSWD
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT = web_config.EMAIL_PSWD_RESET_TIMEOUT
LOGIN_REDIRECT_URL = 'user:resume_list'
LOGIN_URL = 'login'
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '10000/day',
        'anon': '1000/day',
    },
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': web_config.ACCESS_TOKEN_LIFETIME,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
