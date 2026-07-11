# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Smoke tests: every module imports, models register, client instantiates."""

import importlib
import pkgutil

import pytest

import django_baselinker


def test_all_modules_import():
    for mod in pkgutil.walk_packages(django_baselinker.__path__, prefix="django_baselinker."):
        importlib.import_module(mod.name)


@pytest.mark.django_db
def test_account_model_roundtrip():
    from django_baselinker.models import BaselinkerAccount

    account = BaselinkerAccount.objects.create(
        email="shop@example.com", base_url="https://api.baselinker.com", token="x"
    )
    assert BaselinkerAccount.objects.get(pk=account.pk).email == "shop@example.com"


def test_client_from_account_builds_client():
    from django_baselinker.models import BaselinkerAccount
    from django_baselinker.utils import BaselinkerClient

    account = BaselinkerAccount(email="shop@example.com", base_url="https://api.baselinker.com", token="x")
    client = BaselinkerClient.from_account(account)
    assert client.url == "https://api.baselinker.com"
