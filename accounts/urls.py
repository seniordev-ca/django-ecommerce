from django.urls import path
from rest_framework import routers
from .views import LoginAPI, RegisterAPI, ChangePasswordAPI, LogoutAPI

router = routers.DefaultRouter()

urlpatterns = [
    path('users/login', LoginAPI, name="user_login"),
    path('users/register', RegisterAPI, name="user_register"),
    path('users/change-password', ChangePasswordAPI, name="user_change_password"),
    path('users/logout/', LogoutAPI, name='user_logout'),
] + router.urls
