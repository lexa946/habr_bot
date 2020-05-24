import telebot
from telebot import types
import sqlite3
import config




def execute_sql(command):
    base = sqlite3.connect(config.DATABASE)
    cur = base.cursor()
    cur.execute(command)
    result = cur.fetchall()
    base.commit()
    cur.close()
    base.close()
    return result

def get_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Дай последний пост!!')
    return markup

def inline_markup(*args):
    '''
    :param args: передаем кортэж кортэжей типа ((текст, значение),(текст, значение))
    :return: клавиатуру с заданными кнопками
    '''

    keyboard = types.InlineKeyboardMarkup()
    for item in args:
        text, calldata = item
        callback_button = types.InlineKeyboardButton(text=text, callback_data=calldata)
        keyboard.add(callback_button)
    return keyboard

def anketa_get_user(message):
    id = message.chat.id
    command = f"SELECT * FROM anketa WHERE ID = {id}"
    user =  execute_sql(command)
    return user


def anketa_set_id(message):
    id = message.chat.id
    command = f'INSERT INTO anketa(id) VALUES ("{id}")'
    execute_sql(command)


def anketa_set_name(message):
    name = message.text
    command = f'UPDATE anketa SET name = "{name}" WHERE id = {message.chat.id}'
    execute_sql(command)


def anketa_set_cities(message):
    city = message.text.upper()
    if city in config.CITIES:
        command = f'UPDATE anketa SET city = "{city}" WHERE id = {message.chat.id}'
        execute_sql(command)
        return True
    else:
        return False


def anketa_set_age(message):
        if message.text.isdigit() and int(message.text) < 60:
            command = f'UPDATE anketa SET age = {message.text} WHERE id = {message.chat.id}'
            execute_sql(command)
            return True
        else:
            return False

