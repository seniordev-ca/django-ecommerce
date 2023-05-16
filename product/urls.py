from django.urls import path

from .views import ProductViewSet, ProductDetail, CheckCart, OrderPlace, OrderDetail
from rest_framework import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, 'products_all')

urlpatterns = [
    path('products/<str:slug>/', ProductDetail, name="product_detail"),
    path('cart', CheckCart, name="check_cart"),
    path('order/place', OrderPlace, name="place_order"),
    path('order/<str:id>/', OrderDetail, name="check_order"),
] + router.urls
