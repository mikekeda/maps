"""
Django settings for maps project.
"""

import os
import requests
from django.utils.translation import ugettext_lazy as _

SITE_ENV_PREFIX = "MAPS"


def get_env_var(name, default=""):
    """Get all sensitive data from google vm custom metadata."""
    try:
        name = "_".join([SITE_ENV_PREFIX, name])
        res = os.environ.get(name)
        if res:
            # Check env variable (Jenkins build).
            return res
        else:
            res = requests.get(
                "http://metadata.google.internal/computeMetadata/"
                "v1/instance/attributes/{}".format(name),
                headers={"Metadata-Flavor": "Google"},
            )
            if res.status_code == 200:
                return res.text
    except requests.exceptions.ConnectionError:
        return default
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var(
    "SECRET_KEY", "zha7wy2q_pnfi=)h0zei!wukd6c^x(s9z*mb-+7j)rby)q_&t2"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(get_env_var("DEBUG", "True"))

ALLOWED_HOSTS = get_env_var("ALLOWED_HOSTS", "*").split(",")

INTERNAL_IPS = ("127.0.0.1",)

ADMINS = [("Mike", "mriynuk@gmail.com")]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "leaflet",
    "djgeojson",
    "easy_select2",
    "widget_tweaks",
    "mptt",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "import_export",
    "core",
    "covid",
]

if DEBUG:
    from debug_toolbar.settings import PANELS_DEFAULTS

    INSTALLED_APPS += ["debug_toolbar", "django_jenkins", "debug_toolbar_line_profiler"]
    DEBUG_TOOLBAR_PANELS = PANELS_DEFAULTS + [
        "debug_toolbar_line_profiler.panel.ProfilingPanel",
    ]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "maps.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "maps.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env_var("DB_NAME", "maps"),
        "USER": get_env_var("DB_USER", "maps_admin"),
        "PASSWORD": get_env_var("DB_PASSWORD", "maps_pass_!_12"),
        "HOST": get_env_var("DB_HOST", "127.0.0.1"),
        "PORT": "",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Security
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_PRELOAD = True


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "/"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "facebook": {
        "METHOD": "oauth2",
        "SDK_URL": "//connect.facebook.net/{locale}/sdk.js",
        "SCOPE": ["email"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "email",
            "name",
            "first_name",
            "last_name",
            "verified",
            "locale",
            "timezone",
            "link",
            "gender",
            "updated_time",
        ],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": True,
        "VERSION": "v6.0",
    }
}

EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 2525
EMAIL_HOST_USER = get_env_var("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_env_var("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
MAILGUN_SERVER_NAME = "maps.mkeda.me"
EMAIL_SUBJECT_PREFIX = "[Maps]"
SERVER_EMAIL = "admin@maps.mkeda.me"

# Internationalization
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", _("English")),
    ("es", _("Spanish")),
    ("uk", _("Ukrainian")),
    ("it", _("Italian")),
    ("fr", _("French")),
    ("ru", _("Russian")),
]
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale/"),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = "/home/voron/sites/cdn/maps"

STATIC_URL = "https://storage.googleapis.com/cdn.mkeda.me/maps/"
if DEBUG:
    STATIC_URL = "/static/"

STATICFILES_DIRS = (("", os.path.join(BASE_DIR, "static")),)

MEDIA_URL = "/media/"

LOGIN_URL = "/login"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# CELERY STUFF
CELERY_BROKER_URL = "redis://localhost:6379/2"
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

JENKINS_TASKS = (
    "django_jenkins.tasks.run_pylint",
    "django_jenkins.tasks.run_pep8",
    "django_jenkins.tasks.run_pyflakes",
)

PROJECT_APPS = ["core", "maps"]

PYLINT_LOAD_PLUGIN = ["pylint_django"]

GOOGLE_MAP_API_KEY = get_env_var("GOOGLE_MAP_API_KEY")
