import json
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    price = models.FloatField()
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, null=True)

    # Generate random slugs
    def save(self, *args, **kwargs):
        global str
        if self.slug is None:
            slug = slugify(self.title)

            has_slug = Product.objects.filter(slug=slug).exists()
            count = 1
            while has_slug:
                count += 1
                slug = slugify(self.slug) + '-' + str(count)
                has_slug = Product.objects.filter(slug=slug).exists()
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, related_name='images', null=True)
    image = models.URLField()

    def __str__(self):
        return f"New Image"


class Order(models.Model):
    order_number = models.UUIDField(unique=True, editable=False)
    # ordered_products = models.ManyToManyField(Product, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(default=0)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4()
        super().save(*args, **kwargs)

    def set_shipping_address(self, address):
        self.shipping_address = json.dumps(address)

    def get_shipping_address(self):
        return json.loads(self.shipping_address)

    class Meta:
        ordering = ['-created']


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ordered_products')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product')
