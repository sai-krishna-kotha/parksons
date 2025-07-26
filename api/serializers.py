from rest_framework import serializers
from .models import ProductMast, StckMalin, StckDetail
from rest_framework.validators import UniqueValidator

# For reading/creating products
class ProductSerializer(serializers.ModelSerializer):
    # This validator ensures the GTIN is unique across all ProductMast instances.
    gtin = serializers.CharField(
        max_length=14,
        validators=[UniqueValidator(
            queryset=ProductMast.objects.all(),
            message="A product with this GTIN already exists."
        )]
    )
    class Meta:
        model = ProductMast
        fields = ['id', 'gtin', 'product_name', 'description']

# For representing one item in a transaction request
class StockTransactionItemSerializer(serializers.Serializer):
    product_gtin = serializers.CharField(max_length=14)
    quantity = serializers.IntegerField(min_value=1)

# For the overall transaction request body
class StockTransactionSerializer(serializers.Serializer):
    items = StockTransactionItemSerializer(many=True)

# For representing the final stock level
class StockLevelSerializer(serializers.Serializer):
    product_gtin = serializers.CharField(max_length=14)
    product_name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField()