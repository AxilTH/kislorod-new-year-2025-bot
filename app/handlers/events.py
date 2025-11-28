from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

import app.database.requests as db_requests

import textwrap

router = Router()

@router.message(Command('events'))
async def handler_events(message: Message):
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

   file = FSInputFile('public/schedule/photo_schedule_2025-12.jpg')
   await message.answer_photo(photo=file)