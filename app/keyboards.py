from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_events_keyboard(events):
   keyboard = InlineKeyboardMarkup(inline_keyboard=[])
   
   # Создаем ряды по 2 кнопки
   for i in range(0, len(events), 2):
      row_events = events[i:i+2]
      row_buttons = [
         InlineKeyboardButton(text=event.title, callback_data=f"event:{event.id}")
         for event in row_events
      ]
      keyboard.inline_keyboard.append(row_buttons)
   
   # Добавляем кнопку отмены в отдельной строке
   keyboard.inline_keyboard.append([
      InlineKeyboardButton(text="Отмена", callback_data="cancel_checkin")
   ])
   
   return keyboard

# Использование
events_keyboard = create_events_keyboard

# Клавиатура для начала регистрации
register_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="✅ Зарегистрироваться", callback_data="register")],
])

cancel_checkin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_checkin")]
])
