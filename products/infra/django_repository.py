from uuid import UUID

from products.application.repository import ProductRepository
from products.domain.product import Product
from products.infra.models import ProductModel


class DjangoProductRepository(ProductRepository):
    def create(self, product: Product) -> Product:
        ProductModel(id=product.id, **self._to_columns(product)).save(
            force_insert=True
        )
        return product

    def get_by_id(self, product_id: UUID) -> Product | None:
        model = ProductModel.objects.filter(pk=product_id).first()
        return self._to_entity(model) if model is not None else None

    def list_all(self) -> list[Product]:
        return [self._to_entity(model) for model in ProductModel.objects.all()]

    def update(self, product: Product) -> Product:
        ProductModel.objects.filter(pk=product.id).update(**self._to_columns(product))
        return product

    def delete(self, product_id: UUID) -> None:
        ProductModel.objects.filter(pk=product_id).delete()

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
        )

    @staticmethod
    def _to_columns(product: Product) -> dict[str, object]:
        return {
            "name": product.name,
            "description": product.description,
            "price": product.price,
        }
