
import datetime
from django.core.management.base import BaseCommand
import services.dataset as dataset
from services.models import Salon, Employee
import pytz


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):
        day = datetime.datetime(2023, 5, 25, 0, 0, 1, 127325, tzinfo=pytz.UTC)
        salon = Salon.objects.filter(name='Beautiful Nails').first()
        master = Employee.objects.filter(name='Mario Dedivanovic').first()
        print(salon)
        tt = dataset.get_schedule(day, salon=salon, master=master)
        print(tt)

