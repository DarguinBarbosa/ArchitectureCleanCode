from rest_framework import serializers

from products.infra.models import PRICE_DECIMAL_PLACES, PRICE_MAX_DIGITS


class ProductInputSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True, required=False, default="")
    price = serializers.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES
    )


class ProductOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    price = serializers.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, read_only=True
    )
