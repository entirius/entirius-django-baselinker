# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Standalone Django settings for django-baselinker tests."""

SECRET_KEY = "not so secret test secret"  # noqa: S105
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_baselinker",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
