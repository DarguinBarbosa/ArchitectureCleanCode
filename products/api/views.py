from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.api.dependencies import create_use_cases
from products.api.schema import (
    create_product_schema,
    delete_product_schema,
    get_product_schema,
    list_products_schema,
    update_product_schema,
)
from products.api.serializers import (
    ProductInputSerializer,
    ProductOutputSerializer,
)


class ProductsView(APIView):
    @list_products_schema
    def get(self, request):
        products = create_use_cases().list_all.execute()
        return Response(ProductOutputSerializer(products, many=True).data)

    @create_product_schema
    def post(self, request):
        input_serializer = ProductInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        product = create_use_cases().create.execute(**input_serializer.validated_data)
        return Response(
            ProductOutputSerializer(product).data, status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    @get_product_schema
    def get(self, request, product_id):
        product = create_use_cases().get.execute(product_id)
        return Response(ProductOutputSerializer(product).data)

    @update_product_schema
    def put(self, request, product_id):
        input_serializer = ProductInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        product = create_use_cases().update.execute(
            product_id, **input_serializer.validated_data
        )
        return Response(ProductOutputSerializer(product).data)

    @delete_product_schema
    def delete(self, request, product_id):
        create_use_cases().delete.execute(product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
