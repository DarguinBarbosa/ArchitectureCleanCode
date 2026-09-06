"""Wiring of the use cases.

Free of any framework: it imports neither Django nor Strawberry, only the
application layer. That is what lets the tests build the same bundle over an
in-memory repository, with no database and no framework loaded.

The repository is injected here and nowhere else. Adapters receive ready-to-run
use cases, so no presentation code ever learns that a repository exists.
"""

from dataclasses import dataclass

from products.application.repository import ProductRepository
from products.application.use_cases import (
    CreateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
)


@dataclass(frozen=True, slots=True)
class ProductUseCases:
    """Everything the web layer is allowed to do with products."""

    create: CreateProduct
    get: GetProduct
    list_all: ListProducts
    update: UpdateProduct
    delete: DeleteProduct


def build_use_cases(repository: ProductRepository) -> ProductUseCases:
    return ProductUseCases(
        create=CreateProduct(repository),
        get=GetProduct(repository),
        list_all=ListProducts(repository),
        update=UpdateProduct(repository),
        delete=DeleteProduct(repository),
    )
