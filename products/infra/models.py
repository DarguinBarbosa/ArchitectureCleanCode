from django.db import models

from products.domain.product import (
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
)

PRICE_MAX_DIGITS = 12
PRICE_DECIMAL_PLACES = 2
PRODUCT_TABLE = "product"


class ProductModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    description = models.CharField(max_length=MAX_DESCRIPTION_LENGTH, blank=True)
    price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES
    )

    class Meta:
        app_label = "products"
        db_table = PRODUCT_TABLE
