from django.core.management.base import BaseCommand
from services.models import Employee, Salon, Schedule, Procedure
from django.shortcuts import get_object_or_404
from django.http import Http404
import calendar
import datetime
import telebot
from telebot import types
from telebot.types import LabeledPrice, ShippingOption
from dotenv import load_dotenv
import os

import services.dataset as dataset
from pytz import timezone
from django.utils.timezone import utc


load_dotenv()
RECORD_INF = {}
TG_TOKEN = os.environ['TG_BOT_TOKEN']
is_phone_handler_registered = False
is_name_registered = False
PAYMENTS_TOKEN = os.environ['PAYMENTS_TOKEN']
IMAGES_URL = os.environ['IMAGES_URL']


token = TG_TOKEN
provider_token = PAYMENTS_TOKEN
bot = telebot.TeleBot(token)


def get_order_info(record):
    sch_time = record['time'].split('__')
    schedule = Schedule.objects.filter(pk=sch_time[1]).first()
    return f'салон: {schedule.salon}, {schedule.datetime}, мастер: {schedule.employee.name}'


def get_procedure_info(record):
    print(record)
    procedure_id = record['procedure'].split('__')[1]
    procedure = Procedure.objects.filter(pk=procedure_id).first()
    return {'name': procedure.name, 'cost': procedure.cost}


def get_calendar(call_back, month=None):
    markup = types.InlineKeyboardMarkup(row_width=7)

    now = datetime.datetime.now()
    if month is None:
        month = now.month

    # Создаем кнопки для переключения месяцев
    prev_month_button = types.InlineKeyboardButton(text="◀️", callback_data=f'prev_month_{month}')
    next_month_button = types.InlineKeyboardButton(text="▶️", callback_data=f'next_month_{month}')
    markup.row(prev_month_button, next_month_button)

    # Создаем заголовок с названием месяца и годом
    month_year_text = calendar.month_name[month] + " " + str(now.year)
    header_button = types.InlineKeyboardButton(text=month_year_text, callback_data=f'month_{month}')
    markup.add(header_button)

    # Создаем кнопки для дней месяца
    days_in_month = calendar.monthrange(now.year, month)[1]
    day_buttons = []
    for day in range(1, days_in_month + 1):
        day_buttons.append(types.InlineKeyboardButton(text=str(day), callback_data=f'day__{day} {month_year_text}'))
    markup.add(*day_buttons)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data=call_back))
    return markup


def get_list_masters(start_line_num, call_back):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_line_num = int(start_line_num)
    masters = dataset.get_employees()[start_line_num:start_line_num + 10]
    master_buttons = []
    for index, master in enumerate(masters):
        master_buttons.append(types.InlineKeyboardButton(
            text=master["name"],
            callback_data=f'master__{master["id"]}')
        )
    markup.add(*master_buttons)
    prev_masters_button = types.InlineKeyboardButton(text="◀️", callback_data=f'prev_masters_{start_line_num - 10}')
    next_masters_button = types.InlineKeyboardButton(text="▶️", callback_data=f'next_masters_{start_line_num + 10}')
    markup.row(prev_masters_button, next_masters_button)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data=call_back))
    return markup


def get_list_salons(start_line_num: int, call_back):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_line_num = int(start_line_num)
    salons = dataset.get_salons()[start_line_num:start_line_num + 10]
    salon_buttons = []
    for index, salon in enumerate(salons):
        salon_buttons.append(types.InlineKeyboardButton(
            text=salon['name'],
            callback_data=f'salon__{salon["id"]}')
        )
    markup.add(*salon_buttons)
    prev_salons_button = types.InlineKeyboardButton(text="◀️", callback_data=f'prev_salons_{start_line_num - 10}')
    next_salons_button = types.InlineKeyboardButton(text="▶️", callback_data=f'next_salons_{start_line_num + 10}')
    markup.row(prev_salons_button, next_salons_button)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data=call_back))
    return markup


