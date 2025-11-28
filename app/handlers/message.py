from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from datetime import datetime

import app.database.requests as db_requests

import textwrap

router = Router()

@router.message(Command('message'))
async def handler_message(message: Message):
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

   try:
      today = datetime.now().date()

      date_str = today.strftime('%Y-%m-%d')

      file = FSInputFile(f'public/message/photo_message_{date_str}.jpg')

      await message.answer_photo(photo=file)
   except:
      await message.answer('Ой, послание затерялось... Обратись к Деду Морозу!')