# Файл с конфигурацией бота (токен и уровни доступа)

BOT_TOKEN = "7728568712:AAHlw70_94-MGSOHmO4Nb3G5mmPIXLEx-4I"

# Определение уровней доступа
ACCESS_LEVELS = {
    "admin": 3,   # Административный доступ
    "premium": 2, # Платный доступ
    "user": 1     # Уровень доступа для остальных
}

DB_PATH = "database/bot_database.db"
INDEX_PATH = "faiss_index.index"
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
GEN_MODEL_NAME = 'meta-llama/Llama-3.2-1B'
