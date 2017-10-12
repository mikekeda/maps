"""
Django settings for maps project.
"""

import os
import requests
from django.utils.translation import ugettext_lazy as _

SITE_ENV_PREFIX = 'MAPS'


def get_env_var(name, default=''):
    """Get all sensitive data from google vm custom metadata."""
    try:
        name = '_'.join([SITE_ENV_PREFIX, name])
        res = os.environ.get(name)
        if res:
            # Check env variable (Jenkins build).
            return res
        else:
            res = requests.get(
                'http://metadata.google.internal/computeMetadata/'
                'v1/instance/attributes/{}'.format(name),
                headers={'Metadata-Flavor': 'Google'}
            )
            if res.status_code == 200:
                return res.text
    except requests.exceptions.ConnectionError:
        return default
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var(
    'SECRET_KEY',
    'zha7wy2q_pnfi=)h0zei!wukd6c^x(s9z*mb-+7j)rby)q_&t2'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(get_env_var('DEBUG', True))

ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sitemaps',

    'leaflet',
    'djgeojson',
    'easy_select2',
    'widget_tweaks',
    'mptt',
    'social_django',
    'django_jenkins',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'maps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'maps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('DB_NAME', 'maps'),
        'USER': get_env_var('DB_USER', 'maps_admin'),
        'PASSWORD': get_env_var('DB_PASSWORD', 'maps_pass_!_12'),
        'HOST': get_env_var('DB_HOST', '127.0.0.1'),
        'PORT': '',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'core:maps'
SOCIAL_AUTH_FACEBOOK_KEY = get_env_var('SOCIAL_AUTH_FACEBOOK_KEY'),
SOCIAL_AUTH_FACEBOOK_SECRET = get_env_var('SOCIAL_AUTH_FACEBOOK_SECRET'),

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('uk', _('Ukrainian')),
    ('it', _('Italian')),
    ('fr', _('French')),
    ('ru', _('Russian')),
]
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/admin/login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = '/home/voron/sites/cdn/maps'

STATIC_URL = STATIC_URL = '/static/' if DEBUG else 'https://cdn.mkeda.me/maps/'

STATICFILES_DIRS = (
    ("", os.path.join(BASE_DIR, "static")),
)

MEDIA_URL = '/media/'

LOGIN_URL = '/login'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                 'django_jenkins.tasks.run_pep8',
                 'django_jenkins.tasks.run_pyflakes',)

PROJECT_APPS = ['core', 'maps']
