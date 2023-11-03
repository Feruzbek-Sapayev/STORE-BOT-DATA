from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder



keyboard = [[
    KeyboardButton(text="☎️ Telefon raqamni yuborish", request_contact=True)
]]
send_phone_number = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

main_buttons = [
    [KeyboardButton(text="🛍 Buyurtma berish"), KeyboardButton(text="📋 Mening buyurtmalarim")],
    [KeyboardButton(text="ℹ️ Biz haqimizda"), KeyboardButton(text="⚙️ Sozlamalar")]
]
main_markup = ReplyKeyboardMarkup(keyboard=main_buttons, resize_keyboard=True)

def get_all_buttons_markup(cats = None):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="📥 Savat"))
    if cats:
        for cat in cats:
            builder.add(KeyboardButton(text=f"{cat['name']}"))
        builder.adjust(2)
    return builder.as_markup(resize_keyboard = True)
