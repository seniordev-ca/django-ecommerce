from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


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


admin.site.register(Product, ProductAdmin)
