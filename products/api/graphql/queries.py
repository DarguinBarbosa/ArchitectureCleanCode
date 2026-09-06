"""Read operations.

Each resolver takes the use case from the context and maps the result. It
never builds a use case, never resolves a repository and never decides
anything about the business.
"""

from uuid import UUID

import strawberry
from strawberry.types import Info

from products.api.graphql.context import GraphQLContext
from products.api.graphql.types import ProductType


@strawberry.type
class Query:
    @strawberry.field(description="Every product in the catalogue.")
    def products(self, info: Info[GraphQLContext, None]) -> list[ProductType]:
        products = info.context.use_cases.list_all.execute()
        return [ProductType.from_entity(product) for product in products]

    @strawberry.field(description="A single product, or a NOT_FOUND error.")
    def product(self, info: Info[GraphQLContext, None], id: UUID) -> ProductType:
        product = info.context.use_cases.get.execute(id)
        return ProductType.from_entity(product)
