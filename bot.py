import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.handlers import router as questions_router
from handlers.access_handlers import router as access_router

# Создание бота
bot = Bot(token=BOT_TOKEN)

# Основная функция для запуска бота
async def main():
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
