from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    title = models.TextField()


class Product(models.Model):
    title = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()
    price = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
