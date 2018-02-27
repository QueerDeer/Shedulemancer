# -*- coding: cp1251 -*-
import config
import postgres

import telebot
from telebot import types
from telebot.util import async

import datetime

bot = telebot.TeleBot(config.token)


# for '/start', '/help'
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Hi, folks!")


# for tests
@bot.message_handler(commands=['knockhead'])
def handle_greet(message):
    bot.send_message(message.chat.id, 'NO U, {}'.format(message.from_user.first_name))
    bot.send_message(config.N_TEST_MY_ID,
                     (config.N_TEST_CHAT_ID, config.N_NEXT_DAY, config.N_FIRST_ALERT_MESSAGE_ID,
                      config.N_SECOND_ALERT_MESSAGE_ID))


@async
def daily_mail(self):
    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour

        #if today == config.N_NEXT_DAY and hour == config.N_SUBSCRIBERS_HOUR:  # our time is +3 hours
        if True:

            # try:
            #     bot.delete_message(config.N_TEST_CHAT_ID, config.N_FIRST_ALERT_MESSAGE_ID)
            #     bot.delete_message(config.N_TEST_CHAT_ID, config.N_SECOND_ALERT_MESSAGE_ID)
            # except:
            #     print('cannot delete my alert')

            # greet_bot.send_message(test_chat_id, 'Phew, today is {} day of a week'.format(now.isoweekday()))
            first_alert = bot.send_message(config.N_TEST_CHAT_ID,
                                                 'Today:\n{}'.format(config.N_CALENDAR_VOCABULARY[now.isoweekday() - 1]))
            second_alert = bot.send_message(config.N_TEST_CHAT_ID,
                                                  'Tomorrow:\n{}'.format(config.N_CALENDAR_VOCABULARY[(now.isoweekday()) % 7]))

            try:
                first_alert_message_id = first_alert.json()['result']['message_id']
                second_alert_message_id = second_alert.json()['result']['message_id']
            except:
                print('cannot get message_id from json')
            else:
                postgres.set_last_messages(first_alert_message_id, second_alert_message_id)

            # next_date = now + datetime.timedelta(days=1)
            # next_day = next_date.day
            # postgres.reschedule(next_day)


# supergroups
# scheduler
@bot.message_handler(commands=['today', 'tomorrow'], func=lambda message: message.chat.type == "supergroup")
def handle_calendar_neighbours(message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id,
                     config.N_LESSONS[(now.isoweekday() + config.N_CALENDAR_VOCABULARY[message.text]) % 7])


@bot.message_handler(commands=['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
                     func=lambda message: message.chat.type == "supergroup")
def handle_calendar_days(message):
    bot.send_message(message.chat.id, config.N_LESSONS[config.N_CALENDAR_VOCABULARY[message.text]])


# memeses
@bot.message_handler(commands=['add_memes'],
                     func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(
                         message.from_user.id) == (0, 0))
def handle_start_add_memes(message):
    postgres.set_user_condition(message.from_user.id, config.S_ADD_MEMES, config.S_ENTER_NAME)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Enter meme name: ", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(message.from_user.id) == (
    config.S_ADD_MEMES, config.S_ENTER_NAME))
def user_entering_name(message):
    postgres.set_user_condition(message.from_user.id, config.S_ADD_MEMES, config.S_ENTER_TAGS)
    global tmp_name
    tmp_name = message.text
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Enter key words for your meme, separated by commas: ", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(message.from_user.id) == (
    config.S_ADD_MEMES, config.S_ENTER_TAGS))
def user_entering_tags(message):
    global tmp_tags
    tmp_tags = []
    tags = message.text.split(",")
    for tag in tags:
        tmp_tags.append(tag.strip())

    postgres.set_user_condition(message.from_user.id, config.S_ADD_MEMES, config.S_SEND_PIC)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Nice, and now send me the picture: ", reply_markup=keyboard)


