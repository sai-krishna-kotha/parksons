from django.contrib import admin

# Register your models here.
from .models import ProductMast, StckDetail, StckMain

class StckDetailInline(admin.TabularInline):
    model = StckDetail
    extra = 0

class ProductMastAdmin(admin.ModelAdmin):
    list_display = ('gtin', 'product_name')
    search_fields = ('gtin', 'product_name')

class StckMainAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    inlines = [StckDetailInline]

class StckDetailAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'product_name', 'product_gtin', 'quantity')
    
    def product_name(self, obj):
        return obj.product.product_name
    
    def product_gtin(self, obj):
        return obj.product.gtin

admin.site.register(ProductMast, ProductMastAdmin)
admin.site.register(StckDetail, StckDetailAdmin)
admin.site.register(StckMain, StckMainAdmin)
