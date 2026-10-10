# AGENTS.md

`entirius-django-baselinker` (Django app `django_baselinker`) — Baselinker integration module of Entirius: accounts,
mirrored order statuses, order sources and journal events, and an API client.

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
- No AI attribution in commits or PR descriptions.

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

| Topic | Where |
|---|---|
| Baselinker API reference (external) | `docs/_index.md` |
| Client methods and error types | `src/django_baselinker/utils/client.py` |
| Journal log types | `src/django_baselinker/models.py` (`JournalLogType`) |
