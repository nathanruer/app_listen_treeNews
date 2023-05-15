from datetime import datetime
import sqlite3
import get_msg_by_date
import get_msg_by_keyword


DATABASE_NAME = "../LISTEN_TREENEWS/messages.db"
TABLE_NAME = "messages"


def search_messages_by_date_and_keyword(keyword, date_str):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT title, body, url, added_time FROM {TABLE_NAME} WHERE added_time LIKE ?",
            (date_str + "%",),
        )
        messages = cursor.fetchall()

    matching_messages = []

    for message in messages:
        title, body, url, added_time = message
        if keyword.lower() in title.lower() or keyword.lower() in body.lower():
            matching_messages.append(message)

    if not matching_messages:
        print(
            f"No matching messages found for date {date_str} matching {keyword}")
        return

    for message in matching_messages:
        title, body, url, added_time = message
        print(f"- From: {title}: {body}\nSource: {url} - {added_time}")


if __name__ == "__main__":
    keyword = input("Entrez le terme que vous recherchez: ")
    date_str = input("Entrez la date sous la forme 'AAAA-MM-JJ' : ")
    search_messages_by_date_and_keyword(keyword, date_str)
