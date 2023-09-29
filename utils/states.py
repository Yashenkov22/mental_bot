from aiogram.fsm.state import StatesGroup, State


class Quiz(StatesGroup):
    answer = State()


class CurrentEmpoyee(StatesGroup):
    limit = State()
    name = State()


class RegisterUser(StatesGroup):
    fullname: str = State()


class LoadPicture(StatesGroup):
    user_id = State()
    pic_id = State()


class ValidateUser(StatesGroup):
    secret_word = State()


class ChangeName(StatesGroup):
    fullname = State()