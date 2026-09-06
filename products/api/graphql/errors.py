"""Translation of domain exceptions into GraphQL errors.

The GraphQL counterpart of `config/exception_handler.py`: a single place
that maps by category and never imports a concrete feature. GraphQL always
answers 200, so the category travels in `extensions.code` instead of the
HTTP status.

Anything that is not a DomainError is left untouched, so a bug surfaces as
an internal error instead of being disguised as a business rule.
"""

from graphql import GraphQLError
from strawberry.extensions import SchemaExtension

from shared.domain.exceptions import NotFoundError, ValidationError

NOT_FOUND_CODE = "NOT_FOUND"
BAD_REQUEST_CODE = "BAD_REQUEST"


def _as_graphql_error(exc: Exception, code: str) -> GraphQLError:
    return GraphQLError(
        str(exc),
        original_error=exc,
        extensions={"code": code, "type": type(exc).__name__},
    )


class DomainErrorExtension(SchemaExtension):
    """Wraps every resolver so the mapping lives here and not in each one."""

    def resolve(self, _next, root, info, *args, **kwargs):
        try:
            return _next(root, info, *args, **kwargs)
        except NotFoundError as exc:
            raise _as_graphql_error(exc, NOT_FOUND_CODE) from exc
        except ValidationError as exc:
            raise _as_graphql_error(exc, BAD_REQUEST_CODE) from exc
