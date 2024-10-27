import faiss
import numpy as np
import sqlite3
import os
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Путь к базе данных
DB_PATH = "database/bot_database.db"
# Путь для сохранения индекса FAISS
INDEX_PATH = "faiss_index.index"
# Модель для генерации эмбеддингов
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

# Загрузка модели LLaMA с квантованием
GEN_MODEL_NAME = 'meta-llama/Llama-3.2-1B'

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Загрузка модели с квантованием для оптимизации памяти
tokenizer = AutoTokenizer.from_pretrained(
    GEN_MODEL_NAME,
    trust_remote_code=True,
    padding_side="left",
    add_eos_token=True,
    add_bos_token=True,
    use_fast=False
)
tokenizer.pad_token = tokenizer.eos_token

gen_model = AutoModelForCausalLM.from_pretrained(
    GEN_MODEL_NAME, 
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
).to('cuda')

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

# Генерация ответа с использованием LLaMA на GPU
def generate_response_with_llama(user_question):
    # Токенизация пользовательского вопроса
    inputs = tokenizer("Write a clear answer for: " + user_question, return_tensors='pt', padding=True)
    
    # Входные данные на GPU
    input_ids = inputs['input_ids'].to('cuda')
    attention_mask = inputs['attention_mask'].to('cuda')

    # Генерация ответа с оптимизированными параметрами
    outputs = gen_model.generate(
        input_ids, 
        attention_mask=attention_mask,
        max_length=200,
        num_return_sequences=1, 
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=3,
        temperature=0.6,         
        top_k=50,                
        top_p=0.7,              
        do_sample=True,          
        repetition_penalty=1.1  
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
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
    
    threshold = 0.5  # Порог схожести
    if D[0][0] < threshold:
        found_index = I[0][0]
        found_id = question_ids[found_index]
        # Далее выполняем поиск ответа по найденному ID
    else:
        # Если похожий вопрос не найден, генерируем ответ с использованием локальной модели
        return generate_response_with_llama(user_question)
    
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
