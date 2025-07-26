from django.db import models

class ProductMast(models.Model):
    gtin = models.CharField(max_length=14, unique=True, db_index=True)
    product_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} ({self.gtin})"

class StckMain(models.Model): # As per schema: "stores the transaction details"
    TRANSACTION_TYPES = [('IN', 'Stock In'), ('OUT', 'Stock Out')]
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID: {self.id} - {self.get_transaction_type_display()} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class StckDetail(models.Model): # As per schema: "stores the details of the products within each transaction"
    transaction = models.ForeignKey(StckMain, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductMast, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in Transaction {self.transaction.id}"