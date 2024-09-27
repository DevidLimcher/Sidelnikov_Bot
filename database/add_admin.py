import sqlite3

# Путь к базе данных
db_path = 'bot_database.db'

# Добавление пользователя с уровнем доступа 3 (администратор)
def add_admin(user_id: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL-запрос для добавления администратора
    cursor.execute("INSERT OR REPLACE INTO user_access (user_id, access_level) VALUES (?, ?)", (user_id, 3))
    
    conn.commit()
    conn.close()
    print(f"Пользователь с user_id {user_id} добавлен как администратор.")

# Добавления администратора
add_admin(993242836) 
