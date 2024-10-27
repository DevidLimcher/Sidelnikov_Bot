import faiss
import numpy as np
import os
from database.database import get_all_questions
from config import INDEX_PATH, MODEL_NAME
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(MODEL_NAME)

def create_faiss_index():
    """
    Создает индекс FAISS для поиска схожих вопросов и сохраняет его на диск.

    Returns:
        tuple: Кортеж, содержащий объект индекса FAISS и список идентификаторов вопросов 
        из базы данных, либо None, если данные отсутствуют.

    Side Effects:
        - Извлекает все вопросы из базы данных и создает эмбеддинги с помощью модели.
        - Инициализирует и наполняет индекс FAISS этими эмбеддингами.
        - Сохраняет созданный индекс на диск в путь, указанный в `INDEX_PATH`.

    Example:
        >>> index, question_ids = create_faiss_index()

    Usage:
        Используйте эту функцию для создания нового индекса FAISS, если его еще нет на диске.
    """
    data = get_all_questions()
    if not data:
        return None

    questions = [row[1] for row in data]
    embeddings = model.encode(questions, convert_to_numpy=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, INDEX_PATH)
    return index, [row[0] for row in data]


def load_faiss_index():
    """
    Загружает существующий индекс FAISS с диска или создает новый, если индекс отсутствует.

    Returns:
        tuple: Кортеж, содержащий объект индекса FAISS и список идентификаторов вопросов 
        из базы данных. Возвращает None, если данных для индекса нет.

    Side Effects:
        - Проверяет наличие файла индекса на диске по пути `INDEX_PATH`.
        - Если индекс существует, загружает его с диска; иначе вызывает `create_faiss_index` для его создания.

    Example:
        >>> index, question_ids = load_faiss_index()

    Usage:
        Используйте эту функцию для загрузки индекса FAISS, если он был ранее сохранен, 
        или для его создания в случае отсутствия.
    """
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        data = get_all_questions()
        return index, [row[0] for row in data]
    else:
        return create_faiss_index()

