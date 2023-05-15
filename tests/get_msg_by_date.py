import sqlite3
from datetime import datetime

DATABASE_NAME = "../LISTEN_TREENEWS/messages.db"
TABLE_NAME = "messages"


def get_messages_by_date():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT title, body, url, added_time FROM {TABLE_NAME} ORDER BY added_time ASC")
        messages = cursor.fetchall()

    messages_by_date = {}

    for message in messages:
        title, body, url, added_time = message
        added_time = datetime.strptime(added_time, "%Y-%m-%d %H:%M:%S.%f")
        date = added_time.date()

        if date not in messages_by_date:
            messages_by_date[date] = []

        messages_by_date[date].append(
            {'title': title, 'body': body, 'url': url, 'added_time': added_time})

    return messages_by_date


if __name__ == "__main__":
    messages_by_date = get_messages_by_date()

    for date, messages in messages_by_date.items():
        print(f"Messages added on {date.strftime('%Y-%m-%d')}:")
        for message in messages:
            print(
                f"\n- From: {message['title']}: {message['body']}\nSource: {message['url']} - {message['added_time']}")
