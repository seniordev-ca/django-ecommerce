from django.contrib import admin
from .models import Product, ProductImage, Order, OrderedProduct


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = (
        'title',
        'price',
        'created',
    )
    search_fields = (
        'title',
        'price'
    )


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'shipping_address', 'total_price', 'created']
    search_fields = ['order_number', 'user__username', 'shipping_address']
    list_filter = ['created']
    inlines = [OrderedProductInline]
