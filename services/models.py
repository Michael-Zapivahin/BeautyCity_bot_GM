from django.db import models
# from tinymce.models import HTMLField


class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    phone = models.CharField(max_length=12, verbose_name='Phone')

    def __str__(self):
        return f'{self.Name}, phone: {self.phone}'


class Employee(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    phone = models.CharField(max_length=12, verbose_name='Phone')
    photo = models.ImageField(max_length=200, verbose_name='Photo', blank=True, null=True)
    position = models.CharField(max_length=200, verbose_name='Position')

    def __str__(self):
        return f'{self.name} pos: {self.position} ph: {self.phone}'


class Procedure(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    cost = models.IntegerField(verbose_name='Cost')
    time = models.IntegerField(verbose_name='Time in minutes', blank=True, null=True)

    def __str__(self):
        return self.name

