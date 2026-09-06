"""GraphQL representation of a product.

`ProductType` is a transport shape, not the domain entity. It is declared
separately —like the REST serializers— so that renaming or hiding a field
in the API never forces a change in `domain`.
"""

from decimal import Decimal
from uuid import UUID

import strawberry

from products.domain.product import Product


@strawberry.type(name="Product", description="A product in the catalogue.")
class ProductType:
    id: UUID
    name: str
    description: str
    price: Decimal

    @classmethod
    def from_entity(cls, product: Product) -> "ProductType":
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
        )


@strawberry.input(description="Fields accepted when creating or replacing a product.")
class ProductInput:
    name: str
    price: Decimal
    description: str = ""
