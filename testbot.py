# -*- coding: cp1251 -*-
import config, postgres
import telebot
from telebot import types
from postgres import postgresql

import datetime

bot = telebot.TeleBot(config.token)


# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Hi, folks!")


# test commands


# supergroups
@bot.message_handler(commands=['today', 'tomorrow'], func=lambda message: message.chat.type == "supergroup")
def handle_calendar_neighbours(message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id, config.LESSONS[(now.isoweekday() + config.CALENDAR_VOCABULARY[message.text]) % 7],
                     reply_markup=keyboard)


@bot.message_handler(commands=['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'],
                     func=lambda message: message.chat.type == "supergroup")
def handle_calendar_days(message):
    bot.send_message(message.chat.id, config.LESSONS[config.CALENDAR_VOCABULARY[message.text]], reply_markup=keyboard)


@bot.message_handler(commands=['add_memes'],
                     func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(
                         message.from_user.id) == (0, 0))
def handle_start_add_memes(message):
    postgres.set_user_condition(message.from_user.id, config.S_ADD_MEMES, config.S_ENTER_NAME)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Введи имя для мема: ", reply_markup=keyboard)


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
    bot.send_message(message.chat.id, "Введи ключевые слова для поиска твоего мема через запятую: ",
                     reply_markup=keyboard)


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
    bot.send_message(message.chat.id, "Отлично, теперь пришли мне картинку твоего мема: ", reply_markup=keyboard)


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
    bot.send_message(message.chat.id, "Твой мем добавлен в базу!", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: message.chat.type == "supergroup" and postgres.get_user_condition(message.from_user.id) == (
    config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Так, блэд! Тут нет картинки!", reply_markup=keyboard)


# все для обычных диалогов
@bot.message_handler(commands=['today', 'tomorrow'])
def handle_calendar_neighbours(message):
    now = datetime.datetime.now()
    bot.send_message(message.chat.id, config.LESSONS[(now.isoweekday() + config.CALENDAR_VOCABULARY[message.text]) % 7],
                     reply_markup=keyboard)


@bot.message_handler(commands=['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'])
def handle_calendar_days(message):
    bot.send_message(message.chat.id, config.LESSONS[config.CALENDAR_VOCABULARY[message.text]], reply_markup=keyboard)


@bot.message_handler(commands=['add_memes'],
                     func=lambda message: postgres.get_user_condition(message.chat.id) == (0, 0))
def handle_start_add_memes(message):
    postgres.set_user_condition(message.chat.id, config.S_ADD_MEMES, config.S_ENTER_NAME)
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Введи имя для мема: ", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: postgres.get_user_condition(message.chat.id) == (config.S_ADD_MEMES, config.S_ENTER_NAME))
def user_entering_name(message):
    postgres.set_user_condition(message.chat.id, config.S_ADD_MEMES, config.S_ENTER_TAGS)
    global tmp_name
    tmp_name = message.text
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Введи ключевые слова для поиска твоего мема через запятую: ",
                     reply_markup=keyboard)


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
    bot.send_message(message.chat.id, "Отлично, теперь пришли мне картинку твоего мема: ", reply_markup=keyboard)


@bot.message_handler(content_types=["photo"], func=lambda message: postgres.get_user_condition(message.chat.id) == (
config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    tmp_file_id = message.photo[-1].file_id
    postgres.set_user_condition(message.chat.id, 0, 0)
    postgres.insert_memes(tmp_name, tmp_file_id, tmp_tags)
    keyboard = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text="Проверить!", switch_inline_query_current_chat=tmp_name)
    keyboard.add(switch_button)
    bot.send_message(message.chat.id, "Твой мем добавлен в базу!", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: postgres.get_user_condition(message.chat.id) == (config.S_ADD_MEMES, config.S_SEND_PIC))
def user_send_pic(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Отменить", callback_data="reset")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Так, блэд! Тут нет картинки!", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_user_condition(call):
    if call.message.chat.type == "supergroup":
        postgres.set_user_condition(call.from_user.id, 0, 0)
    else:
        postgres.set_user_condition(call.message.chat.id, 0, 0)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, "Добавление мема отменено.")


@bot.inline_handler(func=lambda query: len(query.query) is 0)
def empty_query(query):
    hint = "Введите имя мема или тег для поиска."
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
    bot.polling(none_stop=True)
