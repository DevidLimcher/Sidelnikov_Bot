import sqlite3

# Путь к базе данных
db_path = 'bot_database.db'

# Добавление пользователя с уровнем доступа 3 (администратор)
def add_admin(user_id: int):
    """
    Добавляет пользователя с указанным `user_id` в базу данных как администратора, 
    устанавливая уровень доступа 3.

    Args:
        user_id (int): Идентификатор пользователя, которого нужно назначить администратором.

    Returns:
        None

    Side Effects:
        Добавляет запись в таблицу `user_access` в базе данных, устанавливая для пользователя 
        с данным `user_id` уровень доступа 3. Закрывает подключение к базе данных после выполнения.

    Example:
        >>> add_admin(12345)
        Пользователь с user_id 12345 добавлен как администратор.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL-запрос для добавления администратора
    cursor.execute("INSERT OR REPLACE INTO user_access (user_id, access_level) VALUES (?, ?)", (user_id, 3))
    
    conn.commit()
    conn.close()
    print(f"Пользователь с user_id {user_id} добавлен как администратор.")


# Добавления администратора
add_admin(993242836) 
