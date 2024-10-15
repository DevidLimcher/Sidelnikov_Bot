import sqlite3

# Определяем путь к текущему файлу (db_functions.py)
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_directory, 'bot_database.db')

# Функция для очистки всех вопросов и ответов
def clear_all_questions_answers():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Удаление всех записей из таблицы responses
    cursor.execute("DELETE FROM responses")
    
    # Также можно сбросить автоинкремент, если используется
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='responses'")
    
    conn.commit()
    conn.close()
    print("Все вопросы и ответы успешно удалены.")

clear_all_questions_answers()