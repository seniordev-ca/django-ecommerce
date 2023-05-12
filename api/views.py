from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from product.models import Product, Category, Cart, CartProduct, Order
from product.serializers import ProductSerializer, CartSerializer, OrderSerializer

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LogoutView
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Register API
@api_view(["GET", "POST"])
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Login API
@api_view(["GET", "POST"])
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Change Password API
@api_view(["GET", "POST"])
class ChangePasswordAPI(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    @method_decorator(login_required(login_url='/login'))
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordAPI, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        u = get_user_model().objects.get(username=user['username'])
        u.set_password(user['newPassword'])
        u.save()

        return Response("Successfully changed password.")


# Logout
@api_view(["GET", "POST"])
class LogoutAPI(LogoutView):
    permission_classes = [permissions.IsAuthenticated]


# Get User API
@api_view(["GET", "POST"])
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@api_view(['GET', 'POST'])
def ApiOverview(request):
    api_urls = {
        "Products": "/products",
        "Single Product Detail": "/products/id/",
        "Check cart": "/cart",
    }
    return JsonResponse(api_urls)


@api_view(["GET", "POST"])
def ProductsView(request):
    products = Product.objects.filter(published=True)
    serializers = ProductSerializer(products, many=True)
    return Response(serializers.data)


@api_view(["GET", "POST"])
def ProductDetail(request, id):
    product = Product.objects.get(id=id, published=True)
    serializers = ProductSerializer(product, many=False)
    return Response(serializers.data)


@api_view(["GET", "POST"])
def CheckCart(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_products = CartProduct.objects.filter(cart=cart)
    serializer = CartSerializer(cart, context={'request': request})
    return Response(serializer.data)


@api_view(["GET", "POST"])
def OrderPlace(request):
    # Get user and shipping address from request
    user = request.user
    shipping_address = request.data.get('shipping_address')

    # Get product IDs and quantities from request
    products_data = request.data.get('products')
    product_ids = [item['id'] for item in products_data]
    quantities = [item['quantity'] for item in products_data]

    # Get products and calculate total price
    products = []
    total_price = 0
    for i in range(len(product_ids)):
        product = get_object_or_404(Product, id=product_ids[i])
        products.append(product)
        total_price += product.price * quantities[i]

    # Create order
    order = Order(user=user, shipping_address=shipping_address, total_price=total_price)
    order.save()

    # Add ordered products to order
    for i in range(len(products)):
        order.ordered_products.add(products[i], through_defaults={'quantity': quantities[i]})

    # Serialize order data and return response
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def OrderDetail(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data)
