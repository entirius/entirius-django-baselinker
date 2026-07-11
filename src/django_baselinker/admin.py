# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin, messages
from django.utils.translation import ngettext

from . import models


@admin.register(models.BaselinkerAccount)
class BaselinkerAccountAdmin(admin.ModelAdmin):
    actions = ["refresh_statuses", "refresh_sources"]

    def refresh_statuses(self, request, queryset):
        updated = 0
        failed = 0
        for elem in queryset:
            try:
                (models.BaselinkerOrderStatus.objects.update_for_account(elem))
                updated += 1
            except Exception:
                failed += 1
        if failed == 0:
            self.message_user(
                request,
                ngettext(
                    "%d service statuses were successfully refreshed.",
                    "%d services statuses were successfully refreshed.",
                    updated,
                )
                % updated,
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                ngettext("%d service statuses failed to refresh.", "%d services statuses failed to refresh.", failed)
                % failed,
                messages.ERROR,
            )

    def refresh_sources(self, request, queryset):
        updated = 0
        failed = 0
        for elem in queryset:
            try:
                (models.BaselinkerOrderSource.objects.update_for_account(elem))
                updated += 1
            except Exception:
                failed += 1
        if failed == 0:
            self.message_user(
                request,
                ngettext(
                    "%d service order sources were successfully refreshed.",
                    "%d services order sources were successfully refreshed.",
                    updated,
                )
                % updated,
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                ngettext(
                    "%d service order sources failed to refresh.",
                    "%d services order sources failed to refresh.",
                    failed,
                )
                % failed,
                messages.ERROR,
            )


@admin.register(models.BaselinkerOrderStatus)
class BaselinkerOrderStatusAdmin(admin.ModelAdmin):
    readonly_fields = ["external_id", "external_data", "is_active", "inactive_since"]
    list_filter = ["account", "is_active"]
    search_fields = ["external_id"]


@admin.register(models.BaselinkerOrderSource)
class BaselinkerOrderSourceAdmin(admin.ModelAdmin):
    readonly_fields = ["source", "source_id", "external_data", "is_active", "inactive_since"]
    list_filter = ["account", "is_active"]
    search_fields = ["source", "source_id"]
