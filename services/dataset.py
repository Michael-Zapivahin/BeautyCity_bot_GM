from services.models import Procedure, Employee, Salon, Schedule
from datetime import datetime, timedelta, date
from django.shortcuts import get_object_or_404


def get_day_times(day, interval):
    start = day.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=5)
    time_current = start
    day_times = []
    while time_current <= end:
        day_times.append(time_current)
        time_current += timedelta(minutes=interval)
    return day_times


def get_procedures():
    procedures = []
    for procedure in Procedure.objects.all():
        procedures.append(
            {
                'id': procedure.id,
                'name': procedure.name,
                'cost': procedure.cost,
                'time': procedure.time,
            }
        )
    return procedures


def get_employees():
    employees = []
    for employee in Employee.objects.all():
        employees.append(
            {
                'id': employee.id,
                'name': employee.name,
                'phone': employee.phone,
                'position': employee.position,
            }
        )
    return employees


def get_salons():
    salons = []
    for salon in Salon.objects.all():
        salons.append(
            {
                'id': salon.id,
                'name': salon.name,
                'phone': salon.phone,
                'address': salon.address,
            }
        )
    return salons


def get_schedule(day, salon=None, master=None, busy=False):
    start_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = day.replace(hour=23, minute=59, second=59, microsecond=0)
    schedules_query = Schedule.objects.filter(datetime__gte=start_time, datetime__lte=end_time, confirmation=busy)
    if salon:
        schedules_query = schedules_query.filter(salon=salon)
    if master:
        schedules_query = schedules_query.filter(employee=master)
    schedules = []
    for schedule in schedules_query:
        schedules.append(
            {
                'id': schedule.id,
                'salon': schedule.salon,
                'employee': schedule.employee,
                'datetime': schedule.datetime,
                'client': schedule.client,
                'procedure': schedule.procedure,
                'confirmation': schedule.confirmation,
            }
        )
    return schedules


def set_salon_schedule(salon, employee, day_times):
    for time in day_times:
        schedule, created = Schedule.objects.get_or_create(
            datetime=time,
            salon=salon,
            defaults={
                'employee': employee,
            }
        )


def set_schedule():
    day = datetime.today()
    day_times = get_day_times(day, 30)
    salon1 = get_object_or_404(Salon, pk=1)
    salon2 = get_object_or_404(Salon, pk=2)
    for index in range(2, 6, 1):
        employee = get_object_or_404(Employee, pk=index)
        if index % 2 == 0:
            set_salon_schedule(salon2, employee, day_times)
        else:
            set_salon_schedule(salon1, employee, day_times)


