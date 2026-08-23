"""Model-registration shim.

Django discovers an app's models by importing '<app>.models'. The model
*definition* lives in infra; this module only re-exports it so the ORM
registers it. Do not add logic or new models here.
"""

from products.infra.models import ProductModel

__all__ = ["ProductModel"]
