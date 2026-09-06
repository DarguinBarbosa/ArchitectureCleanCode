"""The one module that names the concrete repository.

Kept apart from `composition.py` on purpose: importing the builder must not
drag Django in, so the choice of adapter lives here and only here. Swapping
MySQL for another store is a one-line change in this file.
"""

from products.api.composition import ProductUseCases, build_use_cases
from products.infra.django_repository import DjangoProductRepository


def create_use_cases() -> ProductUseCases:
    return build_use_cases(DjangoProductRepository())
