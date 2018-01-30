#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import datetime

# also we are in need of class for processing methods (reminder of schedule, answerer...)


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

token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"
test_chat_id = -1001192271209  # 331's chat_id
test_my_id = 363412185  # tet-a-tet chat_id

greet_bot = BotHandler(token)

greetings = '/knockhead'
scheds = ('/mon', '/tue', '/wed', '/thu', '/fri', '/sat')

now = datetime.datetime.now()


def main():
    new_offset = None
    today = now.day
    next_day = now.day
    hour = now.hour

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()

        # doesnt work
        if today == next_day and hour == 6:  # our time is +3 hours
            greet_bot.send_message(test_chat_id, 'Today is {} day of the week'.format(today))
            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day

        # debugging
        if today == next_day and hour == 6:
            greet_bot.send_message(test_my_id, 'Today is {} day of the week'.format(today))
            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day

        if not last_update:
            continue

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']  # sometimes it works wrong
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['from']['first_name']

        if last_chat_text.lower() in greetings:
            greet_bot.send_message(last_chat_id, 'NO U, {}'.format(last_chat_name))

        new_offset = last_update_id + 1  # mmm... it works?


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

