from django.core.management.base import BaseCommand
import calendar
import datetime
import telebot
from telebot import types
from dotenv import load_dotenv
import os

import services.dataset as dataset

load_dotenv()
RECORD_INF = {}
TG_TOKEN = os.environ['TG_BOT_TOKEN']
is_phone_handler_registered = False
is_name_registered = False


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


def get_list_of_times(start_line_num, call_back):
    markup = types.InlineKeyboardMarkup(row_width=4)
    start_line_num = int(start_line_num)
    times = [
                '9:00',
            ][start_line_num:start_line_num + 12]
    time_buttons = []
    for time in times:
        time_buttons.append(types.InlineKeyboardButton(text=time, callback_data=f'time_{time}'))
    markup.add(*time_buttons)
    # Создаем кнопки для переключения месяцев
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
                text = f'{RECORD_INF} \n Выберите процеду'
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
                text = f'{RECORD_INF} \n Выберите дату'
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
                markup = get_list_of_times(0, call_back)
                text = f'{RECORD_INF} \n Выберите время'
                replace_message(call, text, bot, markup)
            if call.data.startswith('prev_times'):
                call_back = 'procedure'
                markup = get_list_of_times(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            if call.data.startswith('next_times'):
                call_back = 'procedure'
                markup = get_list_of_times(call.data.split('_')[2], call_back)
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )

            if call.data.startswith('time'):  # ВОТ ЗДЕСЬ СОГЛАШЕНИЕ
                call_back = 'day'
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton('Назад', callback_data=call_back))
                RECORD_INF['time'] = call.data
                text = f'{RECORD_INF}'
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
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
