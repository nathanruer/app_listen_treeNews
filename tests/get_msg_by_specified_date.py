from datetime import datetime
import sqlite3

DATABASE_NAME = "../LISTEN_TREENEWS/messages.db"
TABLE_NAME = "messages"


def get_messages_by_specified_date(date_str):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT title, body, url, added_time FROM {TABLE_NAME} WHERE added_time LIKE ?",
            (date_str + "%",),
        )
        messages = cursor.fetchall()

    messages_by_specified_date = []
    for message in messages:
        messages_by_specified_date.append({
            "title": message[0],
            "body": message[1],
            "url": message[2],
            "added_time": message[3],
        })

    return messages_by_specified_date


if __name__ == "__main__":
    date_str = input("Entrez la date sous la forme 'AAAA-MM-JJ' : ")
    messages_by_specified_date = get_messages_by_specified_date(date_str)

    print(f"Messages added on {date_str}:")
    for message in messages_by_specified_date:
        print(
            f"\n- From: {message['title']}: {message['body']}\nSource: {message['url']} - {message['added_time']}")
