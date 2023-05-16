from django.urls import reverse
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from knox.models import AuthToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from product.models import Product, Cart, CartProduct, Order
from product.serializers import ProductSerializer, CartSerializer, OrderSerializer
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer


class RegisterAPITestCase(APITestCase):
    url = reverse('user_register')

    def test_register_api_success(self):
        data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'test_user')

    def test_register_api_failure(self):
        data = {
            'username': '',
            'email': 'test_user@example.com',
            'password': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)


class LoginAPITestCase(APITestCase):
    url = reverse('user_login')

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='test_password'
        )

    def test_login_api_success(self):
        data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_api_failure(self):
        data = {
            'username': 'test_user',
            'password': 'wrong_password',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)


class ChangePasswordAPITestCase(APITestCase):
    url = reverse('user_change_password')

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='test_password'
        )
        self.token = AuthToken.objects.create(self.user)[1]

    def test_change_password_api_success(self):
        data = {
            'oldPassword': 'test_password',
            'newPassword': 'new_password',
            'newPassword2': 'new_password',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.check_password('new_password'))

    def test_change_password_api_failure(self):
        data = {
            'oldPassword': 'wrong_password',
            'newPassword': 'new_password',
            'newPassword2': 'new_password',
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.user.check_password('new_password'))


class ApiOverviewTests(APITestCase):
    def test_api_overview(self):
        url = reverse('Overview')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), {
            "Products": "/products",
            "Single Product Detail": "/products/id/",
            "Check cart": "/cart"
        })


class ProductsViewTests(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            title='Product 1', price=10.0, published=True)
        self.product2 = Product.objects.create(
            title='Product 2', price=20.0, published=True)
        self.product3 = Product.objects.create(
            title='Product 3', price=30.0, published=False)

    def test_products_view(self):
        url = reverse('products_all')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProductSerializer(
            instance=[self.product1, self.product2], many=True).data
        self.assertListEqual(response.json(), expected_data)


class ProductDetailTests(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
            title='Product 1', price=10.0, published=True)
        self.product2 = Product.objects.create(
            title='Product 2', price=20.0, published=True)
        self.product3 = Product.objects.create(
            title='Product 3', price=30.0, published=False)

    def test_product_detail(self):
        url = reverse('product_detail', args=[self.product1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProductSerializer(instance=self.product1).data
        self.assertDictEqual(response.json(), expected_data)


client = Client()


class CheckCartTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.create(user=self.user)
        self.product = Product.objects.create(
            title='Test Product', description='Test Product Description', price=10.99, published=True)
        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_check_cart(self):
        response = self.client.get(reverse('check_cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['products'][0]['product'], self.product.id)


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
            'shipping_address': '123 Test Street',
            'products': [
                {'id': self.product1.id, 'quantity': 2},
                {'id': self.product2.id, 'quantity': 1},
            ]
        }
        response = self.client.post(reverse('place_order'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, 42.97)
        self.assertEqual(order.ordered_products.count(), 2)
        self.assertEqual(order.ordered_products.all()[0].id, self.product1.id)
        self.assertEqual(order.ordered_products.all()[1].id, self.product2.id)


class OrderDetailAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product1 = Product.objects.create(title='Product 1', price=10, published=True)
        self.product2 = Product.objects.create(title='Product 2', price=20, published=True)
        self.order = Order.objects.create(user=self.user, shipping_address='123 Main St', total_price=50)
        self.order.ordered_products.add(self.product1, through_defaults={'quantity': 2})
        self.order.ordered_products.add(self.product2, through_defaults={'quantity': 1})
        self.url = reverse('check_order', args=[self.order.id])

    def test_get_order_detail(self):
        """
        Test retrieving order detail
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['shipping_address'], self.order.shipping_address)
        self.assertEqual(response.data['total_price'], str(self.order.total_price))
        self.assertEqual(len(response.data['ordered_products']), 2)
        self.assertEqual(response.data['ordered_products'][0]['id'], self.product1.id)
        self.assertEqual(response.data['ordered_products'][0]['name'], self.product1.name)
        self.assertEqual(response.data['ordered_products'][0]['price'], str(self.product1.price))
        self.assertEqual(response.data['ordered_products'][1]['id'], self.product2.id)
        self.assertEqual(response.data['ordered_products'][1]['name'], self.product2.name)
        self.assertEqual(response.data['ordered_products'][1]['price'], str(self.product2.price))

    def test_get_order_detail_unauthenticated(self):
        """
        Test retrieving order detail without authentication
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_detail_not_found(self):
        """
        Test retrieving non-existent order detail
        """
        self.client.login(username='testuser', password='testpass123')
        url = reverse('check_order', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)