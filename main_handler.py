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

token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"
test_chat_id = -1001192271209  # 331's chat_id
subscribers_hour = 8

greet_bot = BotHandler(token)

# need add alternative commands such as /command@bot_name? (for group chat and autocomplete on desktops)
greetings = '/knockhead'
subscriptions = '/subscribe'
scheds = ('/mon', '/tue', '/wed', '/thu', '/fri', '/sat', '/today', '/tomorrow')


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

        new_offset = last_update_id + 1  # mmm... it works?


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

