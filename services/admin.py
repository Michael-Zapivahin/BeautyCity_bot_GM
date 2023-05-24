from django.contrib import admin
from .models import (
    Client,
    Employee,
    Procedure,
    Salon,
    Schedule,
    Payment
)


# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    pass


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    pass


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
