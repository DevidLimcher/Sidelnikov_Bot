# Скрипт для создания базы данных (таблицы)

import sqlite3

def execute_query(query: str, parameters: tuple = ()):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    conn.commit()
    conn.close()

# Создание таблицы вопросов и ответов
execute_query('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
''')

# Создание таблицы для хранения user_id и access_level
execute_query('''
    CREATE TABLE IF NOT EXISTS user_access (
        user_id INTEGER PRIMARY KEY,  -- Идентификатор пользователя
        access_level INTEGER NOT NULL  -- Уровень доступа (3 - админ, 2 - премиум, 1 - обычный пользователь)
    )
''')

