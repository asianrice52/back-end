from django.core.management.base import BaseCommand
import telebot
from datetime import datetime
from myapp.models import Event

bot = telebot.TeleBot("6432652356:AAHk_zM_O6sSUp_75I7EIOlf0WqbRGOb94c")

new_event = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Этот бот предоставляет информацию о событиях.")


@bot.message_handler(commands=['events'])
def events(message):
    try:
        upcoming_events = Event.objects.all().order_by('date')[:5]
        if upcoming_events:
            for event in upcoming_events:
                bot.send_message(message.chat.id, f"{event.title}\n{event.description}\nДата: {event.date}\nМесто: {event.location}")
        else:
            bot.send_message(message.chat.id, "На данный момент нет предстоящих событий.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при получении событий: {e}")

@bot.message_handler(commands=['help'])
def help(message):
    command_list = [
        "/start - Начать взаимодействие с ботом",
        "/events - Показать предстоящие события",
        "/help - Показать список доступных команд",
        "/create_event - Создание ивента",
    ]
    bot.send_message(message.chat.id, "\n".join(command_list))


@bot.message_handler(commands=['create_event'])
def create_event(message):
    bot.send_message(message.chat.id, "Давайте создадим новое событие. Пожалуйста, введите название события:")
    global new_event
    new_event = Event()
    bot.register_next_step_handler(message, process_title_step)

def process_title_step(message):
    try:
        chat_id = message.chat.id
        title = message.text
        global new_event
        new_event = Event(title=title)

        bot.send_message(chat_id, f"Событие '{title}' успешно создано! Теперь введите описание события:")
        bot.register_next_step_handler(message, process_description_step)
        print(f"Event created: {new_event.title}, {new_event.description}, {new_event.date}, {new_event.location}")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

def process_description_step(message):
    try:
        chat_id = message.chat.id
        description = message.text
        new_event.description = description

        bot.send_message(chat_id, "Описание добавлено. Теперь введите дату события в формате 'гггг-мм-дд чч:мм':")
        bot.register_next_step_handler(message, process_date_step)
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

def process_date_step(message):
    try:
        chat_id = message.chat.id
        date_str = message.text
        new_event.date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

        bot.send_message(chat_id, "Дата добавлена. Теперь введите место проведения события:")
        bot.register_next_step_handler(message, process_location_step)
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

def process_location_step(message):
    try:
        global new_event
        chat_id = message.chat.id
        location = message.text
        new_event.location = location

        new_event.save()  # Сохраняем событие в базу данных

        bot.send_message(chat_id, "Место проведения добавлено. Событие успешно создано!")
        print(f"Ивент создан: {new_event.title}, {new_event.description}, {new_event.date}, {new_event.location}")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['delete_event'])
def delete_event(message):
    bot.send_message(message.chat.id, "Введите название события, которое вы хотите удалить:")
    bot.register_next_step_handler(message, process_delete_event_step)

def process_delete_event_step(message):
    try:
        chat_id = message.chat.id
        title_to_delete = message.text

        event_to_delete = Event.objects.filter(title=title_to_delete).first()

        if event_to_delete:
            event_to_delete.delete()
            bot.send_message(chat_id, f"Событие '{title_to_delete}' успешно удалено.")
        else:
            bot.send_message(chat_id, f"Событие с названием '{title_to_delete}' не найдено.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting bot...")
        bot.polling()
        print("Bot stopped")