"""Tests for the Product domain entity. No DB, no Django."""

import unittest
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from uuid import UUID

from products.domain.exceptions import (
    InvalidDescription,
    InvalidName,
    InvalidPrice,
)
from products.domain.product import (
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    Product,
)


def _valid_product(**overrides) -> Product:
    data = dict(name="Mouse", description="Wireless", price=Decimal("25.50"))
    data.update(overrides)
    return Product(**data)


class ValidProduct(unittest.TestCase):
    def test_generates_its_own_uuid4_id(self):
        product = _valid_product()
        self.assertIsInstance(product.id, UUID)
        self.assertEqual(product.id.version, 4)

    def test_each_product_has_a_distinct_id(self):
        self.assertNotEqual(_valid_product().id, _valid_product().id)

    def test_keeps_the_values(self):
        product = _valid_product(name="Keyboard", price=Decimal("99.90"))
        self.assertEqual(product.name, "Keyboard")
        self.assertEqual(product.price, Decimal("99.90"))

    def test_is_immutable(self):
        product = _valid_product()
        with self.assertRaises(FrozenInstanceError):
            product.name = "other"

    def test_zero_price_is_valid(self):
        self.assertEqual(_valid_product(price=Decimal("0")).price, Decimal("0"))

    def test_empty_description_is_valid(self):
        self.assertEqual(_valid_product(description="").description, "")


class InvalidNameTests(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(InvalidName):
            _valid_product(name="")

    def test_only_whitespace(self):
        with self.assertRaises(InvalidName):
            _valid_product(name="   ")

    def test_not_text(self):
        with self.assertRaises(InvalidName):
            _valid_product(name=123)

    def test_exceeds_max_length(self):
        with self.assertRaises(InvalidName):
            _valid_product(name="x" * (MAX_NAME_LENGTH + 1))


class InvalidDescriptionTests(unittest.TestCase):
    def test_not_text(self):
        with self.assertRaises(InvalidDescription):
            _valid_product(description=None)

    def test_exceeds_max_length(self):
        with self.assertRaises(InvalidDescription):
            _valid_product(description="x" * (MAX_DESCRIPTION_LENGTH + 1))


class InvalidPriceTests(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(InvalidPrice):
            _valid_product(price=Decimal("-0.01"))

    def test_float_rejected(self):
        with self.assertRaises(InvalidPrice):
            _valid_product(price=19.99)

    def test_int_rejected(self):
        with self.assertRaises(InvalidPrice):
            _valid_product(price=20)

    def test_str_rejected(self):
        with self.assertRaises(InvalidPrice):
            _valid_product(price="20")


class RevalidationOnUpdate(unittest.TestCase):
    def test_replace_revalidates_and_rejects_negative_price(self):
        product = _valid_product()
        with self.assertRaises(InvalidPrice):
            replace(product, price=Decimal("-1"))

    def test_replace_keeps_id(self):
        product = _valid_product()
        updated = replace(product, name="New")
        self.assertEqual(updated.id, product.id)


if __name__ == "__main__":
    unittest.main()
