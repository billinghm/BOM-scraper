import sqlite3

con = sqlite3.connect('weather.db')

c = con.cursor()
# c.execute("""DROP TABLE locat""")
c.execute("""CREATE TABLE IF NOT EXISTS locat(
id INTEGER PRIMARY KEY,
name TEXT
)""")
# c.execute("""DROP TABLE locations""")

c.execute("""CREATE TABLE IF NOT EXISTS locations(
id INTEGER PRIMARY KEY,
name TEXT,
date TEXT,
temp REAL, 
wind_speed REAL,
wind_dir TEXT,
humidity REAL, 
rain REAL,
cloud TEXT

)""")
# c.execute("DROP TABLE users")
c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
email TEXT,
Firstname TEXT,
Surname TEXT,
password TEXT
)""")

c.execute("""SELECT * FROM users""")
data = c.fetchall()
print(data)
