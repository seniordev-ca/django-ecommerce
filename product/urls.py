from django.urls import path

from .views import ProductViewSet, ProductDetail, OrderPlace
from rest_framework import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, 'products_all')

urlpatterns = [
    path('products/<str:slug>/', ProductDetail, name="product_detail"),
    path('order/place', OrderPlace, name="place_order"),
] + router.urls
