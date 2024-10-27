# Логика уровней доступа и блокировок контента
def is_blocked(query: str, access_level: int) -> bool:
    """
    Проверяет, содержит ли запрос пользователя запрещенные темы на основе уровня доступа.

    Args:
        query (str): Текст запроса пользователя.
        access_level (int): Уровень доступа пользователя (1 — обычный пользователь).

    Returns:
        bool: True, если запрос содержит запрещенные темы и уровень доступа пользователя — `user`, иначе False.

    Side Effects:
        None

    Example:
        >>> is_blocked("Как сделать ddos-атаку?", 1)
        True

    Usage:
        - Функция проверяет запросы только для пользователей с уровнем доступа `1` (user).
        - Запрещенные темы включают термины, связанные с вредоносной активностью, такие как "hack" и "ddos".
    """
    blocked_topics_user = ["вредоносный код", "hack", "ddos", "exploit"]

    if access_level == 1:  # User
        for topic in blocked_topics_user:
            if topic in query.lower():
                return True
    return False
