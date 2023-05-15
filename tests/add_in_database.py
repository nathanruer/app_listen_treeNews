import sqlite3
from datetime import datetime


DATABASE_NAME = "messages.db"
TABLE_NAME = "messages"

# Open connection and create cursor object
conn = sqlite3.connect(DATABASE_NAME)
c = conn.cursor()

title = "test_title"
body = "test_body"
url = "test_url"

# Insert data into table
with sqlite3.connect(DATABASE_NAME) as conn:
    c.execute(
        f"INSERT INTO {TABLE_NAME} (id, title, body, url, added_time) VALUES (NULL, ?, ?, ?, ?)",
        (title, body, url, datetime.now())
    )

# Save changes to database
conn.commit()

# Retrieve data from table
c.execute("SELECT * FROM messages")
rows = c.fetchall()

# Print data
for row in rows:
    print(f"{row}\n")

# Close the connection
conn.close()
