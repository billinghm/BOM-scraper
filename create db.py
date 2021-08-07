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
cloud TEXT,
lat TEXT,
long TEXT

)""")
# c.execute("DROP TABLE users")
c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
email TEXT,
Firstname TEXT,
Surname TEXT,
password TEXT,
location TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS user_locations(
id INTEGER,
location TEXT
)""")
# c.execute("""SELECT * FROM users""")
# data = c.fetchall()
# print(data)
query = """SELECT locations.lat, locations.long FROM locations 
    INNER JOIN users ON users.location = locations.name 
    WHERE users.id = ? LIMIT 1"""
c.execute(query, (1,)
    )
new_data = c.fetchall()
print(new_data)