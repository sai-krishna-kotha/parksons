from rest_framework import serializers
from .models import ProductMast, StckMain, StckDetail
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
    def validate_gtin(self, value):
        """
        Check that the GTIN has a valid length of 8, 12, 13, or 14 digits.
        """
        # A set is used for slightly faster lookups.
        valid_lengths = {8, 12, 13, 14}
        if len(value) not in valid_lengths:
            raise serializers.ValidationError("Invalid GTIN. Length must be 8, 12, 13, or 14 digits.")
        
        # Also ensure the GTIN contains only digits.
        if not value.isdigit():
            raise serializers.ValidationError("Invalid GTIN. Must contain only numbers.")
            
        return value

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