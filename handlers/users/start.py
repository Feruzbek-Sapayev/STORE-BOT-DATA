from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.session.middlewares.request_logging import logger
from loader import db, bot
from data.config import ADMINS
from utils.extra_datas import make_title
from aiogram.fsm.context import FSMContext
from states.registration import Registratsiya
# from states.user_states import UserState
from keyboards.reply.buttons import send_phone_number, main_markup
router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    """
            MARKDOWN V2                     |     HTML
    link:   [Google](https://google.com/)   |     <a href='https://google.com/'>Google</a>
    bold:   *Qalin text*                    |     <b>Qalin text</b>
    italic: _Yotiq shriftdagi text_         |     <i>Yotiq shriftdagi text</i>



                    **************     Note     **************
    Markdownda _ * [ ] ( ) ~ ` > # + - = | { } . ! belgilari to'g'ridan to'g'ri ishlatilmaydi!!!
    Bu belgilarni ishlatish uchun oldidan \ qo'yish esdan chiqmasin. Masalan  \.  ko'rinishi . belgisini ishlatish uchun yozilgan.
    """
    full_name = message.from_user.full_name
    user = await db.select_user(message.from_user.id)
    if user:
        await message.answer(f"Assalomu alaykum {make_title(full_name)}\!", parse_mode=ParseMode.MARKDOWN_V2)
        await message.answer("Buyurtma berishni boshlash uchun 🛍 Buyurtma berish tugmasini bosing.\nShuningdek, aksiyalarni ko'rishingiz va bizning filiallar bilan tanishishingiz mumkin.", reply_markup=main_markup)
    else:
        await state.set_state(Registratsiya.phone)
        await message.answer("📞 Ro'yxatdan o'tish uchun telefon raqamingizni yuboring.", reply_markup=send_phone_number)

@router.message(Registratsiya.phone)
async def ad_user(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    phone_number = message.contact.phone_number
    await state.clear()
    user = None
    try:
        user = await db.add_user(telegram_id=telegram_id, full_name=full_name, username=username, phone_number=phone_number)
    except Exception as error:
        logger.info(error)
    if user:
        count = await db.count_users()
        msg = (f"[{make_title(user['full_name'])}](tg://user?id={user['telegram_id']}) bazaga qo'shildi\.\nBazada {count} ta foydalanuvchi bor\.")
    else:
        msg = f"[{make_title(full_name)}](tg://user?id={telegram_id}) bazaga oldin qo'shilgan"
    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Exception as error:
            logger.info(f"Data did not send to admin: {admin}. Error: {error}")
    await message.answer(f"Assalomu alaykum {make_title(full_name)}\!", parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer("Buyurtma berishni boshlash uchun 🛍 Buyurtma berish tugmasini bosing.\nShuningdek, aksiyalarni ko'rishingiz va bizning filiallar bilan tanishishingiz mumkin.", reply_markup=main_markup)

