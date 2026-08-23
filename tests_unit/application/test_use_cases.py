"""Tests for the use cases with an in-memory fake repository. No DB, no Django."""

import unittest
from decimal import Decimal
from uuid import uuid4

from products.application.exceptions import ProductNotFound
from products.application.use_cases import (
    CreateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
)
from products.domain.exceptions import InvalidPrice
from tests_unit.doubles.in_memory_repository import InMemoryProductRepository


class UseCaseTestCase(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryProductRepository()

    def _create(self, name="Mouse", description="RGB", price=Decimal("25.50")):
        return CreateProduct(self.repository).execute(
            name=name, description=description, price=price
        )


class CreateProductTests(UseCaseTestCase):
    def test_persists_and_returns_the_entity(self):
        created = self._create()
        self.assertEqual(self.repository.get_by_id(created.id), created)

    def test_generates_id(self):
        self.assertIsNotNone(self._create().id)


class GetProductTests(UseCaseTestCase):
    def test_returns_the_existing_one(self):
        created = self._create()
        self.assertEqual(GetProduct(self.repository).execute(created.id), created)

    def test_missing_raises_not_found(self):
        with self.assertRaises(ProductNotFound):
            GetProduct(self.repository).execute(uuid4())


class ListProductsTests(UseCaseTestCase):
    def test_empty_at_start(self):
        self.assertEqual(ListProducts(self.repository).execute(), [])

    def test_returns_all(self):
        self._create(name="A")
        self._create(name="B")
        self.assertEqual(len(ListProducts(self.repository).execute()), 2)


class UpdateProductTests(UseCaseTestCase):
    def test_updates_fields_and_keeps_id(self):
        created = self._create()
        updated = UpdateProduct(self.repository).execute(
            created.id, name="Mouse Pro", description="New", price=Decimal("40")
        )
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.name, "Mouse Pro")
        self.assertEqual(self.repository.get_by_id(created.id).name, "Mouse Pro")

    def test_missing_raises_not_found(self):
        with self.assertRaises(ProductNotFound):
            UpdateProduct(self.repository).execute(
                uuid4(), name="X", description="", price=Decimal("1")
            )

    def test_invalid_value_revalidates(self):
        created = self._create()
        with self.assertRaises(InvalidPrice):
            UpdateProduct(self.repository).execute(
                created.id, name="X", description="", price=Decimal("-1")
            )


class DeleteProductTests(UseCaseTestCase):
    def test_deletes(self):
        created = self._create()
        DeleteProduct(self.repository).execute(created.id)
        self.assertIsNone(self.repository.get_by_id(created.id))

    def test_missing_raises_not_found(self):
        with self.assertRaises(ProductNotFound):
            DeleteProduct(self.repository).execute(uuid4())


if __name__ == "__main__":
    unittest.main()
