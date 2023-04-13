import requests
from bs4 import BeautifulSoup
import logging
import telegram
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import configparser

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('telegram', 'token')


async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Помощь", callback_data='help')],
        [InlineKeyboardButton("Погода", callback_data='weather'), InlineKeyboardButton("Шутка", callback_data='joke')],
        [InlineKeyboardButton("Новости", callback_data='news')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет, юзер, я бот созданный чтобы делать вещи! Выбери одну из команд или нажми Помощь для получения списка доступных команд.", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data

    if callback_data == 'help':
        await help(update, context)
    elif callback_data == 'weather':
        await weather(update, context)
    elif callback_data == 'joke':
        await joke(update, context)
    elif callback_data == 'news':
        await news(update, context)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def news(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://newsapi.org/v2/top-headlines?country=ru&apiKey=2a053dea4c194ad7b17dc564bbca6510'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'ok':
        articles = data['articles']
        for article in articles:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=article['title'])
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка при получении новостей')


async def joke(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist&format=txt'
    response = requests.get(url)
    if response.status_code == 200:
        joke = response.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text=joke)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка при получении шутки')


async def weather(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    city = ' '.join(context.args)
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=8ee6245fbd400c86b866bb08409fcdae&units=metric'
    response = requests.get(url.format(city))
    data = response.json()

    if data['cod'] == 200:
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        await context.bot.send_message(chat_id=update.effective_chat.id, text=('Температура в городе {} сейчас: {}°C, {}'.format(city, temperature, description)))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка при получении погоды')


async def help(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='- `/start` - приветствие пользователя и вывод меню- `/help` - вывод списка доступных команд- `/echo <текст>` - эхо-ответ с переданным текстом- `/weather <город>` - вывод текущей погоды в указанном городе - `/news` - вывод последних новостей - `/joke` - вывод случайной шутки - `/stop` - прощание с пользователем и остановка работы бота')


async def stop(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Увидимся!")
    await application.stop()


async def unknown(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Я не знаю такой команды!")


if __name__ == '__main__':

    application = ApplicationBuilder().token('6238496236:AAFWzWyATpKFDJHeDtUXO_rztC6YJaCZNpg').build()

    start_handler = CommandHandler('start', start)

    echo_handler = CommandHandler('echo', echo)

    news_handler = CommandHandler('news', news)

    weather_handler = CommandHandler('weather', weather)

    joke_handler = CommandHandler('joke', joke)

    help_handler = CommandHandler('help', help)

    button_handler = CallbackQueryHandler(button)

    stop_handler = CommandHandler('stop', stop)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(news_handler)
    application.add_handler(weather_handler)
    application.add_handler(joke_handler)
    application.add_handler(help_handler)
    application.add_handler(button_handler)
    application.add_handler(stop_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
