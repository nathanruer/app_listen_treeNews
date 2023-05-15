import json
import requests
import websocket
import sqlite3
import datetime
import time
from dotenv import load_dotenv
import os
load_dotenv()


WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DATABASE_NAME = "messages.db"
TABLE_NAME = "messages"
PAGE_SIZE = 50


def build_content(title, body, info, url, link, timestamp):
    is_reply = info.get('isReply', False)
    is_retweet = info.get('isRetweet', False)
    is_quote = info.get('isQuote', False)
    tweet_id = info.get('twitterId', False)

    prefix = "NEW FROM:"
    if is_reply:
        prefix = "NEW REPLY FROM:"
    elif is_retweet:
        prefix = "NEW RT FROM:"
    elif is_quote:
        prefix = "NEW QUOTE FROM:"

    content = f"**.__{prefix} {title}**"

    if body:
        content += f"\n\n{body}"

    # Connection to the database
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        # Source web
        if url:
            content += f"\n\nSOURCE: {url}"
        # Source tweet
        elif link:
            content += f"\n\nSOURCE: {link}"
            url = link

        # Convert the timestamp to a datetime object
        datetime_obj = datetime.datetime.fromtimestamp(timestamp / 1000.0)

        # Format the date according to the desired format
        formatted_date = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

        # Store the message in the database with the retrieved timestamp
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (id, title, body, url, added_time) VALUES (NULL, ?, ?, ?, ?)",
            (title, body, url, formatted_date)
        )
        # Format de l'heure ajouté : Date: 2023-03-28 11:39:33.779000

    return content


def on_message(ws, message):
    try:
        json_msg = json.loads(message)
        title = json_msg['title']
        body = json_msg.get('body', '')
        info = json_msg.get('info', {})
        url = json_msg.get('url', '')
        link = json_msg.get('link', '')
        timestamp = json_msg.get('time')

        content = build_content(title, body, info, url, link, timestamp)

        # Send the message to Discord
        payload = {"content": content}
        requests.post(WEBHOOK_URL, json=payload)

    except Exception as e:
        print(f"Erreur lors de l'analyse du message: {e}")


def on_error(ws, error):
    print(f"Erreur: {error}")


def on_close(ws):
    print("Fermé")


def on_open(ws):
    print("Ouvert")


def get_messages(page):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        offset = (page - 1) * PAGE_SIZE
        cursor.execute(
            f"SELECT * FROM {TABLE_NAME} ORDER BY added_time DESC LIMIT ? OFFSET ?",
            (PAGE_SIZE, offset))
        rows = cursor.fetchall()
        return rows


def listen_treenews_function():
    # Create the database table if it doesn't exist using a context manager
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id INTEGER PRIMARY KEY, title TEXT, body TEXT, url TEXT, added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()

    # Connect to the websocket
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://news.treeofalpha.com/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)

    ws.run_forever()


if __name__ == "__main__":
    listen_treenews_function()
