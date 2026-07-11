# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from enum import IntEnum

from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from int_enum_choices import IntEnumChoices

from .utils import BaselinkerClient


class BaselinkerAccountManager(models.Manager):
    def availability_table(self, print_out=True):
        all_configs = self.all().order_by("pk")
        tpl = "| {:<60} | {:<97} |"
        tpl_all = "| {:<160} |"
        tpl_row = tpl.replace("|", "+")
        tpl_row = tpl_row.replace(":", ":-")
        tpl_row = tpl_row.replace(" ", "-")
        tpl_row = tpl_row.format("", "", "", "", "", "")

        txts = ["Available baselinker accounts:"]
        txts.append(tpl_row)
        txts.append(tpl.format("id", "name"))
        txts.append(tpl_row)
        for config in all_configs:
            txts.append(tpl.format(config.pk, config.email))
        if len(all_configs) == 0:
            txts.append(tpl_all.format("no baselinker accounts are available"))
        txts.append(tpl_row)
        txt = "\n".join(txts)
        if print_out:
            print("\n" + txt, flush=True)
        return txt


class BaselinkerAccount(models.Model):
    objects = BaselinkerAccountManager()
    email = models.EmailField()
    token = models.CharField(max_length=128)
    base_url = models.CharField(max_length=64)

    def __str__(self):
        return self.email


class BaselinkerOrderStatusManager(models.Manager):
    def update_from_data(self, data, account):
        """Updates status list for an account based on passed data,
        idempotent operation"""

        packed = {}
        for elem in data:
            packed[elem["id"]] = elem

        with transaction.atomic():
            active_ids = []
            for id in packed:
                record, _ = self.get_or_create(account=account, external_id=id)
                record.external_data = packed[id]
                record.is_active = True
                record.inactive_since = None
                record.save()
                active_ids.append(record.pk)

            to_inactivate = self.filter(account=account).exclude(is_active=False).exclude(pk__in=active_ids)
            to_inactivate.update(is_active=False, inactive_since=timezone.now())

    def update_for_account(self, account):
        data = BaselinkerClient.from_account(account).getOrderStatusList()["statuses"]
        self.update_from_data(data, account)


