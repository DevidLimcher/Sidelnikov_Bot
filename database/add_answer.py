import csv
import sqlite3
import sys
import os
from database import add_question_answer, question_exists

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH

# Определяем путь к текущему файлу (db_functions.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Определяем путь к базе данных в этой же папке
db_path = os.path.join(current_directory, 'bot_database.db')

# Функция для проверки, существует ли вопрос в таблице
def question_exists(question):
    """
    Проверяет, существует ли заданный вопрос в базе данных.

    Args:
        question (str): Вопрос, который нужно проверить на наличие в базе данных.

    Returns:
        bool: True, если вопрос уже существует в таблице `responses`, иначе False.

    Side Effects:
        Устанавливает соединение с базой данных для выполнения SQL-запроса и закрывает его после завершения.

    Example:
        >>> question_exists("Как погода сегодня?")
        True
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM responses WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# Чтение файлов CSV и добавление вопросов и ответов
file_paths = [
    "/home/davidlimcher/projects/Sidelnikov_Bot/database/Q_A_sets/Q_A_set_3.csv"
]

for file_path in file_paths:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['Question'].strip()
            answer = row['Answer'].strip()

            if not question_exists(question):
                add_question_answer(question, answer)
                print(f"Вопрос и ответ добавлены: {question}")
            else:
                print(f"Вопрос уже существует: {question}")

print("Вопросы и ответы успешно добавлены в базу данных.")
