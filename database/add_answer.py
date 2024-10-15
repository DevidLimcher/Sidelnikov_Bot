import csv
import sqlite3
from database import add_question_answer, question_exists

# Путь к базе данных
db_path = '/Users/davidlimcher/Desktop/Python/Sidelnikov_Bot/database/bot_database.db'

# Функция для проверки, существует ли вопрос в таблице
def question_exists(question):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM responses WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Чтение файлов CSV и добавление вопросов и ответов
file_paths = [
    "/Users/davidlimcher/Desktop/Python/Sidelnikov_Bot/database/Q_A_sets/Q_A_set_1.csv",
    "/Users/davidlimcher/Desktop/Python/Sidelnikov_Bot/database/Q_A_sets/Q_A_set_2.csv",
    "/Users/davidlimcher/Desktop/Python/Sidelnikov_Bot/database/Q_A_sets/Q_A_set_3.csv"
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
