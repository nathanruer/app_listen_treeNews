from datetime import datetime
import logging
import sqlite3
from flask import Flask, render_template, request, g, send_from_directory, url_for
import os
import multiprocessing
from listen_treenews import listen_treenews_function

app = Flask(__name__)
DATABASE_NAME = "messages.db"
TABLE_NAME = "messages"

SELECT_FIELDS = "title, body, url, added_time"
QUERY_ALL_MESSAGES = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} ORDER BY added_time DESC"
QUERY_MESSAGES_BY_DATE = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE added_time LIKE ? ORDER BY added_time DESC"
QUERY_MESSAGES_BY_KEYWORD = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE title LIKE ? OR body LIKE ? ORDER BY added_time DESC"
QUERY_MESSAGES_BY_KEYWORD_AND_DATE = f"SELECT {SELECT_FIELDS} FROM {TABLE_NAME} WHERE added_time LIKE ? AND (title LIKE ? OR body LIKE ?) ORDER BY added_time DESC"
OFFSET_LIMIT = 10  # Limit for the number of results per page


@app.route('/static/<path:path>')
def serve_images(path):
    """Handler for serving images."""
    images_directory = os.path.join(os.getcwd(), 'images')
    return send_from_directory(images_directory, path)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def get_messages(query, params=()):
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        messages = []
        for row in rows:
            title = row['title']
            body = row['body']
            url = row['url']
            # Convert the date to the desired format
            date = datetime.strptime(
                row['added_time'], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            messages.append((title, body, url, date))
        return messages


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/messages")
def messages():
    offset = request.args.get('offset', 0, type=int)
    messages = get_messages(
        f"{QUERY_ALL_MESSAGES} LIMIT {OFFSET_LIMIT} OFFSET {offset}")
    return render_template("messages.html", messages=messages)


@app.route('/messages/filter')
def messages_filter():
    date_str = request.args.get('date', '')
    keyword = request.args.get('keyword', '')

    # Choose the appropriate query based on the provided parameters
    if date_str and keyword:
        query = QUERY_MESSAGES_BY_KEYWORD_AND_DATE
        params = (date_str + '%', '%' + keyword + '%', '%' + keyword + '%')
    elif date_str:
        query = QUERY_MESSAGES_BY_DATE
        params = (date_str + '%',)
    elif keyword:
        query = QUERY_MESSAGES_BY_KEYWORD
        params = ('%' + keyword + '%', '%' + keyword + '%')
    else:
        query = QUERY_ALL_MESSAGES
        params = ()

    # Add the query
    query = f'{query}'

    # Fetch the messages from the database
    messages = get_messages(query, params)

    # Render the appropriate template
    if date_str and keyword:
        template = 'messages_by_keyword_and_date.html'
    elif date_str:
        template = 'messages_by_date.html'
    elif keyword:
        template = 'messages_by_keyword.html'
    else:
        template = 'messages.html'

    return render_template(template, messages=messages, date=date_str, keyword=keyword)


@app.teardown_appcontext
def teardown_db(exception):
    close_db()


if __name__ == '__main__':
    # Start the listen_treenews_function in a separate process
    p = multiprocessing.Process(target=listen_treenews_function)
    p.start()

    # Start the Flask application
    app.run(debug=True, use_reloader=False)
