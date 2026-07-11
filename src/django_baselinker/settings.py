# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.conf import settings

DEBUG = getattr(settings, "DEBUG", False)

# path  adresu url api klienta
PUBLIC_BASE_URL = getattr(settings, "API_PUBLIC_BASE_URL", "api")
if PUBLIC_BASE_URL is not None:
    PUBLIC_BASE_URL = PUBLIC_BASE_URL.strip("/")
