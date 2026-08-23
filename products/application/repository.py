from abc import ABC, abstractmethod
from uuid import UUID

from products.domain.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        """Persist a new product and return it."""

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        """Return the product, or None if it does not exist (no exception)."""

    @abstractmethod
    def list_all(self) -> list[Product]:
        """Return every product."""

    @abstractmethod
    def update(self, product: Product) -> Product:
        """Update an existing product and return it."""

    @abstractmethod
    def delete(self, product_id: UUID) -> None:
        """Delete the product with the given id."""
