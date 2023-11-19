from django.core.management.base import BaseCommand
import telebot
from myapp.models import Product


bot = telebot.TeleBot("6590418109:AAGqhT1_IXFxDtB4elySaUGfdeDDkYwxbXk")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello world!")

@bot.message_handler(commands=['products'])
def products(message):
    products = Product.objects.all()
    for product in products:
        bot.send_message(message.chat.id, f"{product.name}: {product.price}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Available commands:\n/products - List all products\n/add <product_name> <product_price> - Add a new product")


@bot.message_handler(commands=['add'])
def add_product(message):
    try:
        _, product_name, product_price = message.text.split(' ', 2)

        Product.objects.create(name=product_name, price=float(product_price))

        bot.send_message(message.chat.id, f"Product {product_name} added successfully.")

    except ValueError:
        bot.send_message(message.chat.id, "Invalid command format. Use /add <product_name> <product_price>.")
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting bot...")
        bot.polling()
        print("Bot stopped")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

