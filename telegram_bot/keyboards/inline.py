from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from utils.accents_quiz.models import EgeQuestion, TestQuestion
from typing import Union
from telegram_bot.utils.callbacks import QuizCallback, QuizTasksCountCallback, QuizTasksTypeCallback, QuizEgeKeyboardCallback

async def get_back_keyboard(previous_callback: str, builder: InlineKeyboardBuilder = None):
	if not builder:
		builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Назад", callback_data=previous_callback))
	return builder

async def get_return_keyboard(target: str = "menu"):
	builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Вернуться", callback_data=target))
	return builder

async def get_quiz_return_keyboard():
	builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Вернуться", callback_data="done_quiz"))
	return builder

async def get_menu_keyboard(is_admin: bool):
	builder = InlineKeyboardBuilder()
	builder.row(
		InlineKeyboardButton(text="Решать", callback_data="select_quiz"),
		InlineKeyboardButton(text="Ударения", callback_data="accents"),
		InlineKeyboardButton(text="Таблица лидеров", callback_data="leaderboard")
	)
	builder.row(
		InlineKeyboardButton(text="Отправить отчёт", callback_data="report")
	)
	if is_admin:
		builder.add(InlineKeyboardButton(text="Админ панель", callback_data="admin_menu"))
	return builder

async def get_quiz_type_keyboard():
	builder = InlineKeyboardBuilder()
	builder.row(
		InlineKeyboardButton(text="ТЕСТ", callback_data=QuizTasksTypeCallback(tasks_type="тест").pack()),
		InlineKeyboardButton(text="ЕГЭ", callback_data=QuizTasksTypeCallback(tasks_type="егэ").pack())
	)
	return builder

async def get_quiz_tasks_count_keyboard():
	builder = InlineKeyboardBuilder()
	variants = [5, 10, 15, 25, 30]
	for count in variants:
		callback_data = QuizTasksCountCallback(tasks_count=count).pack()
		builder.add(InlineKeyboardButton(text=f"{count}", callback_data=callback_data))
	return builder

async def get_quiz_approve_keyboard():
	builder = InlineKeyboardBuilder()
	builder.add(InlineKeyboardButton(text="Начать", callback_data="start_quiz"))
	return builder

async def generate_for_test(task: TestQuestion):
	options = task.options
	context = f" {task.context}" if task.context else ""
	builder = InlineKeyboardBuilder()
	for index, option in enumerate(options):
		callback_data = QuizCallback(answer=index).pack()
		builder.add(InlineKeyboardButton(text=f"{option}{context}", callback_data=callback_data))
	return builder

async def generate_for_ege(task: EgeQuestion, current_state: list[bool]):
	builder = InlineKeyboardBuilder()
	for option, state in zip(range(1, 6), current_state):
		state_mark = f"✅" if state else f"❌"
		callback_data = QuizEgeKeyboardCallback(index=option - 1).pack()
		builder.add(InlineKeyboardButton(text=f"{option} [{state_mark}]", callback_data=callback_data))
	builder.add(InlineKeyboardButton(text="Готово", callback_data="send_answer"))
	return builder
