"""Assembly of the GraphQL schema.

Not to be confused with `products/api/schema.py`, which holds the OpenAPI
metadata for the REST adapter.
"""

import strawberry

from products.api.graphql.errors import DomainErrorExtension
from products.api.graphql.mutations import Mutation
from products.api.graphql.queries import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[DomainErrorExtension],
)
