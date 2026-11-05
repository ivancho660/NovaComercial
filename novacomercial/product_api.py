
import json
import os
from urllib.request import urlopen
from urllib.error import URLError


PRODUCT_SERVICE_URL = os.environ.get(
    "PRODUCT_SERVICE_URL",
    "http://127.0.0.1:5001"
)


class ProductServiceUnavailable(Exception):
    pass


def get_products_from_service():
    url = f"{PRODUCT_SERVICE_URL}/api/products"

    try:
        with urlopen(url, timeout=5) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

            return data["products"]

    except (URLError, TimeoutError, ValueError, KeyError) as error:
        raise ProductServiceUnavailable(
            "No fue posible conectar con el servicio de productos."
        ) from error
