from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

inline_keyboard = [[
    InlineKeyboardButton(text="✅ Yes", callback_data='yes'),
    InlineKeyboardButton(text="❌ No", callback_data='no')
]]
are_you_sure_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_product_markup(quality):
    product_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="-", callback_data="decrease"), InlineKeyboardButton(text=str(quality), callback_data=f"quality_{quality}"), InlineKeyboardButton(text="+", callback_data="increase")],
        [InlineKeyboardButton(text="📥 Savatga qo'shish", callback_data="add_cart")]
    ])
    return product_buttons