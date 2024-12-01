from faiss_index import load_faiss_index
from llama_model import generate_response_with_llama, generate_code_response
from database.database import get_db_connection
from faiss_index import model
from fuzzywuzzy import fuzz

from fuzzywuzzy import fuzz

from transformers import pipeline

# Инициализируем модель для классификации запросов
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def is_code_request(query: str) -> bool:
    """
    Определяет, содержит ли запрос пользователя слова, указывающие на необходимость генерации кода,
    с помощью NLP-модели для классификации текста.

    Args:
        query (str): Вопрос пользователя.

    Returns:
        bool: True, если запрос связан с генерацией кода, иначе False.
    """
    # Определяем кандидаты для классификации
    labels = ["code request", "general question"]
    
    # Используем NLP-классификатор для определения, подходит ли запрос для генерации кода
    result = classifier(query, labels)
    
    # Если вероятность "code request" выше порога, то считаем это запросом на код
    return result['labels'][0] == "code request" and result['scores'][0] > 0.9




def find_similar_question(user_question):
    """
    Находит наиболее похожий вопрос в базе данных или генерирует новый ответ, если схожий вопрос не найден.

    Args:
        user_question (str): Вопрос пользователя, для которого требуется найти схожий вопрос или ответить.

    Returns:
        str: Либо ответ на похожий вопрос из базы данных, либо сгенерированный моделью ответ.

    Side Effects:
        - Загружает индекс FAISS для поиска схожих вопросов.
        - Генерирует эмбеддинг для пользовательского вопроса и ищет ближайший по схожести вопрос.
        - Если похожий вопрос найден, извлекает ответ из базы данных; в противном случае вызывает 
          `generate_response_with_llama` или `generate_code_response` для создания нового ответа.
    """
    index, question_ids = load_faiss_index()
    if index is None:
        return "Индекс не загружен."

    user_embedding = model.encode([user_question], convert_to_numpy=True)
    D, I = index.search(user_embedding, k=1)

    threshold = 0.5
    if D[0][0] < threshold:
        found_index = I[0][0]
        found_id = question_ids[found_index]
    else:
        # Если вопрос содержит запрос на код, используем генерацию кода
        if is_code_request(user_question):
            return generate_code_response(user_question)
        else:
            return generate_response_with_llama(user_question)

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
    """
    Обрабатывает запрос пользователя, используя функцию `find_similar_question` для поиска ответа.

    Args:
        user_question (str): Вопрос пользователя.

    Returns:
        str: Ответ, найденный в базе данных или сгенерированный моделью.

    Example:
        >>> process_user_question("Что такое квантовая физика?")
        "Квантовая физика - это раздел физики, изучающий поведение частиц на уровне атомов и субатомов."
    """
    return find_similar_question(user_question)
