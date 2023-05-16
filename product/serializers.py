from .models import Product, ProductImage, Order, OrderedProduct
from rest_framework import serializers
from django.contrib.auth.models import User


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class OrderedProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderedProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    ordered_products = OrderedProductSerializer(many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'ordered_products', 'user', 'shipping_address', 'created', 'modified']
        read_only_fields = ['id', 'order_number', 'created', 'modified']
