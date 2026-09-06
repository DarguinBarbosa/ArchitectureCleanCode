"""What every resolver is handed.

Carries the use cases, never the repository: a resolver has no business
knowing that persistence exists. Request and response travel along because
the Django view supplies them and Strawberry expects to find them.

Deliberately free of framework imports —they are typed loosely on purpose—
so that importing the schema does not drag Django in. That is what lets the
tests run the whole schema with no database.
"""

from dataclasses import dataclass
from typing import Any

from products.api.composition import ProductUseCases


@dataclass(frozen=True, slots=True)
class GraphQLContext:
    use_cases: ProductUseCases
    request: Any = None
    response: Any = None
