from datetime import datetime
import sqlite3


DATABASE_NAME = "../LISTEN_TREENEWS/messages.db"
TABLE_NAME = "messages"


def get_messages(keyword):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT title, body, url, added_time FROM {TABLE_NAME}")
        messages = cursor.fetchall()

    matching_messages = []

    for message in messages:
        title, body, url, added_time = message
        if keyword.lower() in title.lower() or keyword.lower() in body.lower():
            matching_messages.append(message)

    if not matching_messages:
        print("No matching messages found.")
        return

    for message in matching_messages:
        title, body, url, added_time = message
        print(f"- From: {title}: {body}\nSource: {url} - {added_time}")


if __name__ == "__main__":
    keyword = input("Entrez le terme que vous recherchez: ")
    get_messages(keyword)
