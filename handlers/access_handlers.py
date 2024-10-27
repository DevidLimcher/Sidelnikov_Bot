from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import add_user_with_access, get_access_level

router = Router()

# Обработчик команды /set_access
@router.message(Command("set_access"))
async def set_access(message: Message):
    """
    Асинхронно устанавливает уровень доступа пользователя на основе команды администратора.

    Args:
        message (Message): Сообщение с командой, включающее идентификатор пользователя и новый уровень доступа.

    Returns:
        None

    Side Effects:
        - Получает текущий уровень доступа пользователя.
        - Если отправитель является администратором, извлекает `user_id` и `level` из текста команды и обновляет 
          уровень доступа для указанного пользователя в базе данных.
        - Отправляет ответное сообщение с подтверждением или ошибкой в зависимости от результата выполнения.

    Example:
        >>> set_access(message)
        Уровень доступа пользователя 12345 изменён на admin.
    
    Command Format:
        /set_access <user_id> <level>
        - <user_id> - идентификатор пользователя, чей уровень доступа нужно изменить.
        - <level> - новый уровень доступа, может быть "user", "premium" или "admin".

    Error Handling:
        - Выводит сообщение об ошибке, если:
          - Уровень доступа указан некорректно.
          - Команда не соответствует ожидаемому формату.
        - Если отправитель не является администратором, выводит сообщение об отсутствии прав.

    Usage:
        - Только пользователи с уровнем доступа `admin` могут изменять уровни доступа других пользователей.
        - Возможные уровни доступа:
            - 1: user
            - 2: premium
            - 3: admin
    """
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

