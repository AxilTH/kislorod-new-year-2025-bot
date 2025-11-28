from aiogram.fsm.state import StatesGroup, State

class DailyTasksState(StatesGroup):
    waiting_for_tf_answer = State()
    waiting_for_ai_answer = State()
    waiting_for_dish_answer = State()
