import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
print("DEBUG: DB_NAME =", os.getenv("DB_NAME"))
print("DEBUG: DB_USER =", os.getenv("DB_USER"))
print("DEBUG: DB_PASSWORD =", os.getenv("DB_PASSWORD"))
print("DEBUG: DB_HOST =", os.getenv("DB_HOST"))
print("DEBUG: DB_PORT =", os.getenv("DB_PORT"))
def get_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', 5432)
        )
        return connection
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


conn = get_connection()
if conn:
    print("conn")
    conn.close()

def create_table_convertations():
    connection = get_connection()
    if connection is None:
        print("Нет подключения к БД!")
        return
    cursor = connection.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS convertations (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            register_date TEXT,
            status TEXT
        )'''
    )
    connection.commit()
    connection.close()

def add_convertation(telegram_id, status):
    connection = get_connection()
    if connection is None:
        print("Нет подключения к БД!")
        return
    cursor = connection.cursor()
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    cursor.execute('''
        INSERT INTO convertations (telegram_id, register_date, status)
        VALUES (%s, %s, %s)
    ''', (telegram_id, dt_string, status))
    connection.commit()
    connection.close()

def get_convertations():
    connection = get_connection()
    if connection is None:
        return "Ошибка подключения к БД."
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM convertations')
    data = cursor.fetchall()
    connection.close()
    info = ''
    for i in data:
        info += f'data: {i}\n'
    return info

def create_table_users():
    connection = get_connection()
    if connection is None:
        print("Нет подключения к БД!")
        return
    cursor = connection.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            username TEXT,
            register_date TEXT
        )'''
    )
    connection.commit()
    connection.close()

def add_user(telegram_id, username):
    connection = get_connection()
    if connection is None:
        print("Нет подключения к БД!")
        return
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    data = cursor.fetchone()
    if data is not None:
        connection.close()
        return
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    cursor.execute('''
        INSERT INTO users (telegram_id, username, register_date)
        VALUES (%s, %s, %s)
    ''', (telegram_id, username, dt_string))
    connection.commit()
    connection.close()

def get_users():
    connection = get_connection()
    if connection is None:
        return "Ошибка подключения к БД."
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    connection.close()
    info = ''
    for i in data:
        info += f'data: {i}\n'
    return info
