from django.db import models
from django.db.models import fields
from .models import Product, Category, CartProduct, Cart, Order
from rest_framework import serializers
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class CartProductSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = CartProduct
        fields = ('product', 'quantity')


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    cart_products = CartProductSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'cart_products', 'created', 'modified')


class OrderSerializer(serializers.ModelSerializer):
    ordered_products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'ordered_products', 'user', 'shipping_address', 'created', 'modified']
        read_only_fields = ['id', 'order_number', 'created', 'modified']