def get_list_procedures(start_line_num: int, call_back):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_line_num = int(start_line_num)
    procedures = dataset.get_procedures()[start_line_num:start_line_num + 10]
    procedure_buttons = []
    for index, procedure in enumerate(procedures):
        procedure_buttons.append(types.InlineKeyboardButton(
            text=procedure['name'],
            callback_data=f'procedure__{procedure["id"]}')
        )
    markup.add(*procedure_buttons)
    prev_procedures_button = types.InlineKeyboardButton(
        text="◀️",
        callback_data=f'prev_procedures_{start_line_num - 10}'
    )
    next_procedures_button = types.InlineKeyboardButton(
        text="▶️",
        callback_data=f'next_procedures_{start_line_num + 10}'
    )
    markup.row(prev_procedures_button, next_procedures_button)
    button_back = types.InlineKeyboardButton('Назад', callback_data=call_back)
    markup.row(button_back)
    return markup


def get_work_times(start_line_num, call_back):
    global RECORD_INF
    salon, master = None, None
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    day = today
    try:
        master_or_salon = RECORD_INF['inf_about_master_or_salon'].split('__')
        if len(master_or_salon) > 1 and master_or_salon[0] == 'master':
            master = get_object_or_404(Employee, pk=master_or_salon[1])
        elif len(master_or_salon) > 1 and master_or_salon[0] == 'salon':
            salon = get_object_or_404(Salon, pk=master_or_salon[1])

        date_id = RECORD_INF['day'].split('__')
        if len(date_id) > 1 and date_id[0] == 'day':
            day = datetime.datetime.strptime(date_id[1], '%d %B %Y')
            day = datetime.datetime(day.year, day.month, day.day, 0, 0, 1,  tzinfo=utc)
    except KeyError or Http404 or IndexError or ValueError:
        pass

    start_line_num = int(start_line_num)
    day_times = dataset.get_schedule(day, salon=salon, master=master)

    if len(day_times) > start_line_num + 12:
        day_times = day_times[start_line_num:start_line_num + 12]

    markup = types.InlineKeyboardMarkup(row_width=4)
    time_buttons = []
    for time in day_times:
        time_buttons.append(types.InlineKeyboardButton(
            text=time['datetime'].strftime("%H:%M"),
            callback_data=f'time__{time["id"]}')
        )
    if len(day_times) == 0:
        time_buttons.append(types.InlineKeyboardButton(
            text='нет времени',
            callback_data=f'time__0')
        )
    markup.add(*time_buttons)

    prev_procedures_button = types.InlineKeyboardButton(
        text="◀️",
        callback_data=f'prev_times_{start_line_num - 12}'
    )
    next_procedures_button = types.InlineKeyboardButton(
        text="▶️",
        callback_data=f'next_times_{start_line_num + 12}'
    )
    markup.row(prev_procedures_button, next_procedures_button)
    markup.row(types.InlineKeyboardButton('Назад', callback_data=call_back))
    return markup


def get_buttons_yes_no(phone_number):
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_yes = types.InlineKeyboardButton(text='Да', callback_data=f'yes_phone_{phone_number}')
    button_no = types.InlineKeyboardButton(text='Заново', callback_data=f'no_phone_{phone_number}')
    markup.add(button_yes, button_no)
    return markup


def replace_message(call, text, bot, markup):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