class BaselinkerOrderStatus(models.Model):
    """Table for storing possible order statuses from Baselinker"""

    objects = BaselinkerOrderStatusManager()
    account = models.ForeignKey(
        "BaselinkerAccount", related_name="order_statuses", on_delete=models.CASCADE, verbose_name="Baselinker account"
    )
    external_id = models.CharField(max_length=100, editable=False)
    external_data = models.JSONField(null=True, blank=True, editable=False)
    is_active = models.BooleanField(default=True, editable=False)
    inactive_since = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def name(self):
        return self.external_data.get("name", "Undefined name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Baselinker status"
        verbose_name_plural = "Baselinker statuses"


class BaselinkerOrderSourceManager(models.Manager):
    def update_from_data(self, data: dict, account):
        print(data)
        packed = {}
        for source_name in data:
            if isinstance(data[source_name], dict):
                for source_id in data[source_name]:
                    external_data = {"description": data[source_name][source_id]}
                    packed[(source_name, source_id)] = external_data
            else:
                # TODO figure out what to do in this case
                pass
        with transaction.atomic():
            active_ids = []
            for name, id in packed:
                record, _ = self.get_or_create(account=account, source=name, source_id=id)
                record.external_data = packed[(name, id)]
                record.save()
                active_ids.append(record.pk)

            to_inactivate = self.filter(account=account).exclude(pk__in=active_ids, is_active=False)
            to_inactivate.update(is_active=False, inactive_since=timezone.now())

    def update_for_account(self, account):
        data = BaselinkerClient.from_account(account).getOrderSources()
        self.update_from_data(data, account)


class BaselinkerOrderSource(models.Model):
    objects = BaselinkerOrderSourceManager()
    account = models.ForeignKey(
        "BaselinkerAccount", related_name="order_sources", on_delete=models.CASCADE, verbose_name="Baselinker account"
    )
    source = models.CharField(max_length=20)
    source_id = models.IntegerField()
    external_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    inactive_since = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def description(self):
        return self.external_data.get("description", f"{self.source}: {self.source_id}")

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Baselinker source"
        verbose_name_plural = "Baselinker sources"
        constraints = [models.UniqueConstraint(fields=["source", "source_id"], name="source_id_unique_per_source")]


class BaselinkerOrder(models.Model):
    account = models.ForeignKey("BaselinkerAccount", related_name="orders", on_delete=models.CASCADE)
    external_order_id = models.CharField(null=True, blank=True, max_length=128)
    baselinker_order_id = models.CharField(null=True, blank=True, max_length=64)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


# Log Types definitions based on:
# https://api.baselinker.com/index.php?method=getJournalList
class JournalLogTypeEnum(IntEnum):
    ORDER_CREATION = 1
    ORDER_CONFIRMATION = 2
    PAYMENT_OF_THE_ORDER = 3
    REMOVAL_OF_ORDER_INVOICE_RECEIPT = 4
    MERGING_THE_ORDERS = 5
    SPLITTING_THE_ORDER = 6
    ISSUING_AN_INVOICE = 7
    ISSUING_A_RECEIPT = 8
    PACKAGE_CREATION = 9
    DELETING_A_PACKAGE = 10
    EDITING_DELIVERY_DATA = 11
    ADDING_A_PRODUCT_TO_AN_ORDER = 12
    EDITING_THE_PRODUCT_IN_THE_ORDER = 13
    REMOVING_THE_PRODUCT_FROM_THE_ORDER = 14
    ADDING_A_BUYER_TO_A_BLACKLIST = 15
    EDITING_ORDER_DATA = 16
    COPYING_AN_ORDER = 17
    ORDER_STATUS_CHANGE = 18
    INVOICE_DELETION = 19
    RECEIPT_DELETION = 20


class JournalLogType(IntEnumChoices):
    enumClass = JournalLogTypeEnum
    labels = {
        JournalLogTypeEnum.ORDER_CREATION: "Order creation",
        JournalLogTypeEnum.ORDER_CONFIRMATION: "DOF download (order confirmation)",
        JournalLogTypeEnum.PAYMENT_OF_THE_ORDER: "Payment of the order",
        JournalLogTypeEnum.REMOVAL_OF_ORDER_INVOICE_RECEIPT: "Removal of order/invoice/receipt",
        JournalLogTypeEnum.MERGING_THE_ORDERS: "Merging the orders",
        JournalLogTypeEnum.SPLITTING_THE_ORDER: "Splitting the order",
        JournalLogTypeEnum.ISSUING_AN_INVOICE: "Issuing an invoice",
        JournalLogTypeEnum.ISSUING_A_RECEIPT: "Issuing a receipt",
        JournalLogTypeEnum.PACKAGE_CREATION: "Package creation",
        JournalLogTypeEnum.DELETING_A_PACKAGE: "Deleting a package",
        JournalLogTypeEnum.EDITING_DELIVERY_DATA: "Editing delivery data",
        JournalLogTypeEnum.ADDING_A_PRODUCT_TO_AN_ORDER: "Adding a product to an order",
        JournalLogTypeEnum.EDITING_THE_PRODUCT_IN_THE_ORDER: "Editing the product in the order",
        JournalLogTypeEnum.REMOVING_THE_PRODUCT_FROM_THE_ORDER: "Removing the product from the order",
        JournalLogTypeEnum.ADDING_A_BUYER_TO_A_BLACKLIST: "Adding a buyer to a blacklist",
        JournalLogTypeEnum.EDITING_ORDER_DATA: "Editing order data",
        JournalLogTypeEnum.COPYING_AN_ORDER: "Copying an order",
        JournalLogTypeEnum.ORDER_STATUS_CHANGE: "Order status change",
        JournalLogTypeEnum.INVOICE_DELETION: "Invoice deletion",
        JournalLogTypeEnum.RECEIPT_DELETION: "Receipt deletion ",
    }


class BaselinkerEvent(models.Model):
    status = models.CharField(
        max_length=16, choices=[("processed", _("Processed")), ("failed", _("Failed")), ("new", _("New"))]
    )
    account = models.ForeignKey(
        "BaselinkerAccount", related_name="logs", on_delete=models.CASCADE, verbose_name="Baselinker account"
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    log_id = models.IntegerField()
    log_type = models.IntegerField()  # TODO: use JournalLogType

    class Meta:
        ordering = ["created_at", "updated_at"]
