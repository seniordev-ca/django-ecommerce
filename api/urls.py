from django import urls
from django.urls import path
from .views import *


urlpatterns = [
    path('', ApiOverview, name="Overview"),
    path('users/login', LoginAPI, name="user_login"),
    path('users/register', RegisterAPI, name="user_register"),
    path('users/change-password', ChangePasswordAPI, name="user_change_password"),
    path('users/logout/', LogoutAPI, name='user_logout'),
    path('products', ProductsView, name="products_all"),
    path('products/<str:id>/', ProductDetail, name="product_detail"),
    path('cart', CheckCart, name="check_cart"),
    path('order/place', OrderPlace, name="place_order"),
    path('order/<str:id>/', OrderDetail, name="check_order"),
]
