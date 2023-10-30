from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from telegram_bot.keyboards import get_menu_keyboard
from telegram_bot.utils.states import Menu
from telegram_bot.database.methods import create_user

router = Router()


@router.message(Command(commands=["menu", "start"]))
async def menu(message: Message, state: FSMContext):
	await message.delete()
	text = """Этот бот поможет вам подготовиться к четвёртому заданию ЕГЭ по русскому языку!
				\nВ разработке! Возможны сбои и ошибки, пожалуйста сообщайте о них.
				\nАвтор: @forgenet."""
	keyboard = await get_menu_keyboard(False)

	data = await state.get_data()
	message_exists = "current_message" in data.keys()
	current = await message.answer(text, reply_markup=keyboard.as_markup())
	if message_exists:
		await data["current_message"].delete()
	await state.update_data(current_message=current)

	await state.set_state(Menu.main)

	await create_user(telegram_id=message.from_user.id, username=message.from_user.username)
	# await state.update_data(prev=state, menu_message=menu_message, message=menu_message)
