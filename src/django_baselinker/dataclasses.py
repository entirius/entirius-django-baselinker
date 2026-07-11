# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from marshmallow_dataclass import dataclass


@dataclass
class BaselinkerProductData:
    storage: str
    storage_id: int
    product_id: str | None
    variant_id: int | None
    name: str
    sku: str
    ean: str
    attributes: str
    price_brutto: float
    tax_rate: int
    quantity: int
    weight: float


@dataclass
class BaselinkerOrderData:
    order_status_id: int
    date_add: int
    currency: str
    payment_method: str
    payment_method_cod: bool
    paid: bool
    user_comments: str | None
    admin_comments: str | None
    email: str
    phone: str
    user_login: str | None
    delivery_method: str
    delivery_price: float
    delivery_fullname: str
    delivery_company: str | None
    delivery_address: str
    delivery_postcode: str
    delivery_city: str
    delivery_country_code: str
    delivery_point_id: str | None
    delivery_point_name: str | None
    delivery_point_address: str | None
    delivery_point_postcode: str | None
    delivery_point_city: str | None
    invoice_fullname: str
    invoice_company: str
    invoice_nip: str
    invoice_address: str
    invoice_postcode: str
    invoice_city: str
    invoice_country_code: str
    want_invoice: bool
    extra_field_1: str | None
    extra_field_2: str | None
    products: list[BaselinkerProductData]
