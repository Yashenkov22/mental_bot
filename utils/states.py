from aiogram.fsm.state import StatesGroup, State


class Quiz(StatesGroup):
    answer = State()


class CurrentEmpoyee(StatesGroup):
    limit = State()
    name = State()


class RegisterUser(StatesGroup):
    fullname: str = State()