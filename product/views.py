from django.http import JsonResponse, HttpResponseNotFound
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import Product, CartProduct, Order
from .serializers import ProductSerializer, CartSerializer, OrderSerializer
from rest_framework.decorators import api_view


# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@api_view(["GET", "POST"])
def ProductDetail(request, slug):
    try:
        try:
            product = Product.objects.get(slug=slug, published=True)
        except Exception as e:
            print(e)

        serializer = ProductSerializer(product)
        return JsonResponse({
            'data': serializer.data
        })
    except Exception as e:
        print(e)
        # raise Http404("Please contact administrator")
        return HttpResponseNotFound('<h1>Not found</h1>')


@api_view(["GET", "POST"])
def CheckCart(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_products = CartProduct.objects.filter(cart=cart)
    serializer = CartSerializer(cart, context={'request': request})
    return JsonResponse({
        'data': serializer.data
    })


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
    return JsonResponse({
        'data': serializer.data
    })


@api_view(["GET", "POST"])
def OrderDetail(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data)
