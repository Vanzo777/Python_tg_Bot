import sqlite3 as sq
import uuid

import aiohttp

# import random - пока не надо, потребуется для поиска пользователей

async def db_start():
    global db, cur
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS profiles(
    user_id TEXT PRIMATY KEY, 
    username TEXT, 
    name TEXT, 
    age TEXT, 
    photo TEXT, 
    description TEXT
    )
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS events(
        event_id TEXT PRIMATY KEY, 
        event_name TEXT, 
        date_start TEXT, 
        date_end TEXT, 
        event_photo TEXT, 
        event_description TEXT, 
        event_url TEXT
        )
        """)
    db.commit()



async def db_end():
    cur.close()
    db.close()
    global session
    if session:
        await session.close()




async def create_profile(user_id, username):
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    user = cur.execute("SELECT 1 FROM profiles WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profiles VALUES(?, ?, ?, ?, ?,?)",(user_id, username, '', '', '', ''))
        db.commit()


async def create_event():
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    # Генерация уникального event_id с помощью UUID
    event_id = str(uuid.uuid4())
    # Проверяем, существует ли событие с таким event_id (теоретически не должно)
    event = cur.execute("SELECT 1 FROM events WHERE event_id = ?", (event_id,)).fetchone()
    if not event:
        # Вставляем новое событие в базу данных
        cur.execute("INSERT INTO events(event_id, event_name, date_start, date_end, event_photo, event_description, event_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (event_id, '', '', '', '', '',''))
        db.commit()
    cur.close()
    db.close()

    return event_id



async def edit_profile(state, user_id):
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    data = await state.get_data()
    cur.execute(
            "UPDATE profiles SET name = '{}', age = '{}', photo = '{}', description = '{}' WHERE user_id == '{}';".format(
                data.get('name'), data.get('age'), data.get('photo'), data.get('description'), user_id))
    db.commit()
    cur.close()

async def edit_event(state):
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    data = await state.get_data()
    cur.execute(
        "UPDATE events SET event_name='{}', date_start='{}', date_end='{}', event_photo='{}', event_description='{}', event_url = '{}' WHERE event_id=='{}';".format(
            data.get('event_name'), data.get('date_start'), data.get('date_end'), data.get('event_photo'), data.get('event_description'), data.get('event_url'), data.get('event_id')
        )
    )
    db.commit()
    cur.close()


async def get_profile(user_id):
    db = sq.connect('bot_database.db')
    cur = db.cursor()

    # Получаем профиль пользователя из базы данных
    cur.execute("SELECT name, age, photo, description FROM profiles WHERE user_id == ?", (user_id,))
    profile = cur.fetchone()

    cur.close()
    return profile



async def get_all_events():
    db = sq.connect('bot_database.db')
    cur = db.cursor()
    cur.execute("SELECT event_id, event_name FROM events WHERE event_name != ''")
    events = cur.fetchall()
    db.close()
    return events


async def delete_event_by_id(event_id: int):
    # Открываем соединение с базой данных
    db = sq.connect('bot_database.db')
    cur = db.cursor()

    # Выполняем запрос на удаление мероприятия
    cur.execute("DELETE FROM events WHERE event_id = ?", (event_id,))

    # Фиксируем изменения в базе данных
    db.commit()

    # Закрываем соединение
    db.close()



async def get_event_by_id(event_id):
    # Подключаемся к базе данных
    with sq.connect('bot_database.db') as db:
        cur = db.cursor()
        # Выполняем запрос для получения данных мероприятия по ID
        cur.execute("SELECT event_name, date_start, date_end, event_photo, event_description, event_url FROM events WHERE event_id=?", (event_id,))
        result = cur.fetchone()  # Получаем одну строку результата

    # Проверяем, что результат найден
    if result:
        # Возвращаем словарь с данными мероприятия
        return {
            'event_name': result[0],
            'date_start': result[1],
            'date_end': result[2],
            'event_photo': result[3],
            'event_description': result[4],
            'event_url': result[5],
        }
    else:
        return None

























####Если однажды нужно будет удалить таблицу
async def drop_table_if_exists(table_name):
    db = sq.connect('bot_database.db')
    cur = db.cursor()

    # Проверяем, существует ли таблица
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cur.fetchone()

    # Если таблица существует, удаляем её
    if result:
        cur.execute(f"DROP TABLE {table_name}")
        print(f"Таблица {table_name} удалена.")
    else:
        print(f"Таблица {table_name} не существует.")

    db.commit()
    db.close()


###Если нужно чистить таблицу

async def clear_table():
    db = sq.connect('bot_database.db')
    cur = db.cursor()

    # Очищаем записи, где event_name пустое
    cur.execute("DELETE FROM events WHERE event_name = '' OR event_name IS NULL")
    deleted_rows = cur.rowcount  # Получаем количество удаленных строк

    db.commit()
    db.close()

    print(f"Удалено записей с пустым event_name: {deleted_rows}")