from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from product.models import Product, Cart, CartProduct, Order
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
    return JsonResponse({
        'data': serializers.data
    })
