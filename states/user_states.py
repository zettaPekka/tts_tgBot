from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    text = State()
    deposit = State()
