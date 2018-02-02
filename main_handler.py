#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import datetime


# also we are in need of class for processing methods (reminder of schedule, answerer...)


# web
class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=5):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}

        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']

        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'

        resp = requests.post(self.api_url + method, params)

        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update


# buildup, missing pairs of tasks for list of scheds
lessons = [
    '10:15 — 13:30 К-923\nСтатистические методы обработки информации (доп.главы)\nОвсянникова Н.В.\n\n14:30 — 17:00 Д-304\nЦифровые динамические системы\nКтитров С.В.',
    'Отдыхаем',
    '10:15 — 12:40 К-923\nЦифровые динамические системы\nКтитров С.В\n\n13:35 — 16:05 К-923\n(четные) Статистические методы обработки информации (доп. главы)\nОвсянникова Н.В.\n(нечетные) Теория игр и исследование операций (доп. главы) Коновалов Р.В., Кулябичев Ю.П.\n\n16:15 — 18:40 (четные) К-822, (нечетные) К-307\nСтандартизация информационных технологий\nСтепанова Е.Б.',
    '10:15 — 13:30 В-407\nВеб-программирование\nЛеонова Н.М.\n\n14:30 — 17:00 K-822\n(четные) Учебная (научно-исследовательская) практика\n(нечетные) Стандартизация информационных технологий\nСтепанова Е.Б.',
    '08:30 — 10:05 каф.20\nВоенная подготовка\n\n10:15 — 17:00 каф.20\nВоенная подготовка',
    '09:20 — 12:40 Д-312\nТеория игр и исследование операций (доп. главы)\nКоновалов Р.В., Кулябичев Ю.П.\n\n14:30 — 17:50 Д-304\nМатематическое обеспечение систем специального назначения\nПивторацкая С.В.',
    'Отдыхаем']

token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"
test_chat_id = -1001192271209  # 331's chat_id
test_my_id = 363412185  # my test chat (not group, tet-a-tet)
subscribers_hour = 5

greet_bot = BotHandler(token)

# need add alternative commands such as /command@bot_name? (for group chat and autocomplete on desktops)
greetings = '/knockhead'  # test func
subscriptions = '/subscribe'  # feature func
sched_days = ('/mon', '/tue', '/wed', '/thu', '/fri', '/sat', '/sun')
sched_coms = ('/today', '/tomorrow')
commands_vocabulary = {
    '/today': -1,
    '/tomorrow': 0,

    '/mon': 0,
    '/tue': 1,
    '/wed': 2,
    '/thu': 3,
    '/fri': 4,
    '/sat': 5,
    '/sun': 6
}


def main():
    new_offset = None

    # set marker for hardcoded schedule alert
    bot_start_date = datetime.datetime.now()
    if bot_start_date.hour > subscribers_hour:
        bot_start_date += datetime.timedelta(days=1)
    next_day = bot_start_date.day

    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour

        greet_bot.get_updates(new_offset)
        last_update = greet_bot.get_last_update()

        # hardsched, need add subscribers list (future) and connect it's elements with test_chat_id's field (replace it)
        if today == next_day and hour == subscribers_hour:  # our time is +3 hours
            greet_bot.send_message(test_chat_id, 'Today is {} day of a week'.format(now.isoweekday()))

            # test, later replace with test_chat_id and remove previous test string
            greet_bot.send_message(test_my_id, 'Today:\n{}'.format(lessons[now.isoweekday() - 1]))
            greet_bot.send_message(test_my_id, 'Tomorrow:\n{}'.format(lessons[(now.isoweekday()) % 7]))

            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day  # it works

        if not last_update:
            continue

        # see JSON-style by getUpdates with offline worker on server
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']  # sometimes it works wrong? (rare error, group chat, sys_mesg?)
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['from']['first_name']

        # command's reactions
        if last_chat_text.lower() in greetings:
            greet_bot.send_message(last_chat_id, 'NO U, {}'.format(last_chat_name))

        if last_chat_text.lower() in sched_coms:
            greet_bot.send_message(last_chat_id, lessons[(now.isoweekday() + commands_vocabulary[last_chat_text]) % 7])

        if last_chat_text.lower() in sched_days:
            greet_bot.send_message(last_chat_id, lessons[commands_vocabulary[last_chat_text]])

        new_offset = last_update_id + 1  # mmm... it works?


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

