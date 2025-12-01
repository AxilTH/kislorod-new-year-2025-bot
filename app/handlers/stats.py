from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.helpers.snowflake_helper import get_snowflakes_word

import app.database.requests as db_requests

import textwrap

router = Router()

@router.message(Command('stats'))
async def handler_stats(message: Message):
   try:
      is_user_registered = await db_requests.is_user_registered(message.from_user.id)
   except Exception as e:
      import logging
      logging.getLogger(__name__).error("Database error in stats handler: %s", e, exc_info=True)
      await message.answer("❌ Произошла ошибка при обращении к базе данных. Попробуйте позже.")
      return

   if not is_user_registered:
      text = textwrap.dedent(
      '''
         Ты еще не зарегистрирован!

         Для регистрации введи команду /start
      '''
      )
      await message.answer(text)
      return
   
   users = (await db_requests.get_all_users())
   sorted_users = sorted(users, key=lambda user: user.score, reverse=True)

   # Определяем эмодзи для первых трех мест
   medals = {
      0: '🥇',
      1: '🥈', 
      2: '🥉'
   }

   # Формируем текст топа
   top_lines = []
   for i, user in enumerate(sorted_users):
      # Формируем полное имя
      full_name = f"{user.first_name} {user.last_name}".strip()
      
      # Добавляем эмодзи для первых трех мест, для остальных - номер
      if i in medals:
         prefix = f"{medals[i]} {full_name}"
      else:
         prefix = f"{i+1}. {full_name}"
      
      score = user.score
      
      line = f"{prefix} — {score} {get_snowflakes_word(score)}"
      top_lines.append(line)

   # Объединяем все строки
   top_text = "\n".join(top_lines)

   # Собираем итоговый текст без лишних отступов
   header = "🏆 ТОП-10 УЧАСТНИКОВ\n\n"
   text = f"{header}{top_text}"

   await message.answer(text, parse_mode='HTML')