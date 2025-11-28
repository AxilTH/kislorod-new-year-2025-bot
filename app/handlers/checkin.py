from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

import app.keyboards as keyboards
import app.database.requests as db_requests
import app.states.checkin_state as checkinState

import textwrap

router = Router()

@router.message(Command('checkin'))
async def handler_checkin(message: Message):
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
   
   events = await db_requests.get_all_events()

   if not events:
      await message.answer('❄️ В предновогодней тишине...')
      return

   events_keyboard = keyboards.create_events_keyboard(events)

   text = textwrap.dedent('📅 Выбери мероприятие, на котором хочешь отметиться:')
   await message.answer(text, reply_markup=events_keyboard)


@router.callback_query(F.data.startswith("event:"))
async def callback_select_event(callback: CallbackQuery, state: FSMContext):
   await callback.message.delete_reply_markup()  # или edit to avoid duplicate KBs
   event_id = int(callback.data.split(":", 1)[1])
   event = await db_requests.get_event_by_id(event_id)

   if not event:
      await callback.message.answer("Мероприятие не найдено.")
      return

   # формат даты для вывода
   local_dt = event.date  # предполагается datetime
   formatted = local_dt.strftime("%d.%m.%Y %H:%M")

   text = (
      f"🎄 {event.title}\n"
      f"📆 {formatted}\n"
      f"❄️ Волшебных снежинок: {event.score}\n\n"
      "🗝️ Напиши секретное слово, которое на мероприятии объявил комиссар:"
   )

   # редактируем предыдущее сообщение (заменяем кнопки) или отправляем новое
   await callback.message.answer(text, reply_markup=keyboards.cancel_checkin_keyboard)
   # сохраняем выбранное event_id в FSM
   await state.update_data(event_id=event_id)
   await state.set_state(checkinState.checkinState.waiting_for_event_code)

@router.message(checkinState.checkinState.waiting_for_event_code)
async def handler_event_code(message: Message, state: FSMContext):
   data = await state.get_data()
   event_id = data.get("event_id")

   if not event_id:
      await message.answer("Ошибка. Попробуйте /checkin ещё раз.")
      await state.clear()
      return

   tg_id = message.from_user.id
   user = await db_requests.get_user_by_tg_id(tg_id)
   if not user:
      await message.answer("Вы не зарегистрированы. Пожалуйста, выполните /start для регистрации.")
      await state.clear()
      return

   codeword = message.text.strip()

   success, result_text, _ = await db_requests.mark_attendance(user_id=user.id, event_id=event_id, codeword=codeword)

   if success:
      await message.answer(result_text)
      await state.clear()
      return

   # Неуспех — различаем: уже отмечен vs неверный код
   lowered = result_text.lower()
   if "уже отмеч" in lowered or "уже отмечены" in lowered or "уже отмечен" in lowered:
      await message.answer(result_text)
      await state.clear()
   else:
      # неверный код — даём возможность попробовать ещё раз
      await message.answer(f"{result_text}. Попробуй еще раз:", reply_markup=keyboards.cancel_checkin_keyboard)


@router.callback_query(F.data == "cancel_checkin")
async def callback_cancel_checkin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Отмена отметки на мероприятии.")

    try:
        await callback.message.delete_reply_markup()
    except Exception:
        pass
