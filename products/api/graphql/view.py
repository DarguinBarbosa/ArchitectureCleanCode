"""The Django view that serves the schema.

The only piece of the GraphQL adapter that touches Django. It exists to do
one thing: build the context, so that every resolver is handed use cases
that are already wired to a repository.
"""

from django.http import HttpRequest, HttpResponse
from strawberry.django.views import GraphQLView

from products.api.dependencies import create_use_cases
from products.api.graphql.context import GraphQLContext


class ProductsGraphQLView(GraphQLView):
    def get_context(
        self, request: HttpRequest, response: HttpResponse
    ) -> GraphQLContext:
        return GraphQLContext(
            use_cases=create_use_cases(),
            request=request,
            response=response,
        )
