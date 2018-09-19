#!/usr/bin/env python3.6

import json
import requests
import urllib
import time
import schedule
import traceback
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import messages
from mysqlhelper import DBHelper

try:
    db = DBHelper()
except Exception as e:
    logging.error(traceback.format_exc())

TOKEN = "658431448:AAF6HYQVwJ4hs5oOfrZc8dpSX6exP7G5VZ0"
URL_BOT = "https://api.telegram.org/bot{}/".format(TOKEN)
URL_MENSA = "https://www.studentenwerk-potsdam.de/essen/unsere-mensen-cafeterien/detailinfos/?tx_typoscriptrendering%5Bcontext%5D=%7B%22record%22%3A%22pages_66%22%2C%22path%22%3A%22tt_content.list.20.ddfmensa_ddfmensajson%22%7D&tx_ddfmensa_ddfmensajson%5Bmensa%5D=6&cHash=0c7f1095dcc78ff74b6cd32cd231c75f"
URL_MENSA_BUTTON = "www.studentenwerk-potsdam.de/mensa-griebnitzsee.html"
FILENAME = "menu.json"

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL_BOT + "getUpdates"
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    print("Sending to ", chat_id ,': ', text)
    text = urllib.parse.quote_plus(text)
    url = URL_BOT + "sendMessage?text={}&chat_id={}&parse_mode={}".format(text, chat_id, "Markdown")
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)
    
def build_keyboard(options):
    keyboard = [[option] for option in options]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_inline_keyboard(keyboard):
    reply_markup = {"inline_keyboard":keyboard}
    return json.dumps(reply_markup)

def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Option 1', callback_data='m1')],
                [InlineKeyboardButton('Option 2', callback_data='m2')],
                [InlineKeyboardButton('Option 3', callback_data='m3')]]
    return InlineKeyboardMarkup(keyboard)

def get_todays_menu():
    return get_menu(0)

def get_menu(id):
    data = get_json_from_url(URL_MENSA)
    if len(data['wochentage']) <= id:
        return "Keine Angebote"
    day = data['wochentage'][id]

    string_list = []    
    string_list.append(messages.DATE)
    string_list.append(day['datum']['data'] + '\n')

    if 'angebote' in day['datum']:
        angebote = day['datum']['angebote']

        for angebot in angebote:
            string_list.append("*" + angebot['titel'] + '*\n')
            string_list.append(angebot['beschreibung'] + '\n')

    else: string_list.append("_Keine Angebote_\n")

    result = ''.join(string_list)
    print(f"Menu for Day {id}: {result}")
    return result

def get_updates(offset=None):
    url = URL_BOT + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            print("Chat " + str(chat_id) + ": " + text)

            if text == '/start':
                send_message(messages.START, chat_id)
                db.add_entry(chat_id)  # Database checks if its duplicate
            elif text == '/stop':
                send_message(messages.STOP, chat_id)
                db.delete_entry(chat_id)
            elif text == '/help':
                send_message(messages.HELP, chat_id)
            elif text == '/menu':
                todays_menu = get_todays_menu()
                keyboard = [[InlineKeyboardButton("Online anzeigen", url=URL_MENSA_BUTTON)]]
                markup = json.dumps(InlineKeyboardMarkup(keyboard).to_dict())
                send_message(todays_menu, chat_id, markup)

        except KeyError:
            pass
    
def save_json_to_file(data):
    with open(FILENAME, 'w') as outfile:
        json.dump(data, outfile)

def broadcast_todays_menu():
    todays_menu = get_todays_menu()
    keyboard = [[InlineKeyboardButton("Online anzeigen", url=URL_MENSA_BUTTON)]]
    markup = json.dumps(InlineKeyboardMarkup(keyboard).to_dict())

    for chat_id in db.get_all_chats():
        print("chat", db.get_all_chats())
        send_message(todays_menu, chat_id, markup)

# Test
def get_and_save():
    data = get_json_from_url(URL_MENSA)
    save_json_to_file(data)

def main():
    try:
        for i in range(0,14):
            get_menu(i)

# """        """  db.setup()

#         schedule.every().day.at("14:35").do(broadcast_todays_menu)
#         last_update_id = None
#         print('Server is listening...')
        
#         while True:
#             schedule.run_pending()
#             updates = get_updates(last_update_id)
#             if len(updates["result"]) > 0:
#                 last_update_id = get_last_update_id(updates) + 1
#             handle_updates(updates)

#             time.sleep(0.5) """ """

    except Exception as e:
        logging.error(traceback.format_exc())
            
if __name__ == '__main__':
    main()