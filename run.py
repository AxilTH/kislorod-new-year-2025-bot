import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN, set_timezone
from app.handlers import router
from app.database.models import async_main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

COMMANDS = [
   BotCommand(command="/start", description="Начать регистрацию в боте"),
   BotCommand(command="/message", description="Получить новое послание"),
   BotCommand(command="/task", description="Получить новое задание"),
   BotCommand(command="/events", description="Посмотреть расписание мероприятий"),
   BotCommand(command="/checkin", description="Отметиться на мероприятии"),
   BotCommand(command="/profile", description="Посмотреть информацию о своем профиле"),
   BotCommand(command="/stats", description="Посмотреть рейтинг участников"),
   BotCommand(command="/help", description="Показать список доступных команд")
]

async def main():
   try:
      logger.info("Initializing database...")
      await async_main()
      logger.info("Database initialized successfully")
   except Exception as e:
      logger.critical("Failed to initialize database: %s", e, exc_info=True)
      sys.exit(1)
   
   set_timezone()
   
   if not TOKEN:
      logger.critical("TOKEN is not set!")
      sys.exit(1)
   
   bot = Bot(token=TOKEN)
   dp = Dispatcher()
   dp.include_router(router)
   await bot.set_my_commands(COMMANDS)
   logger.info("Bot started successfully")
   
   try:
      await dp.start_polling(bot)
   finally:
      # Закрытие соединений с БД при остановке бота
      from app.database.models import engine
      logger.info("Closing database connections...")
      await engine.dispose()
      logger.info("Database connections closed")

if __name__ == '__main__':
   try:
      asyncio.run(main())
   except KeyboardInterrupt:
      logger.info('Bot stopped by user')
   except Exception as e:
      logger.critical("Fatal error: %s", e, exc_info=True)
      sys.exit(1)