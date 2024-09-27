# Логика уровней доступа и блокировок контента

def is_blocked(query: str, access_level: int) -> bool:
    blocked_topics_user = ["вредоносный код", "hack", "ddos", "exploit"]

    if access_level == 1:  # User
        for topic in blocked_topics_user:
            if topic in query.lower():
                return True
    return False
