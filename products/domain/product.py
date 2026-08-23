from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from products.domain.exceptions import (
    InvalidDescription,
    InvalidName,
    InvalidPrice,
)

MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MIN_PRICE = Decimal("0")


@dataclass(frozen=True, slots=True, kw_only=True)
class Product:
    id: UUID = field(default_factory=uuid4)
    name: str
    description: str
    price: Decimal

    def __post_init__(self) -> None:
        self._validate_name()
        self._validate_description()
        self._validate_price()

    def _validate_name(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidName("Product name is required.")
        if len(self.name) > MAX_NAME_LENGTH:
            raise InvalidName(
                f"Product name cannot exceed {MAX_NAME_LENGTH} characters."
            )

    def _validate_description(self) -> None:
        if not isinstance(self.description, str):
            raise InvalidDescription("Product description must be text.")
        if len(self.description) > MAX_DESCRIPTION_LENGTH:
            raise InvalidDescription(
                f"Product description cannot exceed {MAX_DESCRIPTION_LENGTH} characters."
            )

    def _validate_price(self) -> None:
        if not isinstance(self.price, Decimal):
            raise InvalidPrice("Price must be a Decimal.")
        if self.price < MIN_PRICE:
            raise InvalidPrice("Price cannot be negative.")
