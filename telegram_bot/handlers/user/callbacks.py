import random

import aiofiles
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.handlers.callback_query import CallbackQuery
from aiogram.types import FSInputFile

import telegram_bot.keyboards as keyboards
from telegram_bot.utils.states import Quiz, get_state_values, Menu
from utils.accents_quiz import AccentsQuizManager
from .commands import menu as menu_command

router = Router()

@router.callback_query(Text(text="menu"))
async def menu(callback: CallbackQuery, state: FSMContext):
	# TODO: change to another function
	if await state.get_state() == "Menu:report":
		data = await state.get_data()
		for message in data["report_messages_responses"]:
			try:
				await message.delete()
			except TelegramBadRequest:
				pass

	await state.clear()
	text = """Этот бот поможет вам подготовиться к четвёртому заданию ЕГЭ по русскому языку!
					\nВ разработке! Возможны сбои и ошибки, пожалуйста сообщайте о них.
					\nАвтор: @forgenet."""
	keyboard = await keyboards.get_menu_keyboard(False)
	menu_message = await callback.message.edit_text(text, reply_markup=keyboard.as_markup())

	await state.update_data(menu_message=menu_message)
	await callback.answer()

@router.callback_query(Text(text="menu"))
async def return_to_menu(callback: CallbackQuery, state: FSMContext):
	if await state.get_state() in Quiz:
		quiz_messages = []
		try:
			quiz_messages = await get_state_values(state, ["quiz_messages"])
		except KeyError:
			pass
		for message in quiz_messages:
			try:
				await message.delete()
			except TelegramBadRequest as exception:
				pass
	text = "Возникла непредвиденная ошибка!\nНажмите на кнопку чтобы вернуться в меню."
	keyboard = await keyboards.get_return_keyboard()
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()


@router.callback_query(Text(text="accents"))
async def accents(callback: CallbackQuery):
	keyboard = await keyboards.get_back_keyboard("menu")
	text = ""
	for category, words in (await AccentsQuizManager().accents).items():
		words_string = ", ".join([str(word) for word in words])
		text += f"<b>{category.capitalize()}:</b>\n{words_string}\n"
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()

@router.callback_query(Text(text="report"))
async def report(callback: CallbackQuery, state: FSMContext):
	await state.set_state(Menu.report)
	await state.update_data(report_messages_responses=[])

	text = "Сообщите разработчику о <b>проблемах</b>, <b>идеях</b> и любой другой <b>информации</b>, связанной с ботом."
	text += "\nНапишите сообщение в чат."
	keyboard = await keyboards.get_return_keyboard()
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()


@router.callback_query(Text(text="leaderboard"))
async def leaderboard(callback: CallbackQuery, state: FSMContext):
	await state.set_state(Menu.leaderboard)
	await callback.message.edit_text(text="Загрузка...")
	await callback.message.delete()
	image = FSInputFile("data/images/leaderboard.png")
	keyboard = await keyboards.get_return_keyboard("return_from_leaderboard")
	await callback.message.answer_photo(image, reply_markup=keyboard.as_markup())
	await callback.answer()

@router.callback_query(Text(text="return_from_leaderboard"))
async def return_from_leaderboard(callback: CallbackQuery, state: FSMContext):
	await callback.message.delete()
	message = await callback.message.answer(text="Загрузка...")
	callback = callback.construct(id=callback.id, message=message)
	await callback.answer()
	await menu(callback, state)
