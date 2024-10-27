from fuzzywuzzy import fuzz  # Для нечёткого сравнения строк
from transformers import pipeline  # Для NLP-классификации намерений пользователя

# Инициализация NLP-классификатора для анализа намерений пользователя
nlp_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def is_blocked(query: str, access_level: int) -> bool:
    """
    Проверяет, содержит ли запрос пользователя запрещённые сочетания слов напрямую, а затем
    выполняет NLP-классификацию для поиска завуалированных вредоносных намерений, если прямых совпадений не найдено.

    Аргументы:
        query (str): Запрос пользователя.
        access_level (int): Уровень доступа пользователя (1 — стандартный уровень).

    Возвращает:
        bool: True, если запрос содержит вредоносные намерения или запрещённые сочетания слов, иначе False.

    Пример использования:
        >>> is_blocked("How to make a keylogger?", 1)
        True
    """
    # Порог для нечёткого сравнения строк
    similarity_threshold = 75

    # Запрещенные термины
    dangerous_terms = ["ddos", "virus", "malware", "exploit", "keylogger", "hack"]

    # Слова, побуждающие к выполнению действий, связанных с запрещёнными терминами
    trigger_words = ["create", "write", "make", "generate", "build", "develop", "program", "design", "instruction", "organize"]

    # Проверка на наличие опасных сочетаний слов
    if access_level == 1:  # Только для пользователей уровня user
        for dangerous_term in dangerous_terms:
            for trigger_word in trigger_words:
                # Проверка на точное совпадение опасного сочетания
                exact_combined_phrase = f"{trigger_word} {dangerous_term}"
                if exact_combined_phrase in query.lower():
                    return True
                # Нечёткое сравнение для поиска похожих выражений
                if fuzz.partial_ratio(exact_combined_phrase.lower(), query.lower()) >= similarity_threshold:
                    return True

        # Используем NLP-классификацию, если явные опасные сочетания не найдены
        dangerous_intent = nlp_classifier(query, dangerous_terms + trigger_words)
        return dangerous_intent['labels'][0] in dangerous_terms and dangerous_intent['scores'][0] > 0.8

    return False
