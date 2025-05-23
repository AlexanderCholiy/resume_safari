from pathlib import Path

from core.config import WebConfig


WebConfig.validate()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = WebConfig.SECRET_KEY

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost',]

INTERNAL_IPS = ['127.0.0.1', 'localhost',]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'user.apps.UserConfig',
    'pages.apps.PagesConfig',
    'services.apps.ServicesConfig',
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

TEMPLATES_DIR = WebConfig.TEMPLATES_DIR

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

USE_L10N = True

USE_TZ = True

STATIC_URL = 'static/'

STATICFILES_DIRS = [WebConfig.STATIC_DIR]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user.User'

MEDIA_URL = '/media-backend/'

MEDIA_ROOT = WebConfig.MEDIA_DIR

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = WebConfig.EMAIL_SERVER
EMAIL_PORT = WebConfig.EMAIL_PORT
EMAIL_USE_TLS = True
EMAIL_HOST_USER = WebConfig.EMAIL_LOGIN
EMAIL_HOST_PASSWORD = WebConfig.EMAIL_PSWD
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT = WebConfig.EMAIL_PSWD_RESET_TIMEOUT
LOGIN_REDIRECT_URL = 'user:resume_list'
LOGIN_URL = 'login'
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'
