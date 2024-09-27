from database import add_question_answer

questions_and_answers = [
    ("Что такое шифрование данных?", "Шифрование данных — это процесс преобразования информации в форму, недоступную для несанкционированного доступа, с помощью специальных алгоритмов и ключей."),
    ("Какие виды атак на информационные системы существуют?", "Существуют различные виды атак, такие как фишинг, DDoS-атаки, атаки с использованием вредоносного ПО, SQL-инъекции и атаки с перехватом данных."),
    ("Что такое брандмауэр (Firewall)?", "Брандмауэр — это программное или аппаратное средство, которое контролирует и фильтрует сетевой трафик, позволяя или блокируя его на основе заданных правил безопасности."),
    ("Что такое многофакторная аутентификация (MFA)?", "Многофакторная аутентификация (MFA) — это метод защиты, при котором для входа в систему требуется предоставить несколько форм подтверждения личности, таких как пароль и код из SMS."),
    ("Как защитить Wi-Fi сеть?", "Для защиты Wi-Fi сети необходимо использовать шифрование WPA2 или WPA3, задавать сложный пароль, отключать WPS и регулярно обновлять прошивку роутера.")
]

# Добавляем все вопросы и ответы в базу данных
for question, answer in questions_and_answers:
    add_question_answer(question, answer)

print("Вопросы и ответы успешно добавлены в базу данных.")