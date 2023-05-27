from django.core.management.base import BaseCommand
from services.models import Employee, Salon
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
prices = [LabeledPrice(label='Working Time Machine', amount=5750), LabeledPrice('Gift wrapping', 500)]
shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 300))]


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
    markup.row(types.InlineKeyboardButton('Назад', callback_data=call_back))
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

        # start payment block

        @bot.message_handler(commands=['start_payment'])
        def command_start(message):
            bot.send_message(message.chat.id,
                             "Hello, I'm the demo merchant bot."
                             " I can sell you a Time Machine."
                             " Use /buy to order one, /terms for Terms and Conditions")

        @bot.message_handler(commands=['terms'])
        def command_terms(message):
            bot.send_message(message.chat.id,
                             'Thank you for shopping with our demo bot. We hope you like your new time machine!\n'
                             '1. If your time machine was not delivered on time, please rethink your concept of time and try again.\n'
                             '2. If you find that your time machine is not working, kindly contact our future service workshops on Trappist-1e.'
                             ' They will be accessible anywhere between May 2075 and November 4000 C.E.\n'
                             '3. If you would like a refund, kindly apply for one yesterday and we will have sent it to you immediately.')

        @bot.message_handler(commands=['buy'])
        def command_pay(message):
            bot.send_message(message.chat.id,
                             "Real cards won't work with me, no money will be debited from your account."
                             " Use this test card number to pay for your Time Machine: `4242 4242 4242 4242`"
                             "\n\nThis is your demo invoice:", parse_mode='Markdown')
            bot.send_invoice(
                message.chat.id,  # chat_id
                'Working Time Machine',  # title
                ' Want to visit your great-great-great-grandparents? Make a fortune at the races? Shake hands with Hammurabi and take a stroll in the Hanging Gardens? Order our Working Time Machine today!',
                # description
                'HAPPY FRIDAYS COUPON',  # invoice_payload
                provider_token,  # provider_token
                'usd',  # currency
                prices,  # prices
                photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                photo_height=512,  # !=0/None or picture won't be shown
                photo_width=512,
                photo_size=512,
                is_flexible=False,  # True If you need to set up Shipping Fee
                start_parameter='time-machine-example')

        @bot.shipping_query_handler(func=lambda query: True)
        def shipping(shipping_query):
            print(shipping_query)
            bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                                      error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')

        @bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                          error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                        " try to pay again in a few minutes, we need a small rest.")

        @bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            bot.send_message(message.chat.id,
                             'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                             'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                                 message.successful_payment.total_amount / 100, message.successful_payment.currency),
                             parse_mode='Markdown')

        # end payment block

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

            if call.data == 'record':
                global RECORD_INF
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
                RECORD_INF['procedure'] = call.data
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

            if call.data.startswith('payment'):
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton('Back', callback_data='time'))
                bot.send_message(
                    call.message.chat.id,
                    'payment start',
                    reply_markup=markup
                )

            if call.data.startswith('time'):
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton('Назад', callback_data='day'))
                markup.row(types.InlineKeyboardButton('Payment', callback_data='payment'))
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
            name = message.text
            bot.send_message(message.chat.id, f"Приятно познакомиться, {name}")
            bot.send_message(message.chat.id, f"Ваша запись {RECORD_INF} \n до встречи")
            global is_name_registered
            is_name_registered = False

        bot.polling()


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        p = BOT
        p.start(self)
        pass
