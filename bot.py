import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.handlers import router as questions_router
from handlers.access_handlers import router as access_router

# Создание бота
bot = Bot(token=BOT_TOKEN)

async def main():
    """
    Основная асинхронная функция для запуска бота.

    Returns:
        None

    Side Effects:
        - Создает экземпляр `Dispatcher` для управления маршрутизацией команд.
        - Регистрирует `access_router` и `questions_router` для обработки команд, 
          связанных с уровнями доступа и вопросами.
        - Запускает бот в режиме долгосрочного опроса (polling), позволяя ему обрабатывать входящие сообщения.
        - Закрывает сессию бота при завершении работы.

    Example:
        >>> asyncio.run(main())

    Usage:
        Функция `main` должна быть вызвана в асинхронном контексте с использованием `asyncio.run(main())`.
    """
    dp = Dispatcher()

    # Регистрируем роутеры с командами
    dp.include_router(access_router)
    dp.include_router(questions_router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
