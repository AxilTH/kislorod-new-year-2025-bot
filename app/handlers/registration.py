from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import REGISTER_CODE

import app.keyboards as keyboards
import app.states.register_state as registerState
import app.database.requests as db_requests

import textwrap

router = Router()


@router.message(CommandStart())
async def handler_start(message: Message, state: FSMContext):
   is_user_registered = await db_requests.is_user_registered(message.from_user.id)

   # Если пользователь зарегистрирован
   if is_user_registered:
      await message.answer(textwrap.dedent(
      '''
         Ты уже зарегистрирован!

         Для получения списка команд введи команду /help
      '''
      ))
      await state.clear()
      return

   text = textwrap.dedent(
   '''
      ✨ <b>Добро пожаловать в новогоднее волшебство от СПО "Кислород"!</b>

      За окном тихо падает снег, в воздухе витает аромат мандаринов и ожидание чуда… А у нас для тебя есть свой, особенный календарь приятных сюрпризов на весь этот уютный месяц!

      🧣 Как устроено наше волшебство:
      1. <b>Каждый день открывай новое послание.</b> Как маленькое письмо из будущего, которое подскажет, как сделать день чуть светлее.
      2. <b>Заглядывай в расписание мероприятий.</b> Чтобы ни одна встреча с друзьями, ни один тёплый вечер не прошёл мимо.
      3. <b>Выполняй задания каждый день.</b> Они помогут создать праздничное настроение, а за старания ты получишь волшебные снежинки-баллы.
      4. <b>Приходи на наши мероприятия.</b> За участие в создании общего праздника мы щедро начислим тебе снежинок!

      💰 <b>Собирай снежинки-баллы и встречай Новый Год с подарками и самым лучшим настроением!</b>

      Но чтобы сказка началась, нужно сделать первый шаг — зарегистрироваться! 👇
   ''')

   await message.answer(text, reply_markup=keyboards.register_keyboard, parse_mode='HTML')


@router.callback_query(F.data == 'register')
async def handler_register_code(callback: CallbackQuery, state: FSMContext):
   await callback.answer()
   await state.set_state(registerState.registerState.registerCode)

   text = textwrap.dedent(
   '''
      🔐 Регистрация в боте <b>"Кислород. Новый Год"</b>

      Для участия в нашей общей сказке напиши <b>секретное слово</b>, известное каждому из наших бойцов.

      Если слово подзабылось или ты ещё не успел его узнать, смело обращайся к комиссару нашего отряда.

      Введи секретное слово:
   ''')

   await callback.message.answer(text, parse_mode='HTML')


@router.message(registerState.registerState.registerCode)
async def handler_check_register_code(message: Message, state: FSMContext):
   if message.text != REGISTER_CODE:
      await message.answer('Неверное секретное слово! Попробуй еще раз:')
      return

   await state.update_data(registerCode=message.text)
   await state.set_state(registerState.registerState.firstName)

   text = textwrap.dedent(
   '''
      Отлично! Напиши свое <b>имя</b>:
   ''')
   await message.answer(text, parse_mode='HTML')


@router.message(registerState.registerState.firstName)
async def handler_register_last_name(message: Message, state: FSMContext):
   await state.update_data(firstName=message.text)
   await state.set_state(registerState.registerState.lastName)

   text = 'Теперь напиши свою <b>фамилию</b>!'

   await message.answer(text, parse_mode='HTML')


@router.message(registerState.registerState.lastName)
async def handler_register_second_name(message: Message, state: FSMContext):
   await state.update_data(lastName=message.text)
   await state.set_state(registerState.registerState.secondName)

   text = 'Теперь напиши свое <b>отчество</b>!'

   await message.answer(text, parse_mode='HTML')


@router.message(registerState.registerState.secondName)
async def handler_register(message: Message, state: FSMContext):
   await state.update_data(secondName=message.text)

   user_data = await state.get_data()
   user = await db_requests.create_user(
      message.from_user.id, 
      user_data['firstName'], 
      user_data['lastName'], 
      user_data['secondName']
   )

   success_text = textwrap.dedent(f'''
      ✅ Регистрация завершена! Сказка начинается!

      Добро пожаловать, {user.first_name} {user.last_name} {user.second_name}!
      Отныне твой статус в этой зимней сказке - <b>Боец</b> 🧤✨

      Тебя ждут уютные вечера, тёплые встречи и самые зимние чудеса! Давай вместе создадим эту новогоднюю сказку!
   ''')

   await message.answer(success_text, parse_mode='HTML')
   await state.clear()
