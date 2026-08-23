from shared.domain.exceptions import ValidationError


class InvalidProduct(ValidationError):
    """A Product's state violates one or more of its business rules."""


class InvalidName(InvalidProduct):
    """The product name does not meet the business rules."""


class InvalidDescription(InvalidProduct):
    """The product description does not meet the business rules."""


class InvalidPrice(InvalidProduct):
    """The product price does not meet the business rules."""
