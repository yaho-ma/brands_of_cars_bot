import sqlite3
import asyncio
from datetime import date


def add_user_query_toDb(text_from_user):
    connection = sqlite3.connect('history.db')
    cur = connection.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS history_table (id INTEGER PRIMARY KEY AUTOINCREMENT, user_text TEXT, date DATETIME DEFAULT CURRENT_TIMESTAMP)')

    connection.commit()

    cur.execute('INSERT INTO history_table (user_text) VALUES (?)', (text_from_user,))
    connection.commit()

    connection.close()


def show_history():
    conn = sqlite3.connect('history.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM history_table;')
    all_db_data = cur.fetchall()

    conn.close()

    formatted_history = []
    for row in all_db_data:
        formatted_history.append(f'ID: {row[0]}, Query: {row[1]}, Date: {row[2]} ')

    return formatted_history


def show_todays_history():

    current_date = date.today()
    conn = sqlite3.connect('history.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM history_table WHERE DATE(date) = ?', (current_date,))
    result = cur.fetchall()

    conn.close()

    if result:
        return "\n".join([str(row) for row in result])
    else:
        return "No history for today"