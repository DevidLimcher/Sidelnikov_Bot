import scann
import numpy as np
import sqlite3
import os
from sentence_transformers import SentenceTransformer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tensorflow as tf

# Путь к базе данных
DB_PATH = "database/bot_database.db"
# Путь для сохранения индекса ScaNN
INDEX_PATH = "scann_index"
# Модель для генерации эмбеддингов
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# Настройки TensorFlow для использования только CPU
tf.config.set_visible_devices([], 'GPU')

# Загрузка модели SentenceTransformer и указание работы на CPU
model = SentenceTransformer(MODEL_NAME, device='cpu')

# Загрузка GPT-2 модели и перевод её на CPU
gpt_model_name = 'distilgpt2'
gpt_model = GPT2LMHeadModel.from_pretrained(gpt_model_name)
gpt_tokenizer = GPT2Tokenizer.from_pretrained(gpt_model_name)
gpt_model.to('cpu')

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

import os

# Функция для создания и сохранения индекса ScaNN
def create_scann_index():
    # Создаем директорию, если её нет
    if not os.path.exists(INDEX_PATH):
        os.makedirs(INDEX_PATH)
    
    # Получаем все вопросы
    data = get_all_questions()
    if not data:
        return None
    
    # Генерация эмбеддингов для вопросов
    questions = [row[1] for row in data]
    embeddings = model.encode(questions, convert_to_numpy=True)

    # Оптимизированное создание и настройка индекса ScaNN
    searcher = scann.scann_ops_pybind.builder(embeddings, 10, "dot_product").tree(
        num_leaves=100, num_leaves_to_search=10, training_sample_size=250000).score_ah(
        2, anisotropic_quantization_threshold=0.2).reorder(100).build()
    
    # Сохранение индекса на диск
    searcher.serialize(INDEX_PATH)
    return searcher, [row[0] for row in data]



# Функция для загрузки индекса ScaNN
def load_scann_index():
    if os.path.exists(INDEX_PATH):
        searcher = scann.scann_ops_pybind.load_searcher(INDEX_PATH)
        data = get_all_questions()
        return searcher, [row[0] for row in data]
    else:
        return create_scann_index()

# Генерация ответа с помощью GPT-2
def generate_answer(prompt):
    inputs = gpt_tokenizer.encode(prompt, return_tensors='pt')
    outputs = gpt_model.generate(inputs, max_length=150, num_return_sequences=1)
    return gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)

# Поиск наиболее похожего вопроса в базе данных
def find_similar_question(user_question):
    searcher, question_ids = load_scann_index()
    if searcher is None:
        return "Индекс не загружен."

    # Генерация эмбеддинга для пользовательского вопроса
    user_embedding = model.encode([user_question], convert_to_numpy=True)
    
    # Поиск ближайшего соседа
    neighbors, distances = searcher.search_batched(user_embedding)
    
    threshold = 0.5  # Порог схожести
    if distances[0][0] < threshold:
        found_index = neighbors[0][0]
        found_id = question_ids[found_index]
        
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
            # Если точного ответа нет, генерируем его
            generated_answer = generate_answer(user_question)
            return f"Ответ не найден в базе данных. Сгенерированный ответ: {generated_answer}"
    else:
        # Если похожий вопрос не найден, генерируем ответ
        generated_answer = generate_answer(user_question)
        return f"Похожий вопрос не найден. Сгенерированный ответ: {generated_answer}"

# Пример использования
user_input = input("Введите вопрос: ")
response = find_similar_question(user_input)
print(response)
