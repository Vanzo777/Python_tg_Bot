from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import API_TOKEN
from database.database import db_start, drop_table_if_exists, db_end
from aiogram import Bot, Dispatcher
import asyncio

from handlers import user_handlers, other_handlers, admin_handlers
from keyboards.set_menu import set_main_menu


async def main():
    # Создаем бота
    bot = Bot(token=API_TOKEN)

    # Создаем диспетчер
    dp = Dispatcher()

    # Устанавливаем главное меню
    await set_main_menu(bot)
    await drop_table_if_exists('profiles')
    # await db_start()
    # Регистрация роутеров (добавьте ваши роутеры здесь)
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(other_handlers.router)
    # Удаляем вебхук (если есть)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling
    try:
        await dp.start_polling(bot, on_startup=db_start, on_shutdown=db_end)
    finally:
        await bot.session.close()  # Закрываем сессию


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")

