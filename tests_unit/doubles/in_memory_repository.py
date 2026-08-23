"""Test double: in-memory repository.

Implements the same abstract interface (ProductRepository) as the real
adapter, but stores everything in a dict. Lets us test the use cases without
a database or Django.
"""

from uuid import UUID

from products.application.repository import ProductRepository
from products.domain.product import Product


class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._by_id: dict[UUID, Product] = {}

    def create(self, product: Product) -> Product:
        self._by_id[product.id] = product
        return product

    def get_by_id(self, product_id: UUID) -> Product | None:
        return self._by_id.get(product_id)

    def list_all(self) -> list[Product]:
        return list(self._by_id.values())

    def update(self, product: Product) -> Product:
        self._by_id[product.id] = product
        return product

    def delete(self, product_id: UUID) -> None:
        self._by_id.pop(product_id, None)
