from aiogram.filters.state import StatesGroup, State

class UserState(StatesGroup):
    parent_category = State()
    category = State()
    product = State()
    quality = State()      

