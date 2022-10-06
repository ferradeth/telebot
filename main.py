import telebot
from telebot import types
import config
import requests
import sqlite3

connect = sqlite3.connect('mydb.db', check_same_thread=False)

cursor = connect.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS "users"(id INTEGER PRIMARY KEY, login TEXT NOT NULL); ''')
cursor.execute('''CREATE TABLE IF NOT EXISTS "categories"(id INTEGER PRIMARY KEY, name TEXT NOT NULL); ''')
cursor.execute('''CREATE TABLE IF NOT EXISTS "subs"(user_id INTEGER NOT NULL, category_id INTEGER NOT NULL); ''')

connect.commit()

bot = telebot.TeleBot(config.token, parse_mode=None)

if len(cursor.execute('SELECT id, name FROM categories').fetchall()) < len(config.categories):
    for cat in config.categories:
        cursor.execute('INSERT INTO "categories"(name) VALUES (?)', (cat,))
        connect.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message, ):
    login = message.from_user.id
    data = {
        'login': login
    }
    requests.post(config.url+'/start', json=data)
    bot.send_message(message.from_user.id, "привет, рад тебя видеть <3")
    # login = message.from_user.id
    # print(login)
    # if login != '':
    #     result = cursor.execute('SELECT login FROM users WHERE login=?', (login,)).fetchone()
    #     if result is None:
    #         cursor.execute('INSERT INTO "users"(login) VALUES (?)', (login,))
    #         connect.commit()


@bot.message_handler(commands=['help'])
def help_txt(message):
    bot.send_message(message.from_user.id, "/start - начать работу \n /sub - подписаться на категорию \n мои подписки "
                                           "- посмотреть подписки \n /unsub - отписаться от категории \n /news - "
                                           "показать новости")


@bot.message_handler(commands=['news'])
def send_news(message):
    signup = cursor.execute('SELECT id FROM users WHERE login=?', (message.from_user.id,)).fetchone()
    user_cats = cursor.execute('SELECT category_id FROM subs WHERE user_id=?', (signup[0],)).fetchall()
    if user_cats is not None:
        for u_cat in user_cats:
            category = cursor.execute('SELECT name FROM categories WHERE id=?', (u_cat[0],)).fetchone()
            a = requests.get(f'https://newsapi.org/v2/top-headlines?apiKey={config.news_key}&country=ru&pageSize=2'
                             f'&category={category[0]}')
            for i in a.json()['articles']:
                news = [[i['title'], i['publishedAt'], i['url']]]
                for new in news:
                    bot.send_message(message.from_user.id, f" {new[0]} {new[2]}")


@bot.message_handler(commands=['sub'])
def sub_news(message):
    cats = requests.post(config.url+'/sub/info')
    print(cats)
    markup = types.ReplyKeyboardMarkup()
    if cats is not None:
        for category in cats:
            markup.add(types.KeyboardButton(category[1]))
    bot.send_message(message.from_user.id, 'Выберете категорию для подписки: ', reply_markup=markup)
    bot.register_next_step_handler(message, add_sub)


def add_sub(message):
    result = cursor.execute('SELECT id FROM categories WHERE name=?', (message.text,)).fetchone()
    if result is not None:
        signup = cursor.execute('SELECT id FROM users WHERE login=?', (message.from_user.id,)).fetchone()
        check_ex = cursor.execute('SELECT * FROM subs WHERE user_id=? AND category_id=?', (message.from_user.id, result[0])).fetchone()
        if check_ex is None:
            cursor.execute('INSERT INTO subs(user_id, category_id) VALUES (?, ?)', (signup[0], result[0]))
            bot.send_message(message.from_user.id, 'Вы успешно подписались на категорию')
            connect.commit()
        else:
            bot.send_message(message.from_user.id, 'Вы уже подписаны на эту категорию')
    else:
        bot.send_message(message.from_user.id,'Проверьте корректность ввода, возможно такой категории не существует')


@bot.message_handler(commands=['unsub'])
def unsub_cat(message):
    signup = cursor.execute('SELECT id FROM users WHERE login=?', (message.from_user.id,)).fetchone()
    user_cats = cursor.execute('SELECT category_id FROM subs WHERE user_id=?', (signup[0],)).fetchall()
    markup = types.ReplyKeyboardMarkup()
    if user_cats is not None:
        for u_cat in user_cats:
            category = cursor.execute('SELECT name FROM categories WHERE id=?', (u_cat[0],)).fetchone()
            markup.add(types.KeyboardButton(category[0]))
    bot.send_message(message.from_user.id, 'От какой категории вы хотите отписаться? ', reply_markup=markup)
    bot.register_next_step_handler(message, del_sub)


def del_sub(message):
    signup = cursor.execute('SELECT id FROM users WHERE login=?', (message.from_user.id,)).fetchone()
    result = cursor.execute('SELECT id FROM categories WHERE name=?', (message.text,)).fetchone()
    if result is not None:
        cursor.execute('DELETE FROM subs WHERE category_id=? AND user_id=?', (result[0], signup[0]))
        bot.send_message(message.from_user.id, 'Вы успешно отписались от категории')
        connect.commit()
    else:
        bot.send_message(message.from_user.id, 'Введите корректное название категории')


@bot.message_handler(func=lambda m: True)
def say_smt(message):
    if message.text == 'лох':
        bot.send_message(message.from_user.id, 'наелся блох сел на лавочку и сдох')
    elif message.text == 'расскажи шутку':
        bot.send_message(message.from_user.id,
                         'Штирлиц упал с четырнадцатого этажа. Так широко раскидывать мозгами ему еще не приходилось.')
    elif message.text == 'мои подписки':
        signup = cursor.execute('SELECT id FROM users WHERE login=?', (message.from_user.id,)).fetchone()
        user_cats = cursor.execute('SELECT category_id FROM subs WHERE user_id=?', (signup[0],)).fetchall()
        if user_cats is not None:
            for u_cat in user_cats:
                bot.send_message(message.from_user.id,
                                 cursor.execute('SELECT name FROM categories WHERE id=?', (u_cat[0],)).fetchone()[0])


bot.infinity_polling()
