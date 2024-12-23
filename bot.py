from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, logging
from config.token import token

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=token)
dp = Dispatcher()

MENU = {
    'Автозапчасти': 5000,
    "Мобильные запчасти": 2000,
}

MENU_WOMEN = {
    "Косметика": 3000,
}

orders = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.button(text="Мужчина", callback_data="gender_male")
    builder.button(text="Женщина", callback_data="gender_female")
    builder.adjust(1)

    await message.answer("Добро пожаловать.\nВыберите ваш пол:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "gender_male")
async def male(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    for item, price in MENU.items():
        builder.button(text=f"{item} - {price} сом", callback_data=f"menu_male_{item}")
    builder.adjust(2)

    await callback.message.answer("Вы выбрали: Мужчина. Вот доступные категории:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "gender_female")
async def female(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    for item, price in {**MENU, **MENU_WOMEN}.items():
        builder.button(text=f"{item} - {price} сом", callback_data=f"menu_female_{item}")
    builder.adjust(2)

    await callback.message.answer("Вы выбрали: Женщина. Вот доступные категории:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    item = callback.data.split("_")[2]
    
    if category == "male":
        price = MENU.get(item)
    else:
        price = {**MENU, **MENU_WOMEN}.get(item)
    
    if price is None:
        await callback.message.answer("Неизвестная категория")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text=f"Подтвердить выбор: {item} - {price} сом", callback_data=f"confirm_{category}_{item}")
    builder.button(text="Отменить", callback_data="cancel")
    builder.adjust(1)

    await callback.message.answer(f"Вы выбрали товар: {item} - {price} сом. Подтвердите выбор или отмените.", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    item = callback.data.split("_")[2]

    if category == "male":
        price = MENU.get(item)
    else:
        price = {**MENU, **MENU_WOMEN}.get(item)

    if price is None:
        await callback.message.answer("Неизвестная категория")
        return

    await callback.message.answer(f"Ваш заказ подтвержден: {item} - {price} сом. Спасибо за покупку!")
    await callback.answer()

@dp.callback_query(F.data == "cancel")
async def cancel_order(callback: types.CallbackQuery):
    await callback.message.answer("Ваш заказ отменен.")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
