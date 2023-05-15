import sqlite3

conn = sqlite3.connect("messages.db")
c = conn.cursor()

# Retrieve data from table
c.execute("SELECT * FROM messages")
rows = c.fetchall()

# Print data
for row in rows:
    print(f"{row}\n")

# Close the connection
conn.close()
