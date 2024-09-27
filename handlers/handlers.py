# Файл с обработчиками сообщений
from database.database import get_access_level
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import get_answer, add_question_answer
from access_levels import is_blocked

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def start(message: Message):
    access_level = get_access_level(message.from_user.id)
    
    if access_level == 3:
        await message.answer("Привет, администратор!")
    elif access_level == 2:
        await message.answer("Привет, премиум пользователь!")
    else:
        await message.answer("Привет! Задавай вопросы, и я постараюсь ответить.")

@router.message(Command("id"))
async def send_user_id(message: Message):
    user_id = message.from_user.id
    await message.answer(f"Ваш user_id: {user_id}")

# Обработчик команды /add_question для добавления вопроса и ответа
@router.message(Command("add_question"))
async def add_question(message: Message):
    # Проверяем, является ли пользователь администратором
    if get_access_level(message.from_user.id) == 3:
        try:
            # Формат команды: /add_question вопрос | ответ
            # Разделяем текст команды на вопрос и ответ
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
    query = message.text

    access_level = get_access_level(message.from_user.id)

    if is_blocked(query, access_level):
        await message.answer("Я не могу предоставить вам данную информацию.")
    else:
        answer = get_answer(query)
        await message.answer(answer)
        