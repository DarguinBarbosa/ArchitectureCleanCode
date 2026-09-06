"""Architecture guardrail: the inner layers must not pull in any framework.

Domain and application may not depend on Django, on DRF or on GraphQL. Those
are outer-ring details, reachable only through an adapter. If this test
fails, a dependency leaked where it should not.

The check runs in a subprocess on purpose. Reading `sys.modules` in this
process would only prove what the whole test run has imported so far — and
the GraphQL tests legitimately import Strawberry. A clean interpreter is the
only way to measure what these modules drag in by themselves.
"""

import subprocess
import sys
import unittest

MODULES_UNDER_TEST = (
    "products.domain.product",
    "products.application.use_cases",
    "products.api.composition",
    "tests_unit.doubles.in_memory_repository",
)

FORBIDDEN_PACKAGES = (
    "django",
    "rest_framework",
    "strawberry",
    "graphql",
)

PROBE = """
import importlib, sys
for module in {modules!r}:
    importlib.import_module(module)
print(",".join(p for p in {forbidden!r} if p in sys.modules))
"""


class FrameworkIsolation(unittest.TestCase):
    def test_no_framework_is_loaded(self):
        probe = PROBE.format(
            modules=list(MODULES_UNDER_TEST), forbidden=list(FORBIDDEN_PACKAGES)
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            check=True,
        )

        leaked = [name for name in result.stdout.strip().split(",") if name]
        self.assertEqual(leaked, [], f"the inner layers pulled in: {leaked}")


if __name__ == "__main__":
    unittest.main()
