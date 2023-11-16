from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    favorite_brands = models.ManyToManyField('Brand', related_name='followers', blank=True)
    interests = models.ManyToManyField('Interest', related_name='followers', blank=True)

    def __str__(self):
        return self.username

class Conversation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    history = models.TextField()

    def add_to_history(self, message):
        if not self.history:
            self.history = message
        else:
            self.history += f"\n{message}"
        self.save()

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Interest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ClothingItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=100)
    image_url = models.URLField()
    available_quantity = models.PositiveIntegerField()
    tags = models.ManyToManyField('Tag', related_name='items', blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
