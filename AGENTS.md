# AGENTS.md

Baselinker Django module for Volkanos — distribution `entirius-django-baselinker`, Django app `django_baselinker`.

## Commands

| Command | Meaning |
|---|---|
| `make install` | sync dependencies (uv, incl. extras) |
| `make check` | lint + format-check (ruff) |
| `make fix` | auto-fix lint + format |
| `make test` | test suite (pytest + pytest-django) |

## Conventions

- English only: code, docs, commits, branches, PRs.
- MPL-2.0: every non-trivial source file carries the license header (pre-commit inserts it).
- Toolchain: uv + ruff + hatchling + pytest; all config in `pyproject.toml`; `uv.lock` committed.
- Git flow: `master` (production) + `develop` (integration); changes land via PR; semver tag on `master`.
- Never rename the package / Django app_label / DB table prefix `django_baselinker` — it is a schema contract.
- Migrations are part of the public contract — never edit an already released migration.
- Default: do not commit — git is the user's call.

## Architecture

```
src/django_baselinker/
├── models.py          # BaselinkerAccount, BaselinkerOrderStatus, BaselinkerOrderSource,
│                      # BaselinkerOrder, BaselinkerEvent (+ managers syncing from API data)
├── dataclasses.py     # marshmallow_dataclass DTOs for Baselinker API payloads
├── utils/client.py    # BaselinkerClient — API wrapper, rate-limit / blocked-token errors
├── admin.py           # Django admin registrations
├── settings.py        # module settings read from django.conf.settings
└── migrations/        # single 0001_initial (schema contract)
```

Integration point: `BaselinkerClient.from_account(BaselinkerAccount)`; managers
`update_from_data` / `update_for_account` mirror statuses and sources from the API.
