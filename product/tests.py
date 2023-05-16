from django.urls import reverse
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.contrib.auth.models import User
from product.models import Product, Order


class ProductsViewTests(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            title='Product 1', price=10.0, published=True)
        self.product2 = Product.objects.create(
            title='Product 2', price=20.0, published=True)
        self.product3 = Product.objects.create(
            title='Product 3', price=30.0, published=False)

    def test_products_view(self):
        url = reverse('products_all-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductDetailTests(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            title='Product 1', price=10.0, published=True)
        self.product2 = Product.objects.create(
            title='Product 2', price=20.0, published=True)
        self.product3 = Product.objects.create(
            title='Product 3', price=30.0, published=False)

    def test_product_detail(self):
        url = reverse('product_detail', args=[self.product1.slug])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


client = Client()


class OrderPlaceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.product1 = Product.objects.create(
            title='Test Product 1', description='Test Product 1 Description', price=10.99, published=True)
        self.product2 = Product.objects.create(
            title='Test Product 2', description='Test Product 2 Description', price=20.99, published=True)

    def test_order_place(self):
        data = {
            'shippingInfo': '123 Test Street',
            'cartItems': [
                {'id': self.product1.id, 'count': 2},
                {'id': self.product2.id, 'count': 1},
            ]
        }
        response = self.client.post(reverse('place_order'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, 42.97)
        self.assertEqual(order.ordered_products.count(), 2)
        self.assertEqual(order.ordered_products.all()[0].id, self.product1.id)
        self.assertEqual(order.ordered_products.all()[1].id, self.product2.id)
