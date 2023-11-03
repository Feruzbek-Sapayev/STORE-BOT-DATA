from aiogram import Router, types, F
from aiogram.enums.parse_mode import ParseMode
from loader import db, bot
from utils.extra_datas import make_title
from aiogram.fsm.context import FSMContext
from states.user_states import UserState
from keyboards.reply.buttons import get_all_buttons_markup, main_markup
from keyboards.inline.buttons import get_product_markup
router = Router()


@router.message(F.text == "🛍 Buyurtma berish")
async def do_start(message: types.Message, state: FSMContext):
    await state.set_state(UserState.parent_category)
    data = await db.select_parent_cats()
    await state.set_data({'quality': 1})
    await message.answer("Tanla", reply_markup=get_all_buttons_markup(data))
    
@router.message(UserState.parent_category)
async def select_parent_category(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await message.answer("Buyurtma berishni boshlash uchun 🛍 Buyurtma berish tugmasini bosing.\nShuningdek, aksiyalarni ko'rishingiz va bizning filiallar bilan tanishishingiz mumkin.", reply_markup=main_markup)  
        await state.clear()  
    else:
        data = await db.get_category_by_name(message.text)
        if data is not None:
            category_id = data['id']
            await state.update_data({"parent_category_id": category_id})
            categories = await db.select_cats_from_parent_id(id=category_id)
            await message.answer("Category tanla:", reply_markup=get_all_buttons_markup(categories))
            await state.set_state(UserState.category)
        else:
            await message.answer("Bunday bo'lim mavjud emas!")
        
        
@router.message(UserState.category)
async def select_category(message: types.Message, state: FSMContext):  
    if message.text == "⬅️ Orqaga":
        data = await db.select_parent_cats()
        await message.answer("Tanla", reply_markup=get_all_buttons_markup(data))
        await state.set_state(UserState.parent_category) 
    else:
        category_id = await db.get_category_by_name(message.text)
        if category_id is not None:
            category_id = category_id['id']
            data = await db.get_products(category_id)
            await state.update_data({"category_id": category_id})
            await message.answer("Product tanla:", reply_markup=get_all_buttons_markup(data))
            await state.set_state(UserState.product)
        else:
            await message.answer("Bunday bo'lim mavjud emas!")
        
        
@router.message(UserState.product)
async def select_product(message: types.Message, state: FSMContext):  
    if message.text == "⬅️ Orqaga":
        parent_category_id = (await state.get_data()).get("parent_category_id")
        categories = await db.select_cats_from_parent_id(id=parent_category_id)
        await message.answer("Category tanla:", reply_markup=get_all_buttons_markup(categories))
        await state.set_state(UserState.category) 
    else:
        await message.answer("Mahsulot miqdorini tanlang:", reply_markup=get_all_buttons_markup()) 
        product = await db.get_product_by_name(message.text)
        if product is not None:
            quality = (await state.get_data()).get('quality')
            await message.answer_photo(photo=product['image'], caption=f"<b>{product['name']}</b>\n\n{product['description']}\n\nNarxi - {'{:,}'.format(product['price'])}\n\nSoni - {quality} ta\n\nUmumiy - {'{:,}'.format(quality * product['price'])}", parse_mode="html", reply_markup=get_product_markup(quality))
            await state.set_state(UserState.quality)
            await state.update_data({"product_name": message.text})
        else:
            await message.answer("Bunday mahsulot yo'q!")

@router.message(UserState.quality)
async def finaly_product(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        category_id = (await state.get_data()).get("category_id")
        data = await db.get_products(category_id)
        await message.answer("Product tanla:", reply_markup=get_all_buttons_markup(data))
        await state.update_data({"quality": 1})
        await state.set_state(UserState.product)
    
            
@router.callback_query(UserState.quality)
async def update_product(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quality = data.get('quality')
    product = await db.get_product_by_name(data.get('product_name'))
    if call.data == 'decrease':
        if quality == 1:
            await call.answer("Xato")
        else:
            quality -= 1
            await state.update_data(quality = quality)  
            quality = (await state.get_data()).get('quality')
            markup = get_product_markup(quality)
            await bot.edit_message_caption(chat_id=call.from_user.id, message_id=call.message.message_id, caption=f"<b>{product['name']}</b>\n\n{product['description']}\n\nNarxi - {'{:,}'.format(product['price'])}\n\nSoni - {quality} ta\n\nUmumiy - {'{:,}'.format(quality * product['price'])}", parse_mode="html", reply_markup=markup)

    if call.data == 'increase':
        if quality == 10:
            await call.answer("Mahsulot soni chegaralangan")
        else:
            quality += 1
            await state.update_data(quality = quality)
            quality = (await state.get_data()).get('quality')
            markup = get_product_markup(quality)
            await bot.edit_message_caption(chat_id=call.from_user.id, message_id=call.message.message_id, caption=f"<b>{product['name']}</b>\n\n{product['description']}\n\nNarxi - {'{:,}'.format(product['price'])}\n\nSoni - {quality} ta\n\nUmumiy - {'{:,}'.format(quality * product['price'])}", parse_mode="html", reply_markup=markup)    
    await call.answer()