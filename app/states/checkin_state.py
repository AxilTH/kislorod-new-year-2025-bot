from aiogram.fsm.state import State, StatesGroup

class checkinState(StatesGroup):
   waiting_for_event_code = State()