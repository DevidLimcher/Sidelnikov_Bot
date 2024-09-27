# Логика работы с базой данных (SQLite)
import os
import sqlite3

# Определяем путь к текущему файлу (db_functions.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Определяем путь к базе данных в этой же папке
database_path = os.path.join(current_directory, 'bot_database.db')

# Функция для проверки существования вопроса в базе данных
def question_exists(question):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли вопрос в базе данных
    cursor.execute("SELECT 1 FROM responses WHERE question = ?", (question,))
    result = cursor.fetchone()
    
    conn.close()
    
    # Возвращаем True, если вопрос найден, иначе False
    return result is not None

def get_answer(query: str) -> str:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM responses WHERE question = ?", (query,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Ответ не найден."

def add_question_answer(question, answer):
    if question_exists(question):
        print(f"Вопрос '{question}' уже существует в базе данных.")
        return
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO responses (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

# Проверка уровня доступа пользователя
def get_access_level(user_id: int) -> int:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT access_level FROM user_access WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 1  # Возвращает уровень 1 (обычный пользователь), если не найдено

# Добавление пользователя с указанием уровня доступа
def add_user_with_access(user_id: int, access_level: int):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_access (user_id, access_level) VALUES (?, ?)", (user_id, access_level))
    conn.commit()
    conn.close()

# Удаление пользователя из таблицы
def remove_user(user_id: int):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_access WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

