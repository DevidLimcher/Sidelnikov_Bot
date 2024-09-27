from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import add_user_with_access, get_access_level

router = Router()

# Обработчик команды /set_access
@router.message(Command("set_access"))
async def set_access(message: Message):
    access_level = get_access_level(message.from_user.id)

    if access_level == 3:  # Только администратор может менять уровни доступа
        try:
            _, user_id, level = message.text.split()
            user_id = int(user_id)
            level_dict = {"user": 1, "premium": 2, "admin": 3}

            if level.lower() in level_dict:
                level = level_dict[level.lower()]
            else:
                level = int(level)

            if level not in [1, 2, 3]:
                await message.answer("Некорректный уровень доступа.")
                return

            add_user_with_access(user_id, level)
            level_names = {1: "user", 2: "premium", 3: "admin"}
            level_name = level_names.get(level)
            await message.answer(f"Уровень доступа пользователя {user_id} изменён на {level_name}.")
        except ValueError:
            await message.answer("Неверный формат команды.")
    else:
        await message.answer("У вас нет прав на изменение уровня доступа.")

