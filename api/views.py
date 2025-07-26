from django.shortcuts import render
from django.db.models import Sum
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ProductMast, StckMain, StckDetail
from .serializers import (
    ProductSerializer,
    StockTransactionSerializer,
    StockLevelSerializer
)

def index_view(request):
    """Serves the main HTML page."""
    return render(request, 'index.html')

def documentation_view(request):
    """Serves the API documentation page."""
    return render(request, 'documentation.html')

def health_view(request):
    return render(request, 'health.html')

# --- Product Views ---
class ProductListCreateView(generics.ListCreateAPIView):
    """
    View to list all products or create a new one.
    GET: /api/products/
    POST: /api/products/
    """
    queryset = ProductMast.objects.all()
    serializer_class = ProductSerializer

# --- Helper function to get stock ---
def get_product_stock(gtin):
    stock_in = StckDetail.objects.filter(
        product__gtin=gtin, transaction__transaction_type='IN'
    ).aggregate(total=Sum('quantity'))['total'] or 0

    stock_out = StckDetail.objects.filter(
        product__gtin=gtin, transaction__transaction_type='OUT'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    return stock_in - stock_out

# --- Stock Transaction Views ---
class StockTransactionView(APIView):
    """
    Base class for handling stock transactions.
    """
    transaction_type = None # Must be 'IN' or 'OUT'

    def post(self, request, *args, **kwargs):
        serializer = StockTransactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items = serializer.validated_data['items']
        
        try:
            # This is the key: wrap all database operations in transaction.atomic()
            with transaction.atomic():
                malin_record = StckMain.objects.create(transaction_type=self.transaction_type)
                
                for item in items:
                    gtin = item['product_gtin']
                    quantity = item['quantity']
                    
                    # Using select_for_update() locks the row to prevent race conditions
                    product = ProductMast.objects.select_for_update().filter(gtin=gtin).first()
                    if not product:
                        # Raising an exception inside the atomic block triggers a rollback
                        raise ValueError(f"Product with GTIN {gtin} not found.")

                    if self.transaction_type == 'OUT':
                        current_stock = get_product_stock(gtin)
                        if current_stock < quantity:
                            # More descriptive error message!
                            raise ValueError(f"Not enough stock for '{product.product_name}' (GTIN: {gtin}). Available: {current_stock}, Requested: {quantity}")
                    
                    StckDetail.objects.create(
                        transaction=malin_record,
                        product=product,
                        quantity=quantity
                    )
            
            return Response({"message": "Transaction successful", "transaction_id": malin_record.id}, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            # The custom, user-friendly error message will be returned
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StockInView(StockTransactionView):
    """ Handle Stock IN. POST: /api/stock/in/ """
    transaction_type = 'IN'

class StockOutView(StockTransactionView):
    """ Handle Stock OUT. POST: /api/stock/out/ """
    transaction_type = 'OUT'

# --- Stock Level View ---
class StockLevelView(APIView):
    """
    Check current stock level for a product.
    GET: /api/stock/level/{gtin}/
    """
    def get(self, request, gtin, *args, **kwargs):
        product = ProductMast.objects.filter(gtin=gtin).first()
        if not product:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        current_stock = get_product_stock(gtin)

        serializer = StockLevelSerializer(data={
            'product_gtin': product.gtin,
            'product_name': product.product_name,
            'quantity': current_stock
        })
        serializer.is_valid() # It will always be valid
        return Response(serializer.data, status=status.HTTP_200_OK)