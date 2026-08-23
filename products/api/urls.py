from django.urls import path

from products.api.views import ProductDetailView, ProductsView

urlpatterns = [
    path("products/", ProductsView.as_view(), name="products"),
    path(
        "products/<uuid:product_id>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]
