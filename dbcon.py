import sqlite3

def connect():
    con = sqlite3.connect('weather.db')
    return con