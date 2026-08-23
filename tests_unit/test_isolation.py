"""Architecture guardrail: the domain and application tests must not pull in
Django. If this test fails, a dependency leaked where it should not.
"""

import importlib
import sys
import unittest

MODULES_UNDER_TEST = (
    "products.domain.product",
    "products.application.use_cases",
    "tests_unit.doubles.in_memory_repository",
)


class DjangoIsolation(unittest.TestCase):
    def test_django_is_not_loaded(self):
        for module in MODULES_UNDER_TEST:
            importlib.import_module(module)
        self.assertNotIn("django", sys.modules)


if __name__ == "__main__":
    unittest.main()
