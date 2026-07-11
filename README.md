# django-baselinker

Baselinker integration module for Volkanos — stores Baselinker accounts, mirrors order statuses,
order sources and journal events, and wraps the [Baselinker API](https://api.baselinker.com/)
with a rate-limit-aware client.

## Installation

```shell
pip install entirius-django-baselinker
```

Add the app to your project:

```python
INSTALLED_APPS = [
    ...
    "django_baselinker",
]
```

## Usage

```python
from django_baselinker.models import BaselinkerAccount
from django_baselinker.utils import BaselinkerClient

client = BaselinkerClient.from_account(BaselinkerAccount.objects.get(email="shop@example.com"))
inventories = client.getInventories()
```

## Development

```shell
make install     # sync dependencies (uv)
make check       # lint + format check (ruff)
make test        # test suite (pytest + pytest-django)
```

Development and agent instructions: [AGENTS.md](AGENTS.md).

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).
