from email.policy import default
from django.db import models
from django.core.validators import MaxValueValidator ,MinValueValidator
import os
# Create your models here.
class Identite(models.Model):   
    name = models.fields.CharField(max_length=100)
    email = models.fields.EmailField()
    tel = models.fields.IntegerField()
    detail = models.fields.CharField(max_length=1000,default=" ")
    image1 = models.ImageField(upload_to='images',default=None)
    image2 = models.ImageField(upload_to='images',default=None)
    image3 = models.ImageField(upload_to='images',default=None)
    # image4 = models.ImageField(upload_to='images',default=None)
    # image5 = models.ImageField(upload_to='images',default=None)
    # image6 = models.ImageField(upload_to='images',default=None)
    address = models.fields.CharField(max_length=100)
    ##pour representer chaque band par son nom
    def __str__(self) -> str:
        return f'{self.name}'
class Images(models.Model):   
    image = models.ImageField(upload_to='image')
    def __str__(self) -> str:
        return f'{self.image}'