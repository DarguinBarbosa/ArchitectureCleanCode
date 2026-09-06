"""The GraphQL schema, exercised end to end without a database.

Injecting use cases through the context is what makes this possible: the
same bundle the Django view builds over MySQL is built here over an
in-memory repository. No Django, no DB, no HTTP.
"""

import logging
import unittest
from decimal import Decimal
from uuid import uuid4

from products.api.composition import build_use_cases
from products.api.graphql.context import GraphQLContext
from products.api.graphql.schema import schema
from tests_unit.doubles.in_memory_repository import InMemoryProductRepository

MISSING_ID = "11111111-1111-1111-1111-111111111111"


class GraphQLSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Strawberry logs every error it processes. That is right in production
        # and pure noise here, where failing on purpose is half the suite.
        logging.getLogger("strawberry.execution").setLevel(logging.CRITICAL)

    def setUp(self):
        self.repository = InMemoryProductRepository()
        self.context = GraphQLContext(use_cases=build_use_cases(self.repository))

    def execute(self, query: str):
        return schema.execute_sync(query, context_value=self.context)

    def create_product(self, name="Keyboard", price="89.90", description="TKL"):
        return self.execute(
            f'mutation {{ createProduct(input: {{name: "{name}", '
            f'price: "{price}", description: "{description}"}}) '
            f"{{ id name description price }} }}"
        )

    def assert_error_code(self, result, expected_code: str, expected_type: str):
        self.assertIsNotNone(result.errors)
        extensions = result.errors[0].extensions
        self.assertEqual(extensions["code"], expected_code)
        self.assertEqual(extensions["type"], expected_type)

    # --- queries -----------------------------------------------------------

    def test_products_returns_an_empty_list_when_there_is_nothing(self):
        result = self.execute("{ products { id } }")

        self.assertIsNone(result.errors)
        self.assertEqual(result.data["products"], [])

    def test_products_returns_what_the_repository_holds(self):
        self.create_product(name="Mouse")
        self.create_product(name="Monitor")

        result = self.execute("{ products { name } }")

        self.assertIsNone(result.errors)
        names = [product["name"] for product in result.data["products"]]
        self.assertEqual(sorted(names), ["Monitor", "Mouse"])

    def test_a_query_returns_only_the_requested_fields(self):
        self.create_product()

        result = self.execute("{ products { name } }")

        self.assertEqual(list(result.data["products"][0].keys()), ["name"])

    def test_product_returns_a_single_item_by_id(self):
        created = self.create_product(name="Webcam").data["createProduct"]

        result = self.execute(f'{{ product(id: "{created["id"]}") {{ name }} }}')

        self.assertIsNone(result.errors)
        self.assertEqual(result.data["product"]["name"], "Webcam")

    def test_product_reports_not_found_for_an_unknown_id(self):
        result = self.execute(f'{{ product(id: "{MISSING_ID}") {{ name }} }}')

        self.assert_error_code(result, "NOT_FOUND", "ProductNotFound")

    # --- mutations ---------------------------------------------------------

    def test_create_product_persists_and_returns_it(self):
        result = self.create_product(name="Headset", price="120.00")

        self.assertIsNone(result.errors)
        created = result.data["createProduct"]
        self.assertEqual(created["name"], "Headset")
        self.assertEqual(created["price"], "120.00")
        self.assertEqual(len(self.repository.list_all()), 1)

    def test_create_product_defaults_the_description(self):
        result = self.execute(
            'mutation { createProduct(input: {name: "Cable", price: "3.00"}) '
            "{ description } }"
        )

        self.assertIsNone(result.errors)
        self.assertEqual(result.data["createProduct"]["description"], "")

    def test_update_product_replaces_every_field(self):
        created = self.create_product().data["createProduct"]

        result = self.execute(
            f'mutation {{ updateProduct(id: "{created["id"]}", '
            f'input: {{name: "Keyboard TKL", price: "99.00", '
            f'description: "No numpad"}}) {{ id name price description }} }}'
        )

        self.assertIsNone(result.errors)
        updated = result.data["updateProduct"]
        self.assertEqual(updated["id"], created["id"])
        self.assertEqual(updated["name"], "Keyboard TKL")
        self.assertEqual(updated["price"], "99.00")

    def test_update_product_reports_not_found_for_an_unknown_id(self):
        result = self.execute(
            f'mutation {{ updateProduct(id: "{MISSING_ID}", '
            f'input: {{name: "X", price: "1.00"}}) {{ id }} }}'
        )

        self.assert_error_code(result, "NOT_FOUND", "ProductNotFound")

    def test_delete_product_removes_it_and_echoes_the_id(self):
        created = self.create_product().data["createProduct"]

        result = self.execute(
            f'mutation {{ deleteProduct(id: "{created["id"]}") }}'
        )

        self.assertIsNone(result.errors)
        self.assertEqual(result.data["deleteProduct"], created["id"])
        self.assertEqual(self.repository.list_all(), [])

    def test_delete_product_reports_not_found_for_an_unknown_id(self):
        result = self.execute(f'mutation {{ deleteProduct(id: "{MISSING_ID}") }}')

        self.assert_error_code(result, "NOT_FOUND", "ProductNotFound")

    # --- business rules come from the entity, not from the resolver --------

    def test_a_negative_price_is_rejected_by_the_domain(self):
        result = self.create_product(price="-1.00")

        self.assert_error_code(result, "BAD_REQUEST", "InvalidPrice")
        self.assertEqual(self.repository.list_all(), [])

    def test_a_blank_name_is_rejected_by_the_domain(self):
        result = self.create_product(name="   ")

        self.assert_error_code(result, "BAD_REQUEST", "InvalidName")

    def test_the_price_reaches_the_domain_as_a_decimal(self):
        self.create_product(price="19.99")

        stored = self.repository.list_all()[0]
        self.assertIsInstance(stored.price, Decimal)
        self.assertEqual(stored.price, Decimal("19.99"))

    def test_the_id_is_generated_by_the_domain(self):
        created = self.create_product().data["createProduct"]

        stored = self.repository.list_all()[0]
        self.assertEqual(str(stored.id), created["id"])
        self.assertNotEqual(stored.id, uuid4())


if __name__ == "__main__":
    unittest.main()
