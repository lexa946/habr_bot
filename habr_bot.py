import telebot
from telebot import apihelper
import config
import habr_parser
import habr_bot_logic
import time

TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)
telebot.apihelper.proxy = {'https': 'socks5h://508519294:ekCx3RuA@grsst.s5.opennetwork.cc:999'}

markup_start = habr_bot_logic.inline_markup(('Зарегестрироваться', 'new_user'))
default_markup = habr_bot_logic.inline_markup( ('Удалить анкету', 'del'))






@bot.message_handler(func=lambda message: True, commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать.\nВы можете заполнить анкету.', reply_markup=markup_start)



@bot.message_handler(func=lambda message: True, commands=['refresh'])
def refresh(message):
    if message.chat.id in config.ADMINS:
        last_post = habr_parser.last_in_base()
        new_posts = habr_parser.get_new_posts(last_post)
        for post in new_posts:
            title, link = post
            post = f'[{title}]({link})'
            bot.send_message(config.CHANNEL_NAME, post, parse_mode='Markdown')
            time.sleep(3)
        habr_parser.write_in_base(new_posts)
        bot.send_message(message.chat.id, f'обновлено - {len(new_posts)}')

    else:
        bot.send_message('Вы не админ!')




################REGISTRACI9##########################
@bot.message_handler(func=lambda message:not habr_bot_logic.anketa_get_user(message))
def send_default(message):
    bot.send_message(message.chat.id, 'Сначала зарегайся', reply_markup=markup_start)


@bot.message_handler(func=lambda message: config.States.S_ENTER_NAME == habr_bot_logic.execute_sql(f'SELECT * FROM anketa WHERE ID = {message.chat.id}')[0][4])
def set_name(message):
    habr_bot_logic.anketa_set_name(message)
    command = f'UPDATE anketa SET state = 2 WHERE id = {message.chat.id}'
    habr_bot_logic.execute_sql(command)
    bot.send_message(message.chat.id, 'Имя заполнил, а из какого ты города?')


@bot.message_handler(func=lambda message: config.States.S_ENTER_CITY == habr_bot_logic.execute_sql(f'SELECT * FROM anketa WHERE ID = {message.chat.id}')[0][4])
def set_city(message):

    flag = habr_bot_logic.anketa_set_cities(message)
    if not flag:
        bot.send_message(message.chat.id, 'Такого города не существует!')
        return
    else:
        command = f'UPDATE anketa SET state = 3 WHERE id = {message.chat.id}'
        habr_bot_logic.execute_sql(command)
        bot.send_message(message.chat.id, 'А лет сколько тебе?')


@bot.message_handler(func=lambda message: config.States.S_ENTER_AGE == habr_bot_logic.execute_sql(f'SELECT * FROM anketa WHERE ID = {message.chat.id}')[0][4])
def set_age(message):
    flag = habr_bot_logic.anketa_set_age(message)
    if not flag:
        bot.send_message(message.chat.id, 'Неверный возраст')
        return
    else:
        command = f'UPDATE anketa SET state = 4 WHERE id = {message.chat.id}'
        habr_bot_logic.execute_sql(command)
        bot.send_message(message.chat.id, 'Регистрация завершена - спасибо!', reply_markup=default_markup)
#####################################################


@bot.callback_query_handler(func=lambda call: call.data == 'new_user')
def new_user(call):
    user = habr_bot_logic.anketa_get_user(call.message)
    if user:
        bot.send_message(call.message.chat.id, 'Вы уже зарегестрированы!')
    else:
        bot.send_message(call.message.chat.id, 'Введите своё имя:')
        habr_bot_logic.anketa_set_id(call.message)
        command = f'UPDATE anketa SET state = 1 WHERE id = {call.message.chat.id}'
        habr_bot_logic.execute_sql(command)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        # if call.data == 'new_user':
        #     user = habr_bot_logic.anketa_get_user(call.message)
        #     if user:
        #         bot.send_message(call.message.chat.id, 'Вы уже зарегестрированы!')
        #     else:
        #         bot.send_message(call.message.chat.id, 'Введите своё имя:')
        #         habr_bot_logic.anketa_set_id(call.message)
        #         command = f'UPDATE anketa SET state = 1 WHERE id = {call.message.chat.id}'
        #         habr_bot_logic.execute_sql(command)

        if call.data == 'redactor':
            # user = habr_bot_logic.anketa_get_user(call.message)
            # if not user:
            #     bot.send_message(call.message.chat.id, 'Сначала зарегестрируйся!', reply_markup=markup_start)
            pass


        if call.data == 'del':
            command = f'DELETE FROM anketa WHERE id = {call.message.chat.id}'
            habr_bot_logic.execute_sql(command)

            bot.send_message(call.message.chat.id, 'Ваша анкета удалена! ', reply_markup=markup_start)

        if call.data == 'test':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='пыщь')
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='пыщь')



if __name__ == '__main__':
    bot.infinity_polling()
