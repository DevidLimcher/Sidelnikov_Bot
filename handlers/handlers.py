# Файл с обработчиками сообщений
from database.database import get_access_level
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import get_answer, add_question_answer
from access_levels import is_blocked
import sys
import os
from rag_ import process_user_question 

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def start(message: Message):
    """
    Асинхронный обработчик команды /start, отправляющий приветственное сообщение 
    в зависимости от уровня доступа пользователя.

    Args:
        message (Message): Сообщение, содержащее команду /start от пользователя.

    Returns:
        None

    Side Effects:
        - Получает уровень доступа пользователя.
        - Отправляет приветственное сообщение, соответствующее уровню доступа: 
          "администратор", "премиум пользователь" или "обычный пользователь".

    Example:
        >>> /start
        Привет, администратор!
    """
    access_level = get_access_level(message.from_user.id)
    
    if access_level == 3:
        await message.answer("Привет, администратор!")
    elif access_level == 2:
        await message.answer("Привет, премиум пользователь!")
    else:
        await message.answer("Привет! Задавай вопросы, и я постараюсь ответить.")


@router.message(Command("id"))
async def send_user_id(message: Message):
    """
    Асинхронный обработчик команды /id, который отправляет пользователю его идентификатор (user_id).

    Args:
        message (Message): Сообщение, содержащее команду /id от пользователя.

    Returns:
        None

    Side Effects:
        Отправляет сообщение с `user_id` пользователя.

    Example:
        >>> /id
        Ваш user_id: 123456789
    """
    user_id = message.from_user.id
    await message.answer(f"Ваш user_id: {user_id}")


# Обработчик команды /add_question для добавления вопроса и ответа
@router.message(Command("add_question"))
async def add_question(message: Message):
    """
    Асинхронный обработчик команды /add_question для добавления нового вопроса и ответа 
    в базу данных. Доступен только администраторам.

    Args:
        message (Message): Сообщение, содержащее команду /add_question от пользователя.

    Returns:
        None

    Side Effects:
        - Проверяет уровень доступа пользователя.
        - Добавляет новый вопрос и ответ в базу данных, если команда имеет корректный формат.
        - Отправляет сообщение с подтверждением или ошибкой в зависимости от результата выполнения.

    Command Format:
        /add_question <вопрос> | <ответ>

    Example:
        >>> /add_question Какой сегодня день? | Сегодня понедельник
        Вопрос и ответ успешно добавлены.
    """
    # Проверяем, является ли пользователь администратором
    if get_access_level(message.from_user.id) == 3:
        try:
            # Формат команды: /add_question вопрос | ответ
            question, answer = message.text[len("/add_question "):].split('|')
            
            # Добавляем вопрос и ответ в базу данных
            add_question_answer(question.strip(), answer.strip())
            
            await message.answer("Вопрос и ответ успешно добавлены.")
        except ValueError:
            await message.answer("Ошибка: Неправильный формат. Используйте /add_question вопрос | ответ")
    else:
        await message.answer("У вас нет прав на добавление вопросов.")


# Обработчик для всех остальных сообщений
@router.message()
async def handle_message(message: Message):
    """
    Асинхронный обработчик для всех текстовых сообщений, кроме команд. Функция обрабатывает запрос 
    пользователя, проверяет его на соответствие разрешённым темам и доступность в базе данных.

    Args:
        message (Message): Сообщение от пользователя с текстовым запросом.

    Returns:
        None

    Side Effects:
        - Проверяет уровень доступа пользователя и текст сообщения на наличие запрещённых тем.
        - При наличии запрещённых тем отправляет сообщение об отказе в ответе.
        - Если текст превышает лимит длины сообщения Telegram (4096 символов), разбивает его на части и отправляет поэтапно.

    Пример использования:
        >>> Запрос: "Напишите мне программу на Python для сортировки массива"
        Ответ: Часть 1: "def sort_array(arr):\n..."
        Часть 2: "... return arr"

    Алгоритм:
        - Проверка на запрещённые темы с учётом уровня доступа пользователя.
        - Запрос передаётся в `process_user_question` для поиска ответа в базе данных или генерации нового.
        - Если длина ответа превышает максимальную длину сообщения Telegram (4096 символов), текст разбивается на части.
    """
    query = message.text
    access_level = get_access_level(message.from_user.id)

    # Проверка на запрещённые темы или уровни доступа
    if is_blocked(query, access_level):
        await message.answer("Я не могу предоставить вам данную информацию.")
    else:
        # Получаем ответ от process_user_question
        response_text = process_user_question(query)

        # Максимальная длина сообщения Telegram
        max_length = 4096
        # Если ответ длинный, разбиваем его на части
        if len(response_text) > max_length:
            parts = [response_text[i:i + max_length] for i in range(0, len(response_text), max_length)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(response_text)


