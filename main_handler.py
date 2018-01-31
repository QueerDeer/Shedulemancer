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

greet_bot = BotHandler(token)

greetings = '/knockhead'
subscriptions = '/subscribe'
scheds = ('/mon', '/tue', '/wed', '/thu', '/fri', '/sat', '/today')

now = datetime.datetime.now()


def main():
    new_offset = None
    next_day = now.day

    while True:
        greet_bot.get_updates(new_offset)

        today = now.day
        hour = now.hour

        last_update = greet_bot.get_last_update()

        # need add subscription checking (list) and connect it's elements with test_chat_id's field (replace it)
        if today == next_day and hour == 8:  # our time is +3 hours
            greet_bot.send_message(test_chat_id, 'Today is {} day of a week'.format(now.isoweekday()))
            next_date = now + datetime.timedelta(days=1)
            next_day = next_date.day  # doesnt't work?

        if not last_update:
            continue

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']  # sometimes it works wrong, it may connect with next_day too
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

