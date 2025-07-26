from rest_framework import serializers
from .models import ProductMast, StckMalin, StckDetail

# For reading/creating products
class ProductSerializer(serializers.ModelSerializer):
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