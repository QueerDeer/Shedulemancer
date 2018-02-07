#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import datetime
import psycopg2
import subprocess


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
        try:
            result_json = resp.json()['result']
        except:
            print('not json')
            result_json = None

        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'

        resp = requests.post(self.api_url + method, params)

        return resp

    def delete_message(self, chat_id, message_id):
        params = {'chat_id': chat_id, 'message_id': message_id}
        method = 'deleteMessage'

        resp = requests.post(self.api_url + method, params)

        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update

# connect to postgresql database (from devcenter (documentation) - easier way is vulnerable to credential changes)
proc = subprocess.Popen('heroku config:get DATABASE_URL -a aqueous-mesa-67117', stdout=subprocess.PIPE, shell=True)
db_url = proc.stdout.read().decode('utf-8').strip() + '?sslmode=require'

conn = psycopg2.connect(db_url)

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
test_chat_id = -1001192271209  # 331's chat_id, pull it from db
test_my_id = 363412185  # my test chat (not group, tet-a-tet)

greet_bot = BotHandler(token)

# need add alternative commands such as /command@bot_name? (for group chat and autocomplete on desktops)
greetings = ('/knockhead', '/knockhead@mephi_shed_bot')
subscriptions = '/subscribe'  # pull chat_id, default alert_flag and smth else to db in 'if last_chat_text.lower()...'
sched_days = ('/mon', '/mon@mephi_shed_bot', '/tue', '/tue@mephi_shed_bot', '/wed', '/wed@mephi_shed_bot', '/thu',
              '/thu@mephi_shed_bot', '/fri', '/fri@mephi_shed_bot', '/sat', '/sat@mephi_shed_bot', '/sun',
              '/sun@mephi_shed_bot')
sched_coms = ('/today', '/today@mephi_shed_bot', '/tomorrow', '/tomorrow@mephi_shed_bot')
commands_vocabulary = {
    '/today': -1,
    '/today@mephi_shed_bot': -1,
    '/tomorrow': 0,
    '/tomorrow@mephi_shed_bot': 0,

    '/mon': 0,
    '/mon@mephi_shed_bot': 0,
    '/tue': 1,
    '/tue@mephi_shed_bot': 1,
    '/wed': 2,
    '/wed@mephi_shed_bot': 2,
    '/thu': 3,
    '/thu@mephi_shed_bot': 3,
    '/fri': 4,
    '/fri@mephi_shed_bot': 4,
    '/sat': 5,
    '/sat@mephi_shed_bot': 5,
    '/sun': 6,
    '/sun@mephi_shed_bot': 6
}


def main():
    new_offset = None

    subscribers_hour = 5
    first_alert_message_id = 0
    second_alert_message_id = 0

    # set marker for hardcoded schedule alert
    bot_start_date = datetime.datetime.now()
    if bot_start_date.hour > subscribers_hour:  # correct it with checking alert_flag (pull it from db previously)
        bot_start_date += datetime.timedelta(days=1)
    next_day = bot_start_date.day

    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour

        greet_bot.get_updates(new_offset)
        last_update = greet_bot.get_last_update()

        # hardsched, need if for db alert_flag (is already pulled)
        if today == next_day and hour == subscribers_hour:  # our time is +3 hours
            try:
                greet_bot.delete_message(test_chat_id, first_alert_message_id)  # pull mesg_id-s from db
                greet_bot.delete_message(test_chat_id, second_alert_message_id)
            except:
                print('cannot delete my alert')

            # greet_bot.send_message(test_chat_id, 'Phew, today is {} day of a week'.format(now.isoweekday()))
            first_alert = greet_bot.send_message(test_chat_id, 'Today:\n{}'.format(lessons[now.isoweekday() - 1]))
            second_alert = greet_bot.send_message(test_chat_id, 'Tomorrow:\n{}'.format(lessons[(now.isoweekday()) % 7]))

            try:
                first_alert_message_id = first_alert.json()['result']['message_id']
                second_alert_message_id = second_alert.json()['result']['message_id']  # and then push it to db
            except:
                print('cannot get id from json')

            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day

        if not last_update:
            continue

        # see JSON-style by getUpdates with offline worker on server
        last_update_id = last_update['update_id']
        try:
            last_chat_text = last_update['message']['text']  # sometimes it works wrong (add request and smth else)
        except:
            print('no text but json, CATCH U')
            last_chat_text = 'another_action'
        try:
            last_chat_id = last_update['message']['chat']['id']
        except:
            print('no chat field or (hardly) chat id')
            last_chat_id = 363412185
        try:
            last_chat_name = last_update['message']['from']['first_name']
        except:
            print('no from field or (hardly?) first_name')
            last_chat_name = 'unknown_action'

        # command's reactions
        if last_chat_text.lower() in greetings:
            greet_bot.send_message(last_chat_id, 'NO U, {}'.format(last_chat_name))

        if last_chat_text.lower() in sched_coms:
            greet_bot.send_message(last_chat_id, lessons[(now.isoweekday() + commands_vocabulary[last_chat_text]) % 7])

        if last_chat_text.lower() in sched_days:
            greet_bot.send_message(last_chat_id, lessons[commands_vocabulary[last_chat_text]])

        if last_chat_text.lower() == 'another_action':
            greet_bot.send_message(last_chat_id, last_chat_name)

        new_offset = last_update_id + 1  # mmm... it works?


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

