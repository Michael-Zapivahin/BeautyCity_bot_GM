from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    phone = models.CharField(max_length=12, verbose_name='Phone')

    def __str__(self):
        return f'{self.name}, phone: {self.phone}'


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


class Salon(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    phone = models.CharField(max_length=12, verbose_name='Phone')
    address = models.CharField(max_length=200, verbose_name='Address')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    photo = models.ImageField(max_length=200, verbose_name='Photo', blank=True, null=True)
    lat = models.FloatField(verbose_name='Lat')
    lng = models.FloatField(verbose_name='Lng')

    def __str__(self):
        return f'{self.name}, phone: {self.phone}'


class Schedule(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='schedules', verbose_name='Salon')
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name='schedules', verbose_name='Employee'
    )
    datetime = models.DateTimeField(verbose_name='Date time')
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, related_name='schedules', verbose_name='Client', blank=True, null=True
    )
    procedure = models.ForeignKey(
        Procedure, on_delete=models.SET_NULL, related_name='schedules', verbose_name='Procedure', blank=True, null=True
    )
    confirmation = models.BooleanField(verbose_name='Confirmation', default=False)

    def __str__(self):
        return f'{self.salon.name} dt: {self.datetime}'


class Payment(models.Model):
    order = models.ForeignKey(
        Schedule, on_delete=models.PROTECT, related_name='payments', verbose_name='Order'
    )
    debt = models.IntegerField(blank=True, null=True, verbose_name='Debt')
    payment = models.IntegerField(blank=True, null=True, verbose_name='Payment')
    tips = models.IntegerField(blank=True, null=True, verbose_name='Tips')

    def __str__(self):
        return f'{self.order.client} debt: {self.debt}'
