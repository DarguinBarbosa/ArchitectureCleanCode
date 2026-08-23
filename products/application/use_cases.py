from dataclasses import replace
from decimal import Decimal
from uuid import UUID

from products.application.exceptions import ProductNotFound
from products.application.repository import ProductRepository
from products.domain.product import Product


def _get_or_fail(repository: ProductRepository, product_id: UUID) -> Product:
    product = repository.get_by_id(product_id)
    if product is None:
        raise ProductNotFound(product_id)
    return product


class CreateProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, name: str, description: str, price: Decimal) -> Product:
        product = Product(name=name, description=description, price=price)
        return self._repository.create(product)


class GetProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: UUID) -> Product:
        return _get_or_fail(self._repository, product_id)


class ListProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Product]:
        return self._repository.list_all()


class UpdateProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(
        self, product_id: UUID, name: str, description: str, price: Decimal
    ) -> Product:
        existing = _get_or_fail(self._repository, product_id)
        updated = replace(existing, name=name, description=description, price=price)
        return self._repository.update(updated)


class DeleteProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: UUID) -> None:
        _get_or_fail(self._repository, product_id)
        self._repository.delete(product_id)
