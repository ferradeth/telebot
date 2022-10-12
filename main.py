import telebot
from telebot import types
import config
import requests

bot = telebot.TeleBot(config.token, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message, ):
    login = message.from_user.id
    data = {
        'login': login
    }
    requests.post(config.url+'/start', json=data)
    bot.send_message(message.from_user.id, "привет, рад тебя видеть <3")


@bot.message_handler(commands=['help'])
def help_txt(message):
    bot.send_message(message.from_user.id, "/start - начать работу \n /sub - подписаться на категорию \n /unsub - "
                                           "отписаться от категории \n /news - показать новости")


@bot.message_handler(commands=['news'])
def send_news(message):
    login = message.from_user.id
    url = config.url + "/news"

    data = {
        "login": login
    }

    sub_categories = requests.post(url, json=data)

    for category in sub_categories.json():
        req = requests.get(
            f'https://newsapi.org/v2/top-headlines?apiKey={config.news_key}&country=cn&pageSize=3&category={category["name"]}')
        for i in req.json()["articles"]:
            news_list = [[i["title"], i["publishedAt"], i["url"]]]
            print(news_list)
            for new in news_list:
                bot.send_message(message.from_user.id, f"{new[0]} {new[2]}")


@bot.message_handler(commands=['sub'])
def sub_news(message):
    cats = requests.post(config.url+'/sub/info')
    markup = types.ReplyKeyboardMarkup()
    if cats is not None:
        for category in cats.json():
            markup.add(types.KeyboardButton(f"{category['name']}"))
    bot.send_message(message.from_user.id, 'Выберете категорию для подписки: ', reply_markup=markup)
    bot.register_next_step_handler(message, add_sub)


def add_sub(message):
    login = message.from_user.id
    data = {
        "login": login,
        "category": message.text
    }

    result = requests.post(config.url+"/sub/sub", json=data)
    bot.send_message(message.from_user.id, result.json()['answer'])


@bot.message_handler(commands=['unsub'])
def unsub_cat(message):
    data = {
        "login": message.from_user.id
    }
    result = requests.post(config.url+"/unsub/cats", json=data)
    print(result.json())
    markup = types.ReplyKeyboardMarkup()
    if result is not None:
        for u_cat in result.json():
            markup.add(types.KeyboardButton(u_cat['name']))
    bot.send_message(message.from_user.id, 'От какой категории вы хотите отписаться? ', reply_markup=markup)
    bot.register_next_step_handler(message, del_sub)


def del_sub(message):
    data = {
        "login": message.from_user.id,
        "name":  message.text
    }
    result = requests.post(config.url + "/unsub/del", json=data)
    bot.send_message(message.from_user.id, result.json()['answer'])


bot.infinity_polling()
