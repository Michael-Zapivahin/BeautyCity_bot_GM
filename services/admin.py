from django.contrib import admin
from .models import Client, Employee, Procedure


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