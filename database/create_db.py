# Скрипт для создания базы данных (таблицы)

import sqlite3

def execute_query(query: str, parameters: tuple = ()):
    """
    Выполняет заданный SQL-запрос с параметрами и сохраняет изменения в базе данных.

    Args:
        query (str): SQL-запрос, который нужно выполнить.
        parameters (tuple, optional): Кортеж с параметрами для подстановки в запрос. 
            По умолчанию пустой кортеж.

    Returns:
        None

    Side Effects:
        Устанавливает соединение с базой данных `bot_database.db` для выполнения запроса и закрывает его после завершения.

    Example:
        >>> execute_query("INSERT INTO responses (question, answer) VALUES (?, ?)", ("Как погода?", "Солнечно"))
    """
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

