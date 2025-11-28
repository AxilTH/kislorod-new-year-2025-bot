from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

import app.database.requests as db_requests

import textwrap

router = Router()

@router.message(Command('help'))
async def handler_help(message: Message):
   is_user_registered = await db_requests.is_user_registered(message.from_user.id)

   if not is_user_registered:
      text = textwrap.dedent(
      '''
         Ты еще не зарегистрирован!

         Для регистрации введи команду /start
      '''
      )
      await message.answer(text)
      return

   text = textwrap.dedent(
   '''
      🎄 Волшебная книга заклинаний бота <b>"Кислород. Новый Год"</b>:

      /start — Начать новогоднее путешествие
      /message — Прочесть тайное зимнее послание ✨
      /task — Получить задание от Снеговика-помощника ⛄
      /events — Заглянуть в расписание волшебных встреч 🗓️
      /checkin — Оставить снежинку на странице мероприятия ❄️
      /profile — Открыть свой новогодний профиль 🎁
      /stats — Посмотреть гирлянду лидеров 🏆
      /help — Прочесть книгу заклинаний 🧝

      Выбери заклинание — и начнутся чудеса!
   ''')
   await message.answer(text, parse_mode='HTML')
