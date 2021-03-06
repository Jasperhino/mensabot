#!/usr/bin/env python3.6
import re
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
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content.decode("utf8")
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        return None
    return content

def get_json_from_url(url):
    content = get_url(url)
    if content:
        js = json.loads(content)
        return js
    return None

def get_updates():
    url = URL_BOT + "getUpdates"
    js = get_json_from_url(url)
    if js:
        return js
    return None

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
    print("Response:", get_url(url))

def edit_message(text, chat_id, message_id, reply_markup=None):
    print(f"Editing message {message_id} in {chat_id} to: {text}")
    url = URL_BOT + "editMessageText?text={}&chat_id={}&message_id={}&parse_mode={}".format(text, chat_id, message_id, "Markdown")
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    print("Response:", get_url(url))
    
def build_keyboard(options):
    keyboard = [[option] for option in options]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_inline_keyboard(keyboard):
    reply_markup = {"inline_keyboard":keyboard}
    return json.dumps(reply_markup)

def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton("Online anzeigen", url=URL_MENSA_BUTTON)]]
    return json.dumps(InlineKeyboardMarkup(keyboard).to_dict())

def callback_keyboard():
    keyboard = [[
                InlineKeyboardButton('<--', callback_data='b'),
                InlineKeyboardButton('-->', callback_data='f')
                ]]
    return json.dumps(InlineKeyboardMarkup(keyboard).to_dict())

def get_todays_menu():
    return get_menu(0)

def get_menu(id):
    data = get_json_from_url(URL_MENSA)
    if not data:
        return "Ups... Something went wrong. Sry :/"
    if len(data['wochentage']) <= id:
        return "Keine Angebote"
    day = data['wochentage'][id]

    string_list = []    
    string_list.append(messages.DATE)
    string_list.append(day['datum']['data'] + '\n')

    if 'angebote' in day['datum']:
        angebote = day['datum']['angebote']

        for angebot in angebote:
            string_list.append("\n*" + angebot['titel'] + '*')
            if angebot['filter']['zutaten']['vegan']:
                string_list.append(" _(vegan)_")
            if angebot['filter']['zutaten']['vegetarisch']:
                string_list.append(" _(vegetarisch)_")
            string_list.append('\n' + angebot['beschreibung'] + '\n')
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
        print(f"Handling Update: {update}")
        # Handling chat commands
        if 'message' in update:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            print("Chat " + str(chat_id) + ": " + text)
            if text == '/start':
                send_message(messages.START, chat_id)
                if db.contains(chat_id):
                    db.update_listening(chat_id, 1)
                else:
                    db.add_entry(chat_id)
                schedule_listener(chat_id, db.get_time(chat_id))
            elif text == '/stop':
                send_message(messages.STOP, chat_id)
                schedule.clear(chat_id)
                db.update_listening(chat_id, 0)
            elif text == '/help':
                send_message(messages.HELP, chat_id)
            elif text == '/menu':
                todays_menu = get_todays_menu()
                send_message(todays_menu, chat_id, main_menu_keyboard())
            elif text == '/test':
                send_message("menu test:", chat_id, main_menu_keyboard())
            else:
                m = re.search("([0-1]?\d|2[0-3])[:|.][0-5]\d", text)
                if m:
                    time = m[0]
                    if len(time) < 5:
                        time = '0' + time
                    time = time[:2] + ':' + time[3:]
                    schedule_listener(chat_id, time)
                    send_message(f"{messages.ACK} {time}", chat_id)
                    db.update_time(chat_id, time)
                else: send_message("Wat?", chat_id)
            
        # Handling callbacks
        if 'callback_query' in update:
            print("Handling Callback")
            callback_query = update["callback_query"]

            message_id = callback_query["message"]["message_id"]
            chat_id = callback_query["message"]["chat"]["id"]
            
            data = callback_query["data"]
            if data == 'f':
                print("Recieved Callback", data)
            elif data == 'b':
                print("Recieved Callback", data)
            edit_message(data, chat_id, message_id, main_menu_keyboard())
    
def save_json_to_file(data):
    with open(FILENAME, 'w') as outfile:
        json.dump(data, outfile)

def broadcast_todays_menu():
    todays_menu = get_todays_menu()
    keyboard = main_menu_keyboard()

    for chat_id in db.get_all_listeners():
        send_message(todays_menu, chat_id, keyboard)
    
def send_todays_menu(chat_id):
    todays_menu = get_todays_menu()
    keyboard = main_menu_keyboard()
    send_message(todays_menu, chat_id, keyboard)

# Test
def get_and_save():
    data = get_json_from_url(URL_MENSA)
    save_json_to_file(data)

def schedule_all_listeners():
    for (chat_id, time) in db.get_all_listeners():
        schedule_listener(chat_id, time)

def schedule_listener(chat_id, time):
        print(f"scheduling {chat_id} at {time}")
        schedule.clear(chat_id)
        job = schedule.every().day.at(time).do(send_todays_menu, chat_id)
        job.tags.add(chat_id)

def main():
    try:
        db.setup()
        schedule_all_listeners()
        last_update_id = None
        print('Server is running...')
    except Exception as e:
        logging.error(traceback.format_exc())
    while True:
        try:
            schedule.run_pending()
            updates = get_updates(last_update_id)
            if 'result' in updates:
                if len(updates["result"]) > 0:
                    last_update_id = get_last_update_id(updates) + 1
                handle_updates(updates)

            time.sleep(0.5)
        except Exception as e:
            logging.error(traceback.format_exc())


            
if __name__ == '__main__':
    main()