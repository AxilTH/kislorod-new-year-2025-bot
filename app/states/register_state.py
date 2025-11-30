from aiogram.fsm.state import State, StatesGroup

class registerState(StatesGroup):
   registerCode = State()
   firstName = State()
   lastName = State()