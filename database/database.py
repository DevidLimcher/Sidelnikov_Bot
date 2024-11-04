# Логика работы с базой данных (SQLite)
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH

# Определяем путь к текущему файлу (db_functions.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Определяем путь к базе данных в этой же папке
database_path = os.path.join(current_directory, 'bot_database.db')

# Функция для проверки существования вопроса в базе данных
def question_exists(question):
    """
    Проверяет, существует ли заданный вопрос в базе данных.

    Args:
        question (str): Вопрос, который необходимо проверить на наличие в базе данных.

    Returns:
        bool: True, если вопрос найден в таблице `responses`, иначе False.

    Side Effects:
        Устанавливает соединение с базой данных и закрывает его после завершения операции.

    Example:
        >>> question_exists("Какой сегодня день?")
        True
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли вопрос в базе данных
    cursor.execute("SELECT 1 FROM responses WHERE question = ?", (question,))
    result = cursor.fetchone()
    
    conn.close()
    
    # Возвращаем True, если вопрос найден, иначе False
    return result is not None


def get_answer(query: str) -> str:
    """
    Извлекает ответ на заданный вопрос из базы данных.

    Args:
        query (str): Вопрос, для которого требуется получить ответ.

    Returns:
        str: Ответ из таблицы `responses`, если вопрос найден, иначе "Ответ не найден".

    Side Effects:
        Устанавливает соединение с базой данных для выполнения SQL-запроса и закрывает его после завершения.

    Example:
        >>> get_answer("Как погода?")
        "Солнечно"
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM responses WHERE question = ?", (query,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Ответ не найден."


def add_question_answer(question, answer):
    """
    Добавляет вопрос и ответ в базу данных, если такого вопроса еще нет.

    Args:
        question (str): Вопрос, который необходимо добавить.
        answer (str): Ответ на вопрос, который будет сохранен в базе данных.

    Returns:
        None

    Side Effects:
        Проверяет, существует ли уже вопрос в базе данных, и добавляет новую запись, если вопрос отсутствует.
        Закрывает соединение с базой данных после завершения операции.

    Example:
        >>> add_question_answer("Как погода?", "Солнечно")
    """
    if question_exists(question):
        print(f"Вопрос '{question}' уже существует в базе данных.")
        return
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO responses (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()


def get_access_level(user_id: int) -> int:
    """
    Проверяет уровень доступа пользователя по его `user_id`.

    Args:
        user_id (int): Идентификатор пользователя для проверки уровня доступа.

    Returns:
        int: Уровень доступа пользователя, если найден, иначе возвращает 1 (обычный пользователь).

    Side Effects:
        Устанавливает соединение с базой данных для выполнения SQL-запроса и закрывает его после завершения.

    Example:
        >>> get_access_level(12345)
        3
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT access_level FROM user_access WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 1


def add_user_with_access(user_id: int, access_level: int):
    """
    Добавляет пользователя с указанным уровнем доступа в базу данных.

    Args:
        user_id (int): Идентификатор пользователя.
        access_level (int): Уровень доступа пользователя.

    Returns:
        None

    Side Effects:
        Добавляет или обновляет запись в таблице `user_access` для указанного пользователя
        с данным уровнем доступа. Закрывает соединение с базой данных после завершения.

    Example:
        >>> add_user_with_access(12345, 2)
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_access (user_id, access_level) VALUES (?, ?)", (user_id, access_level))
    conn.commit()
    conn.close()


def remove_user(user_id: int):
    """
    Удаляет пользователя из таблицы `user_access` по его `user_id`.

    Args:
        user_id (int): Идентификатор пользователя, которого нужно удалить.

    Returns:
        None

    Side Effects:
        Удаляет запись о пользователе из базы данных, если она существует.
        Закрывает соединение с базой данных после завершения.

    Example:
        >>> remove_user(12345)
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_access WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_db_connection():
    """
    Устанавливает и возвращает соединение с базой данных.

    Returns:
        sqlite3.Connection: Объект соединения с базой данных `DB_PATH`.

    Example:
        >>> conn = get_db_connection()
    """
    conn = sqlite3.connect(DB_PATH)
    return conn


def get_all_questions():
    """
    Извлекает все вопросы из базы данных.

    Returns:
        list: Список кортежей с id и текстом вопросов из таблицы `responses`.

    Side Effects:
        Устанавливает соединение с базой данных для выполнения запроса и закрывает его после завершения.

    Example:
        >>> get_all_questions()
        [(1, "Как погода?"), (2, "Сколько времени?")]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question FROM responses")
    data = cursor.fetchall()
    conn.close()
    return data
