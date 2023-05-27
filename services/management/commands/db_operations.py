
import datetime
from django.core.management.base import BaseCommand
import services.dataset as dataset
from services.models import Salon, Employee
import pytz


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        year, month, day = options['year'], options['month'], options['day']
        day = datetime.datetime(year, month, day, 0, 0, 0, tzinfo=pytz.UTC)
        salon = Salon.objects.filter(phone=options['salon_phone']).first()
        master = Employee.objects.filter(phone=options['master_phone']).first()
        print(salon, master, day)
        dataset.set_salon_schedule(day, salon=salon, employee=master)

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='?', type=int)
        parser.add_argument('month', nargs='?', type=int)
        parser.add_argument('day', nargs='?', type=int)
        parser.add_argument('salon_phone', nargs='?', type=str)
        parser.add_argument('master_phone', nargs='?', type=str)
