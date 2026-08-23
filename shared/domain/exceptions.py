"""Shared kernel: base exceptions common to all apps.

Pure Python, with no dependency on Django or on any feature. Each domain
extends these bases so the global handler can map by category (not found /
validation) without knowing any concrete app.
"""


class DomainError(Exception):
    """Root of every business exception, in any app."""


class NotFoundError(DomainError):
    """The requested resource does not exist. The handler maps it to 404."""


class ValidationError(DomainError):
    """A business rule was violated. The handler maps it to 400."""