class BOT:
    def start(self):

        bot = telebot.TeleBot(TG_TOKEN)

        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            # Отправка стартового сообщения
            menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            button2 = types.KeyboardButton('Помощь')
            menu.add(button2)
            bot.send_message(
                message.chat.id,
                "Привет. это телеграм бот салонов красоты XXXX. Здесь вы можете записаться на прием, в удобное для вас место и время.",
                reply_markup=menu
            )
            keyword = types.InlineKeyboardMarkup()
            keyword.add(types.InlineKeyboardButton('Записаться', callback_data='record'))

            # Отправка сообщения с меню чтоб сразу было видно
            bot.send_message(message.chat.id, 'Хотите записаться?', reply_markup=keyword)


        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            if message.text == 'Помощь':
                bot.send_message(
                    message.chat.id,
                    'Если возникли проблемы с записью, или есть непонятные моменты, свяжитесь по телефону XXXX'
                )


        @bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            global RECORD_INF
            if call.data.startswith('start_payment_tips'):
                procedure = get_procedure_info(RECORD_INF)
                amount = int(procedure['cost'])
                tips = amount * 0.1
                RECORD_INF['amount'] = amount
                RECORD_INF['tips'] = tips
                price = []
                price.append(LabeledPrice(label=f'Услуги салона {procedure["name"]}', amount=amount*100))
                price.append(LabeledPrice(label=f'Чаевые ', amount=round(tips * 100)))
                bot.send_invoice(
                    call.message.chat.id,
                    'Оплата услуг салона',
                    'Вы можете оплатить услуги на месте!',
                    'HAPPY FRIDAYS COUPON',
                    provider_token,
                    'rub',
                    prices=price,
                    photo_url='',
                    photo_height=512,
                    photo_width=512,
                    photo_size=512,
                    is_flexible=False,
                    start_parameter='service-example')

            if call.data.startswith('start_payment_buy'):
                procedure = get_procedure_info(RECORD_INF)
                amount = int(procedure['cost'])
                RECORD_INF['amount'] = amount
                price = []
                price.append(LabeledPrice(label=f'Услуги салона {procedure["name"]}', amount=amount*100))
                bot.send_invoice(
                    call.message.chat.id,
                    'Оплата услуг салона',
                    'Вы можете оплатить услуги на месте!',
                    'HAPPY FRIDAYS COUPON',
                    provider_token,
                    'rub',
                    prices=price,
                    photo_url='',
                    photo_height=512,
                    photo_width=512,
                    photo_size=512,
                    is_flexible=False,
                    start_parameter='service-example')

            if call.data == 'record':
                RECORD_INF = {}
                keyboard = types.InlineKeyboardMarkup()
                button_master = types.InlineKeyboardButton(text='Выбрать мастера', callback_data='select_master')
                button_salon = types.InlineKeyboardButton(text='Выбор салона', callback_data='select_salon')
                keyboard.add(button_master, button_salon)
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id,
                    text='Супер, начнем запись!', reply_markup=keyboard
                )

            if call.data == 'select_master':
                call_back = 'record'
                markup = get_list_masters(0, call_back)
                text = 'Выберите мастера'
                replace_message(call, text, bot, markup)
            if call.data.startswith('next_masters'):
                call_back = 'record'
                markup = get_list_masters(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('prev_masters') and int(call.data.split('_')[2]) >= 0:
                call_back = 'record'
                markup = get_list_masters(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data == 'select_salon':
                call_back = 'record'
                markup = get_list_salons(0, call_back)
                text = 'Выберите салон'
                replace_message(call, text, bot, markup)
            if call.data.startswith('next_salons'):
                call_back = 'record'
                markup = get_list_salons(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('prev_salons') and int(call.data.split('_')[2]) >= 0:
                call_back = 'record'
                markup = get_list_salons(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data.startswith('salon') or call.data.startswith('master'):
                call_back = 'record'
                RECORD_INF['inf_about_master_or_salon'] = call.data
                markup = get_list_procedures(0, call_back)
                text = f'Выберите процеду'
                replace_message(call, text, bot, markup)
            if call.data.startswith('next_procedures'):
                call_back = 'record'
                markup = get_list_procedures(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('prev_procedures') and int(call.data.split('_')[2]) >= 0:
                call_back = 'record'
                markup = get_list_procedures(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data.startswith('procedure'):
                call_back = 'salon'
                markup = get_calendar(call_back)
                text = f'Выберите дату'
                replace_message(call, text, bot, markup)

            if call.data.startswith('prev_month'):
                call_back = 'salon'
                current_month = int(call.data.split('_')[2])
                prev_month = current_month - 1 if current_month > 1 else 12
                markup = get_calendar(call_back, prev_month)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('next_month'):
                call_back = 'salon'
                current_month = int(call.data.split('_')[2])
                next_month = current_month + 1 if current_month < 12 else 1
                markup = get_calendar(call_back, next_month)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data.startswith('day'):
                call_back = 'procedure'
                RECORD_INF['day'] = call.data
                markup = get_work_times(0, call_back)
                text = f'Выберите время'
                replace_message(call, text, bot, markup)

            if call.data.startswith('prev_times'):
                call_back = 'procedure'
                markup = get_work_times(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('next_times'):
                call_back = 'procedure'
                markup = get_work_times(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data.startswith('time'):
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton('Назад', callback_data='day'))
                RECORD_INF['time'] = call.data
                bot.send_message(
                    call.message.chat.id,
                    'Если все верно, напишите номер телефона, учтите, написав, вы соглашаетесь с обработкой персональных данных: \n Предоставляя свои персональные данные Покупатель даёт согласие на обработку, хранение и использование своих персональных данных на основании ФЗ № 152-ФЗ «О персональных данных» от 27.07.2006 г.',
                    reply_markup=markup
                )
                global is_phone_handler_registered
                if not is_phone_handler_registered:
                    bot.register_next_step_handler(call.message, process_phone_number)
                    is_phone_handler_registered = True
            if call.data.startswith('no_phone'):
                bot.send_message(call.message.chat.id, 'Повторите номер телефона')
                bot.register_next_step_handler(call.message, process_phone_number)

            if call.data.startswith('yes_phone'):
                call_back = 'time'
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton('Назад', callback_data=call_back))
                RECORD_INF['phone_number'] = call.data.split('_')[2]
                bot.send_message(call.message.chat.id, 'Как к вам обращаться?', reply_markup=markup)
                global is_name_registered
                if not is_name_registered:
                    bot.register_next_step_handler(call.message, process_name)
                    is_name_registered = True



        def process_phone_number(message):
            phone_number = message.text
            bot.send_message(message.chat.id, f"Ваш номер телефона: {phone_number}")
            markup = get_buttons_yes_no(phone_number)
            bot.send_message(message.chat.id, "Верно?", reply_markup=markup)
            global is_phone_handler_registered
            is_phone_handler_registered = False

        def process_name(message):
            dataset.make_order(RECORD_INF)
            name = message.text
            RECORD_INF['client_name'] = name
            bot.send_message(message.chat.id, f"Приятно познакомиться, {name}")
            markup = types.InlineKeyboardMarkup()
            button_pyment = types.InlineKeyboardButton(text='Оплатить', callback_data='start_payment_buy')
            button_tips = types.InlineKeyboardButton(text='Оплатить с чаевыми (10%)',
                                                     callback_data='start_payment_tips')
            markup.row(button_pyment, button_tips)
            bot.send_message(message.chat.id, f"Ваша запись {get_order_info(RECORD_INF)} \n до встречи", reply_markup=markup)
            global is_name_registered
            is_name_registered = False


        # start payment block

        @bot.shipping_query_handler(func=lambda query: True)
        def shipping(shipping_query):
            pass

        @bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                          error_message="Произошла ошибка при оплате, попробуйте еще раз.")

        @bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            global RECORD_INF
            dataset.set_payment(record=RECORD_INF)
            bot.send_message(message.chat.id,
                             'Срасибо за платеж! Мы будем рады видеть вас в нашем салоне! '.format(
                                 message.successful_payment.total_amount / 100, message.successful_payment.currency),
                             parse_mode='Markdown')

        # end payment block

        bot.polling()


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        p = BOT
        p.start(self)
        pass
