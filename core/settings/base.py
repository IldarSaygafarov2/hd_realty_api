"""
Base Django settings - common for all environments.
"""

import os
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "project"
env = environ.Env()
env.read_env(ROOT_DIR / ".env")

# Application definition
INSTALLED_APPS = [
    "corsheaders",
    "modeltranslation",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.constance",
    "constance",
    "project.infrastructure.apps.InfrastructureConfig",
    "project.apps.categories.apps.CategoriesConfig",
    "project.apps.districts.apps.DistrictsConfig",
    "project.apps.advertisements.apps.AdvertisementsConfig",
    "project.apps.users.apps.UsersConfig",
    "project.apps.portfolio.apps.PortfolioConfig",
    "project.apps.consultations.apps.ConsultationsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database - override in local/production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ru", "Русский"),
    ("uz", "Oʻzbekcha"),
]

LOCALE_PATHS = [ROOT_DIR / "locale"]

# django-modeltranslation: name = русский, отдельное поле только для uz
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = ROOT_DIR / "staticfiles"

# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = ROOT_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key-not-for-production")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@hdrealty.local")

# CSRF: доверенные origins для прокси (nginx)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000"],
)

# CORS: для фронтенда на другом домене/порту
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = True

# Django Unfold
from django.templatetags.static import static

UNFOLD = {
    "SHOW_LANGUAGES": True,
    "SCRIPTS": [
        lambda request: static("users/js/notifications-poller.js"),
    ],
}

# django-constance: динамические параметры в БД
from decimal import Decimal as _Decimal  # noqa: E402

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_ADDITIONAL_FIELDS = {
    "decimal_rate": [
        "django.forms.DecimalField",
        {"max_digits": 14, "decimal_places": 4},
    ],
}
CONSTANCE_CONFIG = {
    "USD_RATE": (
        _Decimal("12000.0000"),
        "Курс 1 USD к UZS. Обновляется автоматически с cbu.uz каждый день в 09:00.",
        "decimal_rate",
    ),
}
CONSTANCE_CONFIG_FIELDSETS = {
    "Курс валют": ("USD_RATE",),
}
