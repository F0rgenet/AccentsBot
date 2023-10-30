from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from telegram_bot.utils.states import Menu

from loguru import logger
router = Router()

@router.message(Menu.report)
async def catch_report(message: Message, state: FSMContext):
	text = f"Получен репорт от пользователя {message.from_user.username}:\n{message.text}"
	logger.info(text)
	await message.delete()
	message = await message.answer("Сообщение отправлено!")
	report_messages_responses = (await state.get_data())["report_messages_responses"]
	await state.update_data(report_messages_responses=report_messages_responses+[message])
