"""GraphQL adapter.

Sibling of the REST adapter, under the same rule: resolvers only
orchestrate. Every operation goes through the application use cases, so
neither the ORM nor a business rule is reachable from here.
"""
