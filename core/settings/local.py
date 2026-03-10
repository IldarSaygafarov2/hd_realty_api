"""
Local / development settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

_allowed = set(env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"]))
_allowed.add("0.0.0.0")  # для Docker
ALLOWED_HOSTS = list(_allowed)

# Database - PostgreSQL when DB_HOST set (Docker), otherwise SQLite
if env("DB_HOST", default=""):
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
            "NAME": env("DB_NAME", default="hd_realty"),
            "USER": env("DB_USER", default="postgres"),
            "PASSWORD": env("DB_PASSWORD", default="postgres"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }
