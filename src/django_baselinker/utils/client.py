# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import logging
from datetime import datetime
from json.decoder import JSONDecodeError

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class BaselinkerResponseError(Exception):
    """Error raised when too many requests done to Baselinker per minute"""

    def __init__(
        self,
        error_message: str,
        url: str,
        request_params: dict,
        response: requests.Response,
        result_json: dict | None = None,
    ):
        self.url = url
        self.request_params = request_params
        self.response = response
        self.result_json = result_json
        message = (
            f"Url: {url}\n"
            + f"Request params: {request_params}\n"
            + f"Response code: {response.status_code}\n"
            + f"Response json: \n\n{result_json}\n"
        )
        super().__init__(message)


class BaselinkerBlockedTokenResponseError(BaselinkerResponseError):
    """Error raised when too many requests done to Baselinker per minute"""


class BaselinkerClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token
        super().__init__()

    @classmethod
    def from_account(cls, account):
        return cls(account.base_url, account.token)

    @classmethod
    def from_account(cls, account):
        return cls(account.base_url, account.token)

    def make_request(self, method: str, params: dict):
        req_data = {"token": self.token, "method": method, "parameters": json.dumps(params)}
        res = requests.post(self.url, req_data)
        try:
            result = res.json()
        except JSONDecodeError:
            raise BaselinkerResponseError(
                error_message="Response does not contain valid json data",
                url=self.url,
                request_params=params,
                response=res,
            )
        if settings.DEBUG:
            logger.debug(
                f"Baselinker REQUEST url={self.url} params={params}\nBaselinker RESP code={res.status_code}:\n{result}"
            )
        if res.status_code > 399:
            raise BaselinkerResponseError(
                error_message=result.get("error_message"),
                url=self.url,
                request_params=params,
                response=res,
                result_json=result,
            )
        assert "status" in result, "can not find status field in Baselinker response"
        if result["status"] == "ERROR" and result["error_code"] == "ERROR_BLOCKED_TOKEN":
            # RESP True: {'status': 'ERROR', 'error_code': 'ERROR_BLOCKED_TOKEN',
            # 'error_message': 'Query limit exceeded, token blocked until 2022-05-03 17:15:34'}
            if result["error_message"][:18] == "Query limit exceed":
                raise BaselinkerBlockedTokenResponseError(
                    error_message=result["error_message"],
                    url=self.url,
                    request_params=params,
                    response=res,
                    result_json=result,
                )
        if result["status"] != "SUCCESS":
            try:
                error_message = str(result["error_message"])
            except:
                error_message = "Unknown error"
            raise BaselinkerResponseError(
                error_message=f"Error in making Baselinker: {error_message}",
                url=self.url,
                request_params=params,
                response=res,
                result_json=result,
            )
        return result

    def getInventories(self):
        return self.make_request("getInventories", {})

    def getInventoryProductList(self, inventory_id, page=1):
        return self.make_request("getInventoryProductList", {"inventory_id": inventory_id, "page": page})

    def getOrderStatusList(self):
        return self.make_request("getOrderStatusList", {})

    def getJournalList(self, last_log_id: int = None, logs_types: list[int] = None, order_id: int = None):
        kwargs = {"last_log_id": last_log_id, "logs_types": logs_types, "order_id": order_id}
        resp = self.make_request("getJournalList", {k: v for k, v in kwargs.items() if v is not None})
        # validating response
        assert "status" in resp, "can not find status in Baselinker getJournalList response"
        assert resp["status"] == "SUCCESS", "Error in Baselinker getJournalList response"
        assert "logs" in resp, "can not find orders in Baselinker getJournalList response"
        return list(resp["logs"])

    def getOrder(self, order_id: int, get_unconfirmed_orders=False, include_custom_extra_fields=True):
        orders = self.getOrders(
            query={"order_id": int(order_id)},
            get_unconfirmed_orders=get_unconfirmed_orders,
            include_custom_extra_fields=include_custom_extra_fields,
        )
        # validating response
        assert len(orders) == 1, f"there is no order {order_id} in Baselinker getOrder response"
        return orders[0]

    def getOrders(self, query: dict = {}, get_unconfirmed_orders=False, include_custom_extra_fields=True):
        query.update(
            {
                "get_unconfirmed_orders": get_unconfirmed_orders,
                "include_custom_extra_fields": include_custom_extra_fields,
            }
        )
        resp = self.make_request("getOrders", query)
        assert "orders" in resp, "can not find orders in Baselinker getOrders response"
        return list(resp["orders"])

    def getOrderTransactionDetails(self, order_id):
        resp = self.make_request("getOrderTransactionDetails", {"order_id": order_id})
        return resp

    def getOrderExtraFields(self, order_id: int):
        resp = self.make_request("getOrderExtraFields", {"order_id": order_id})
        return resp

    def addOrder(self, order_data):
        return self.make_request("addOrder", order_data)

    def setOrderPayment(self, order_id: int, payment_data):
        return self.make_request("setOrderPayment", {"order_id": order_id, **payment_data})

    def setOrderStatus(self, order_id: int, status_id):
        return self.make_request("setOrderStatus", {"order_id": order_id, "status_id": status_id})

    def setOrderFields(self, order_id: int, fields: dict) -> dict:
        """
        Example usage
        client = BaselinkerClient()
        client.setOrderField(231321, {"admin_comment": "There was an exception"})
        """
        return self.make_request("setOrderFields", {"order_id": order_id, **fields})

    def getOrderSources(self):
        resp = self.make_request("getOrderSources", {})
        assert "status" in resp, "No status in Baselinker getOrderSources response"
        assert resp["status"] == "SUCCESS", "Error in Baselinker getOrderSources response"
        assert "sources" in resp, "No sources list in Baselinker getOrderSources response"
        return resp["sources"]

    def getSeries(self):
        return self.make_request("getSeries", {})

    def addInvoice(self, order_id: int, series_id: int):
        return self.make_request("addInvoice", {"order_id": order_id, "series_id": series_id})

    def getInvoice(self, invoice_id: int):
        return self.make_request("getInvoices", {"invoice_id": invoice_id})

    def getInvoices(self, order_id: int, series_id: int):
        return self.make_request("getInvoices", {"order_id": order_id})

    def addOrderInvoiceFile(self, invoice_id: int, file_b64: str, external_invoice_number: str):
        return self.make_request(
            "addOrderInvoiceFile",
            {"invoice_id": invoice_id, "file": file_b64, "external_invoice_number": external_invoice_number},
        )

    def createPackageManual(
        self, order_id: int, courier_code: str, package_number: str, pickup_date: datetime, return_shipment: str
    ):
        return self.make_request(
            "createPackageManual",
            {
                "order_id": order_id,
                "courier_code": courier_code,
                "package_number": package_number,
                "pickup_date": int(pickup_date.timestamp()),
                "return_shipment": return_shipment,
            },
        )
