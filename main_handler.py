#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import datetime
import psycopg2
from urllib import parse
import os


# upgrade process of db connect/reconnect/etc. and add success checking? (make it better), remove copy-paste
# also we are in need of class for scheduling and answering (not in the main body)?

# web, gonna migrate from requests to ?
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


# postgres connector; need def: pull, push, update, ...?
class DbLoader:
    def __init__(self):
        parse.uses_netloc.append("postgres")
        self.db_url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=self.db_url.path[1:],
            user=self.db_url.username,
            password=self.db_url.password,
            host=self.db_url.hostname,
            port=self.db_url.port
        )
        cursor = conn.cursor()

        cursor.execute("SELECT sub_chat_id FROM subscribers")
        self.test_chat_id = cursor.fetchall()
        cursor.execute("SELECT alert_day FROM subscribers")
        self.next_day = cursor.fetchall()
        cursor.execute("SELECT today_mesg_id FROM subscribers")
        self.first_alert_message_id = cursor.fetchall()
        cursor.execute("SELECT tomorrow_mesg_id FROM subscribers")
        self.second_alert_message_id = cursor.fetchall()

        cursor.close()
        conn.close()

    def set_last_messages(self, f_a_m_id, s_a_m_id):
        conn = psycopg2.connect(
            database=self.db_url.path[1:],
            user=self.db_url.username,
            password=self.db_url.password,
            host=self.db_url.hostname,
            port=self.db_url.port
        )
        cursor = conn.cursor()

        cursor.execute("UPDATE subscribers SET today_mesg_id = (%s)", f_a_m_id)
        conn.commit()
        cursor.execute("UPDATE subscribers SET tomorrow_mesg_id = (%s)", s_a_m_id)
        conn.commit()

        self.first_alert_message_id = f_a_m_id
        self.second_alert_message_id = s_a_m_id

        cursor.close()
        conn.close()

    def reschedule(self, next_day):
        conn = psycopg2.connect(
            database=self.db_url.path[1:],
            user=self.db_url.username,
            password=self.db_url.password,
            host=self.db_url.hostname,
            port=self.db_url.port
        )
        cursor = conn.cursor()

        cursor.execute("UPDATE subscribers SET alert_day = (%s)", next_day)
        conn.commit()

        self.next_day = next_day

        cursor.close()
        conn.close()


# buildup
lessons = [
    '10:15 — 13:30 К-923\nСтатистические методы обработки информации (доп.главы)\nОвсянникова Н.В.\n\n14:30 — 17:00 Д-304\nЦифровые динамические системы\nКтитров С.В.',
    'Отдыхаем',
    '10:15 — 12:40 К-923\nЦифровые динамические системы\nКтитров С.В\n\n13:35 — 16:05 К-923\n(нечетные) Статистические методы обработки информации (доп. главы)\nОвсянникова Н.В.\n(четные) Теория игр и исследование операций (доп. главы) Коновалов Р.В., Кулябичев Ю.П.\n\n16:15 — 18:40 (нечетные) К-822, (четные) К-307\nСтандартизация информационных технологий\nСтепанова Е.Б.',
    '10:15 — 13:30 В-407\nВеб-программирование\nЛеонова Н.М.\n\n14:30 — 17:00 K-822\n(четные) Учебная (научно-исследовательская) практика\n(нечетные) Стандартизация информационных технологий\nСтепанова Е.Б.',
    '08:30 — 10:05 каф.20\nВоенная подготовка\n\n10:15 — 17:00 каф.20\nВоенная подготовка',
    '09:20 — 12:40 Д-312\nТеория игр и исследование операций (доп. главы)\nКоновалов Р.В., Кулябичев Ю.П.\n\n14:30 — 17:50 Д-304\nМатематическое обеспечение систем специального назначения\nПивторацкая С.В.',
    'Отдыхаем']

# need add alternative commands such as /command@bot_name? (for group chat and autocomplete on desktops)
greetings = ('/knockhead', '/knockhead@mephi_shed_bot')
subscriptions = '/subscribe'  # pull chat_id, default alert_flag and smth else to db in 'if last_chat_text.lower()...'
sched_days = ('/mon', '/mon@mephi_shed_bot', '/tue', '/tue@mephi_shed_bot', '/wed', '/wed@mephi_shed_bot', '/thu',
              '/thu@mephi_shed_bot', '/fri', '/fri@mephi_shed_bot', '/sat', '/sat@mephi_shed_bot', '/sun',
              '/sun@mephi_shed_bot')
sched_coms = ('/today', '/today@mephi_shed_bot', '/tomorrow', '/tomorrow@mephi_shed_bot')
secret_test_bd_com = ('/catchemall')
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

test_my_id = 363412185  # my test chat (not group, tet-a-tet)
subscribers_hour = 5
token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"

greet_bot = BotHandler(token)
db_loader = DbLoader()


def main():
    new_offset = None

    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour

        greet_bot.get_updates(new_offset)
        last_update = greet_bot.get_last_update()

        # hardsched
        if today == db_loader.next_day and hour == subscribers_hour:  # our time is +3 hours

            try:
                greet_bot.delete_message(db_loader.test_chat_id, db_loader.first_alert_message_id)
                greet_bot.delete_message(db_loader.test_chat_id, db_loader.second_alert_message_id)
            except:
                print('cannot delete my alert')

            # greet_bot.send_message(test_chat_id, 'Phew, today is {} day of a week'.format(now.isoweekday()))
            first_alert = greet_bot.send_message(db_loader.test_chat_id,
                                                 'Today:\n{}'.format(lessons[now.isoweekday() - 1]))
            second_alert = greet_bot.send_message(db_loader.test_chat_id,
                                                  'Tomorrow:\n{}'.format(lessons[(now.isoweekday()) % 7]))

            try:
                first_alert_message_id = first_alert.json()['result']['message_id']
                second_alert_message_id = second_alert.json()['result']['message_id']

                db_loader.set_last_messages(first_alert_message_id, second_alert_message_id)
            except:
                print('cannot get id from json')

            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day
            db_loader.reschedule(next_day)

        if not last_update:
            continue

        # see JSON-style by getUpdates with offline worker on server
        last_update_id = last_update['update_id']
        try:
            last_chat_text = last_update['message']['text']  # sometimes it works wrong (add request and smth else)
        except:
            print('no text but json')
            last_chat_text = 'another_action'  # add, dismiss, sticker, file
        try:
            last_chat_id = last_update['message']['chat']['id']
        except:
            print('no chat field or (hardly) chat id')
            last_chat_id = test_my_id
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

        # add pull to db for if subscribe command
        # if last_chat_text.lower() in subscriptions:

        # for tests
        if last_chat_text.lower() in secret_test_bd_com:
            greet_bot.send_message(test_my_id, "sub: " + str(db_loader.test_chat_id) + "\nnext alert date: " + str(
                db_loader.next_day) + "\nlast today: " + str(
                db_loader.first_alert_message_id) + "\nlast tomorrow: " + str(db_loader.second_alert_message_id))

        # also for tests
        # if last_chat_text.lower() == 'another_action':
        #    greet_bot.send_message(last_chat_id, last_chat_name)

        new_offset = last_update_id + 1  # mmm... it works?


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

