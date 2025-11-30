from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from datetime import datetime

from app.database.models import Task
from app.database.requests import (
   is_user_registered,
   get_task_by_id,
   get_current_task, 
   mark_task_completed, 
   update_user_score,
   get_tasks_status
)

import textwrap

router = Router()

@router.message(Command("task"))
async def handler_task(message: Message):
   is_user_registered_ = await is_user_registered(message.from_user.id)

   if not is_user_registered_:
      text = textwrap.dedent(
      '''
         Ты еще не зарегистрирован!

         Для регистрации введи команду /start
      '''
      )
      await message.answer(text)
      return


   user_id = message.from_user.id
   today = datetime.now().date()
   
   tasks_status = await get_tasks_status(user_id, today)
    
   if not tasks_status:
      await message.answer("На сегодня заданий нет!")
      return
    
   all_completed = all(status['completed'] for status in tasks_status.values())
   if all_completed:
      await message.answer("🎉 Поздравляем! Вы выполнили все задания на сегодня!")
      return
    
   current_task = await get_current_task(user_id, today)
   if current_task:
      await send_task_message(message, current_task)
   else:
      await message.answer("❌ Ошибка: не удалось найти текущее задание")

async def send_task_message(message: Message, task: Task):
   if task.type == 'TF':
      from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
      
      keyboard = InlineKeyboardMarkup(
         inline_keyboard=[
               [
                  InlineKeyboardButton(text="✅ Правда", callback_data=f"tf_{task.id}_True"),
                  InlineKeyboardButton(text="❌ Ложь", callback_data=f"tf_{task.id}_False")
               ]
         ]
      )
        
      await message.answer(textwrap.dedent(f'''
         1️⃣ Задание 1/3: <b>Новый год в разных странах</b>. Правда vs Ложь
                                           
         {task.description}

         Выберите правильный ответ:
      '''), parse_mode='HTML', reply_markup=keyboard)
        
   elif task.type == 'AI':
      try:
         today = datetime.now().date()

         date_str = today.strftime('%Y-%m-%d')

         file = FSInputFile(f'public/ai_images/photo_ai_image_{date_str}.jpg')
         
         await message.answer_photo(photo=file, caption=textwrap.dedent(f'''
            2️⃣ Задание 2/3: <b>Напишите название новогоднего фильма/мультфильма</b>, к которому представлена эта ИИ-афиша. 
                                                                        
            Пишите ответ без кавычек и с большой буквы. 
            Например: Кислород.
                                                                        
            ✨ Название пишем полностью, как в оригинальном названии фильма;
            ✨ Буквы «Е» и «Ё» равноправны и не влияют на ответ; 
            ✨ Если в названии есть имена собственные, пишем их с большой буквы; 
            ✨ Если это серия фильмов, то давать указание на часть не нужно: 

            ✅ Чебурашка 
            ❌ Чебурашка 2
            
            🎬 Напишите название фильма в ответном сообщении.
         '''), parse_mode='HTML')
      except:
         await message.answer('Ой, задание 2️⃣ затерялось... Обратись к Деду Морозу!')
        
   elif task.type == 'DISH':
      try:
         today = datetime.now().date()
         date_str = today.strftime('%Y-%m-%d')
         file = FSInputFile(f'public/dish_images/photo_dish_image_{date_str}.jpg')

         description_part = f"\nОписание: {task.description}\n" if task.description else ""

         await message.answer_photo(photo=file, caption=
            f'3️⃣ Задание 3/3: <b>Угадай название салата на праздничный стол</b> 🥗\n'
            f'{description_part}\n'
            f'✨ Если вы не знаете, что это за салат, придумайте ему своё оригинальное название\n'
            f'✨ Баллы за это задание начисляются всем!\n' 
            f'✨ Креативьте друзья, давайте посмеёмся 🤗',
         parse_mode='HTML')
      except:
         await message.answer('Ой, задание 3️⃣ затерялось... Обратись к Деду Морозу!')

@router.callback_query(F.data.startswith("tf_"))
async def handle_tf_answer(callback: CallbackQuery):
   user_id = callback.from_user.id
   _, task_id, answer = callback.data.split("_")
   task_id = int(task_id)
   today = datetime.now().date()
    
   task = await get_task_by_id(task_id)

   if not task:
      await callback.answer("Задание не найдено!", show_alert=True)
      return
    
   is_correct = (answer == task.correct_answer)
   points = task.score if is_correct else 0
    
   success = await mark_task_completed(user_id, task_id, points, answer)
    
   if success and points > 0:
      await update_user_score(user_id, points)
    
   result_text = (
      f"✅ Правильно! Было зачислено +{points} баллов!\n" 
         if is_correct else
      f"❌ Неправильно. Правильный ответ: {
         'Правда' if task.correct_answer == 'True' else 'Ложь'
      }"
   )
    
   await callback.message.edit_text(
      f"{callback.message.text}\n\n{result_text}"
   )
   
   next_task = await get_current_task(user_id, today)
   
   if next_task:
      await send_task_message(callback.message, next_task)
   else:
      await callback.message.answer("🎉 Поздравляем! Вы выполнили все задания на сегодня!")

@router.message(F.text)
async def handle_text_answer(message: Message):
   user_id = message.from_user.id
   today = datetime.now().date()
   user_answer = message.text.strip().translate(str.maketrans('ёЁ—', 'еЕ-'))
    
   current_task = await get_current_task(user_id, today)
    
   if not current_task or current_task.type not in ['AI', 'DISH']:
      return
    
   task = current_task
    
   if task.type == 'AI':
      normalized_task_answer = task.correct_answer.strip().translate(str.maketrans('ёЁ—', 'еЕ-'))
      is_correct = (user_answer.lower() == normalized_task_answer.lower())
      points = task.score if is_correct else 0
      
      result_text = (
         f"✅ Правильно! Было зачислено +{points} баллов!\n" 
         if is_correct else
         f"❌ Неправильно. Правильный ответ: {task.correct_answer}"
      )
        
   elif task.type == 'DISH':
      points = task.score
      result_text = f"✅ Хм... Интересное название для салата. Ответ принят! Было зачислено +{points} баллов"

   success = await mark_task_completed(user_id, task.id, points, user_answer)
   
   if success and points > 0:
      await update_user_score(user_id, points)
    
   await message.answer(result_text)
    
   next_task = await get_current_task(user_id, today)
    
   if next_task:
      await send_task_message(message, next_task)
   else:
      await message.answer("🎉 Поздравляем! Вы выполнили все задания на сегодня!")
