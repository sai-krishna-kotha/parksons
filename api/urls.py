from django.urls import path
from .views import (
    ProductListCreateView,
    StockInView,
    StockOutView,
    StockLevelView,
    documentation_view,
    health_view,
)

urlpatterns = [
    path('docs/', documentation_view, name='api-documentation'),
    path('health/', health_view, name="site-health"),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('stock/in/', StockInView.as_view(), name='stock-in'),
    path('stock/out/', StockOutView.as_view(), name='stock-out'),
    path('stock/level/<str:gtin>/', StockLevelView.as_view(), name='stock-level'),
]