@bot.message_handler(content_types=["photo"],
                     func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(
                         message.from_user.id) == (config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    tmp_file_id = message.photo[-1].file_id
    postgres.set_user_condition(message.from_user.id, 0, 0)
    postgres.insert_memes(tmp_name, tmp_file_id, tmp_tags)
    keyboard = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text="Проверить!", switch_inline_query_current_chat=tmp_name)
    keyboard.add(switch_button)
    bot.send_message(message.chat.id, "The meme is in ur base killin ur d00dz", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(message.from_user.id) ==
                         (config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Fuck, you are kidding me - there is no picture!", reply_markup=keyboard)


# tet-a-tet chats
# scheduler
@bot.message_handler(commands=['today', 'tomorrow'])
def handle_calendar_neighbours(message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id,
                     config.N_LESSONS[(now.isoweekday() + config.N_CALENDAR_VOCABULARY[message.text]) % 7])


@bot.message_handler(commands=['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'])
def handle_calendar_days(message):
    bot.send_message(message.chat.id, config.N_LESSONS[config.N_CALENDAR_VOCABULARY[message.text]])


# memeses
@bot.message_handler(commands=['add_memes'],
                     func=lambda message: postgres.get_user_condition(message.chat.id) == (0, 0))
def handle_start_add_memes(message):
    postgres.set_user_condition(message.chat.id, config.S_ADD_MEMES, config.S_ENTER_NAME)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Enter meme name: ", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: postgres.get_user_condition(message.chat.id) == (config.S_ADD_MEMES, config.S_ENTER_NAME))
def user_entering_name(message):
    postgres.set_user_condition(message.chat.id, config.S_ADD_MEMES, config.S_ENTER_TAGS)
    global tmp_name
    tmp_name = message.text
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Enter key words for your meme, separated by commas: ", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: postgres.get_user_condition(message.chat.id) == (config.S_ADD_MEMES, config.S_ENTER_TAGS))
def user_entering_tags(message):
    global tmp_tags
    tmp_tags = []
    tags = message.text.split(",")
    for tag in tags:
        tmp_tags.append(tag.strip())

    postgres.set_user_condition(message.chat.id, config.S_ADD_MEMES, config.S_SEND_PIC)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Nice, and now send me the picture: ", reply_markup=keyboard)


@bot.message_handler(content_types=["photo"], func=lambda message: postgres.get_user_condition(message.chat.id) == (
config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    tmp_file_id = message.photo[-1].file_id
    postgres.set_user_condition(message.chat.id, 0, 0)
    postgres.insert_memes(tmp_name, tmp_file_id, tmp_tags)
    keyboard = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text="Проверить!", switch_inline_query_current_chat=tmp_name)
    keyboard.add(switch_button)
    bot.send_message(message.chat.id, "The meme is in ur base killin ur d00dz", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: postgres.get_user_condition(message.chat.id) == (config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Fuck, you are kidding me - there is no picture!", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_user_condition(call):
    if call.message.chat.type == "supergroup":
        postgres.set_user_condition(call.from_user.id, 0, 0)
    else:
        postgres.set_user_condition(call.message.chat.id, 0, 0)

    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Adding meme rejected.")


@bot.inline_handler(func=lambda query: len(query.query) is 0)
def empty_query(query):
    hint = "Enter name or tag for search meme: "
    memes = postgres.get_last_memes()
    i = 0

    try:
        result = []
        for mem in memes:
            result.append(types.InlineQueryResultCachedPhoto(
                id=i,
                description=hint,
                photo_file_id=mem))
            i += 1
        bot.answer_inline_query(query.id, result, cache_time=10)

    except Exception as e:
        print(e)


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def inline_mode(query):
    try:
        exact_memes = postgres.get_memes_by_name(query.query)
        memes = postgres.get_memes_by_tag(query.query)

        if (exact_memes is not None):
            memes.append(exact_memes)
        i = 0
        result = []
        for mem in memes:
            result.append(types.InlineQueryResultCachedPhoto(
                id=i,
                photo_file_id=mem))
            i += 1
        bot.answer_inline_query(query.id, result, cache_time=10)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    config.N_TEST_CHAT_ID, config.N_NEXT_DAY, config.N_FIRST_ALERT_MESSAGE_ID, config.N_SECOND_ALERT_MESSAGE_ID =\
        postgres.check_alert()

    daily_mail(self)  # async_scheduler

    bot.polling(none_stop=True)  # message_handler
