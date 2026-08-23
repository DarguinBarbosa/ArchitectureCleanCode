from uuid import UUID

from shared.domain.exceptions import NotFoundError


class ProductNotFound(NotFoundError):
    """No Product exists with the requested identifier."""

    def __init__(self, product_id: UUID) -> None:
        super().__init__(f"No product exists with id {product_id}.")
