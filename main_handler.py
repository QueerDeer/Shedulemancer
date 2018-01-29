#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import datetime


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


token = "545213183:AAF2vAqvhV_YTgP-LUZrV3vsBkF6iNbNWJA"
greet_bot = BotHandler(token)
greetings = 'FuckYou'
now = datetime.datetime.now()


def main():
    new_offset = None
    today = now.day
    hour = now.hour
    minute = now.minute

    while True:
        greet_bot.get_updates(new_offset)

        last_update = greet_bot.get_last_update()
        if not last_update:
            continue
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        if last_chat_text.lower() in greetings:
            greet_bot.send_message(last_chat_id, 'NO U, {}'.format(last_chat_name))

        if today == now.day and hour == 4 and minute == 20:
            greet_bot.send_message(last_chat_id, 'Today is {}'.format(today.strftime("%A")))

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
