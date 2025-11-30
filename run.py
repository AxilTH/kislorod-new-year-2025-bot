import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN, set_timezone
from app.handlers import router
from app.database.models import async_main

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
   await async_main() 
   set_timezone()
   bot = Bot(token=TOKEN)
   dp = Dispatcher()
   dp.include_router(router)
   await bot.set_my_commands(COMMANDS)
   await dp.start_polling(bot)

if __name__ == '__main__':
   try:
      asyncio.run(main())
   except KeyboardInterrupt:
      print('Exit')