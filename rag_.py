import faiss
import numpy as np
import sqlite3
import os
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Путь к базе данных
DB_PATH = "database/bot_database.db"
# Путь для сохранения индекса FAISS
INDEX_PATH = "faiss_index.index"
# Модель для генерации эмбеддингов
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

# Модель для генерации текста
GEN_MODEL_NAME = 'gpt2'
gen_model = GPT2LMHeadModel.from_pretrained(GEN_MODEL_NAME)
tokenizer = GPT2Tokenizer.from_pretrained(GEN_MODEL_NAME)

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Получение всех вопросов из базы данных
def get_all_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question FROM responses")  
    data = cursor.fetchall()
    conn.close()
    return data

# Функция для создания и сохранения индекса FAISS
def create_faiss_index():
    # Получаем все вопросы
    data = get_all_questions()
    if not data:
        return None
    
    # Генерация эмбеддингов для вопросов
    questions = [row[1] for row in data]
    embeddings = model.encode(questions, convert_to_numpy=True)

    # Создание индекса FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Сохранение индекса на диск
    faiss.write_index(index, INDEX_PATH)
    return index, [row[0] for row in data] 

# Функция для загрузки индекса FAISS
def load_faiss_index():
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        data = get_all_questions()
        return index, [row[0] for row in data]
    else:
        return create_faiss_index()

# Генерация ответа с использованием локальной языковой модели
def generate_response_with_gpt2(user_question):
    # Установить токен заполнителя
    tokenizer.pad_token = tokenizer.eos_token
    
    # Токенизация пользовательского вопроса с генерацией attention mask
    inputs = tokenizer("Give a simple explanation: " + user_question, return_tensors='pt', max_length=60, truncation=True, padding=True)
    
    # Входные данные и attention mask
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    # Генерация ответа с использованием дополнительных параметров
    outputs = gen_model.generate(
        input_ids, 
        attention_mask=attention_mask,
        max_length=80,          
        num_return_sequences=1, 
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=3,  
        temperature=0.3,         
        top_k=50,                
        top_p=0.85,              
        do_sample=True,          
        repetition_penalty=2.0  
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response


# Поиск наиболее похожего вопроса в базе данных
def find_similar_question(user_question):
    index, question_ids = load_faiss_index()
    if index is None:
        return "Индекс не загружен."

    # Генерация эмбеддинга для пользовательского вопроса
    user_embedding = model.encode([user_question], convert_to_numpy=True)
    
    # Поиск ближайшего соседа
    D, I = index.search(user_embedding, k=1)
    
    threshold = 0.5  # Порог схожести, можно уменьшить для повышения точности
    if D[0][0] < threshold:
        found_index = I[0][0]
        found_id = question_ids[found_index]
        # Далее выполняем поиск ответа по найденному ID
    else:
        # Если похожий вопрос не найден, генерируем ответ с использованием локальной модели
        return generate_response_with_gpt2(user_question)
    
    # Проверка записи по найденному ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM responses WHERE id = ?", (found_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        question, answer = result[1], result[2]
        return f"Похожий вопрос: {question}\nОтвет: {answer}"
    else:
        return f"Запись с ID {found_id} не найдена в базе данных."

def process_user_question(user_question):
    # Используем существующую функцию для поиска или генерации ответа
    return find_similar_question(user_question)

