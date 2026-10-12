# entirius-django-baselinker

A Django module that connects Entirius, the open-source modular ecommerce platform, to the Baselinker order manager.
It stores Baselinker accounts, mirrors order statuses, order sources and journal events, and wraps the
Baselinker API (https://api.baselinker.com/) in a client that reports rate-limit and blocked-token errors.

[![PyPI](https://img.shields.io/pypi/v/entirius-django-baselinker.svg)](https://pypi.org/project/entirius-django-baselinker/)
[![Python](https://img.shields.io/pypi/pyversions/entirius-django-baselinker.svg)](https://pypi.org/project/entirius-django-baselinker/)
[![License: MPL-2.0](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://github.com/entirius/entirius-django-baselinker/blob/develop/LICENSE)

## What it does

- Stores Baselinker accounts (email, token, base URL) as Django models.
- Mirrors order statuses and order sources of an account from the Baselinker API.
- Keeps Baselinker orders and journal events with typed journal log types.
- Wraps the Baselinker API methods (inventories, orders, invoices, packages) in `BaselinkerClient`.
- Raises dedicated errors for failed responses and blocked tokens.

## Installation

```shell
uv add entirius-django-baselinker
pip install entirius-django-baselinker
```

```python
INSTALLED_APPS = [
    ...
    "django_baselinker",
]

# urls.py
urlpatterns = [
    path("", include("django_baselinker.urls")),
]
```

The module has no required settings; accounts and their tokens live in the `BaselinkerAccount` model.

## Quick start

```python
from django_baselinker.models import BaselinkerAccount
from django_baselinker.utils import BaselinkerClient

client = BaselinkerClient.from_account(BaselinkerAccount.objects.get(email="shop@example.com"))
inventories = client.getInventories()
```

## Requirements

- Python 3.11 or newer, Django 4.0 or newer.
- Entirius packages pulled in: `entirius-py-int-enum-choices`.

## Documentation

- Module docs: https://github.com/entirius/entirius-django-baselinker/tree/develop/docs
- Entirius documentation: https://docs.entirius.com/
- Releases: https://github.com/entirius/entirius-django-baselinker/releases

## Part of Entirius

This module is an integration for the Entirius backend service (Volkanos); it has no sibling Django apps to install.

- Backend service: https://github.com/entirius/entirius-service-volkanos
- Docker harness: https://github.com/entirius/entirius-zeno
- Sibling modules: https://github.com/entirius/entirius-django-getresponse, https://github.com/entirius/entirius-django-utils

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: https://github.com/entirius/entirius-django-baselinker/blob/develop/AGENTS.md

## License

Mozilla Public License 2.0 (MPL-2.0) — see https://github.com/entirius/entirius-django-baselinker/blob/develop/LICENSE.
