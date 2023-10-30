from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.handlers.callback_query import CallbackQuery
from loguru import logger
from aiogram import Router

import telegram_bot.keyboards as keyboards
from telegram_bot.utils.callbacks import *
from telegram_bot.utils.states import Quiz, get_state_values
from telegram_bot.database.methods import add_solved_task
from utils.accents_quiz import AccentsQuizManager, TestQuestion, EgeQuestion
from .callbacks import return_to_menu, menu
from utils.leaderboard.images import generate_leaderboard_image


router = Router()

@router.callback_query(Text(text="select_quiz"))
async def select_quiz(callback: CallbackQuery, state: FSMContext):
	await state.set_state(Quiz.preparing)
	select_keyboard = await keyboards.get_quiz_type_keyboard()
	keyboard = await keyboards.get_back_keyboard("menu", select_keyboard)
	text = "Выберите тип заданий:"
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()

@router.callback_query(QuizTasksTypeCallback.filter())
async def select_quiz_tasks_count(callback: CallbackQuery, callback_data: QuizTasksTypeCallback, state: FSMContext):
	tasks_type = callback_data.tasks_type
	await state.update_data(tasks_type=tasks_type)

	select_keyboard = await keyboards.get_quiz_tasks_count_keyboard()
	keyboard = await keyboards.get_back_keyboard("select_quiz", select_keyboard)
	text = f"Вы выбрали тип заданий: {tasks_type.upper()}\nВыберите количество заданий:"
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()

@router.callback_query(QuizTasksCountCallback.filter())
async def approve_quiz_settings(callback: CallbackQuery, callback_data: QuizTasksCountCallback, state: FSMContext):
	tasks_count = callback_data.tasks_count

	data = await state.get_data()
	try:
		tasks_type = data["tasks_type"]
	except KeyError:
		await return_to_menu(callback, state)
		return

	await state.update_data(tasks_count=tasks_count)
	approve_keyboard = await keyboards.get_quiz_approve_keyboard()
	back_keyboard_callback_text = QuizTasksTypeCallback(tasks_type=tasks_type).pack()
	keyboard = await keyboards.get_back_keyboard(back_keyboard_callback_text, approve_keyboard)
	text = f"Вы выбрали тип заданий: {tasks_type.upper()}\nВы выбрали количество заданий: {tasks_count}\n" \
		   	"Нажмите на кнопку чтобы начать тест."
	await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
	await callback.answer()

@router.callback_query(Text(text="start_quiz"))
async def start_quiz(callback: CallbackQuery, state: FSMContext):
	await state.set_state(Quiz.solving)

	data_keys = ["tasks_count", "tasks_type"]
	try:
		tasks_count, tasks_type = await get_state_values(state, data_keys)
	except KeyError:
		await return_to_menu(callback, state)
		return

	await state.update_data(current_question_index=0, correct_answers=0, quiz_messages=[])
	if tasks_type == "тест":
		questions = await AccentsQuizManager().get_test_questions(tasks_count)
		await state.update_data(questions=questions)
		await quiz_test_task(callback, QuizCallback(answer=""), state)
	else:
		questions = await AccentsQuizManager().get_ege_questions(tasks_count, True)
		# TODO: settings
		await state.update_data(questions=questions, keyboard_state=False)
		await quiz_ege_task(callback, state)
	await callback.answer()
	test_info = f"{tasks_type.upper()}({tasks_count} вопросов)"
	logger.info(f"Пользователь {callback.from_user.username} начал проходить тест: {test_info}")

@router.callback_query(QuizCallback.filter())
async def quiz_test_task(callback: CallbackQuery, callback_data: QuizCallback, state: FSMContext):
	# TODO: FIX duplication
	data_keys = ["questions", "current_question_index", "correct_answers", "quiz_messages"]
	try:
		questions, current_question_index, correct_answers, quiz_messages = await get_state_values(state, data_keys)
	except KeyError as exception:
		logger.info(f"У пользователя {callback.from_user.username} возникла проблема при запуске теста: {exception}")
		await return_to_menu(callback, state)
		return

	await state.update_data(current_question_index=current_question_index+1)
	answer = callback_data.answer
	if answer != "":
		# был ответ
		previous_question: TestQuestion = questions[current_question_index - 1]
		answer_response_text, is_correct = previous_question.estimate_task(answer)
		if is_correct:
			correct_answers += 1
			await state.update_data(correct_answers=correct_answers)
		await add_solved_task(callback.from_user.id, callback.from_user.username, is_correct)
		await callback.message.edit_text(answer_response_text, reply_markup=None)
	else:
		await callback.message.delete()
	if current_question_index < len(questions):
		task: TestQuestion = questions[current_question_index]
		quiz_keyboard = await keyboards.generate_for_test(task)
		text = questions[current_question_index-1].task_text()
		message = await callback.message.answer(text=text, reply_markup=quiz_keyboard.as_markup())
		await state.update_data(quiz_messages=quiz_messages + [message])
	else:
		await state.set_state(Quiz.results)
		text = f"Вы прошли тест. Ваш результат: <b>{correct_answers}/{len(questions)}</b>"
		return_keyboard = await keyboards.get_quiz_return_keyboard()
		await callback.message.answer(text=text, reply_markup=return_keyboard.as_markup())


@router.callback_query(QuizEgeKeyboardCallback.filter())
async def quiz_ege_keyboard_changed(callback: CallbackQuery, callback_data: QuizEgeKeyboardCallback, state: FSMContext):
	index = callback_data.index
	data = await state.get_data()
	try:
		current_keyboard_state = data["keyboard_state"]
	except KeyError as exception:
		logger.info(f"У пользователя {callback.from_user.username} возникла проблема при запуске теста: {exception}")
		await return_to_menu(callback, state)
		return

	current_keyboard_state[index] = not current_keyboard_state[index]
	await state.update_data(keyboard_state=current_keyboard_state)
	keyboard = await keyboards.generate_for_ege(data["questions"][data["current_question_index"]-1], current_keyboard_state)

	await callback.message.edit_text(callback.message.html_text, reply_markup=keyboard.as_markup())

@router.callback_query(Text(text="send_answer"))
async def quiz_ege_task(callback: CallbackQuery, state: FSMContext):
	data_keys = ["questions", "current_question_index", "correct_answers", "quiz_messages", "keyboard_state"]
	try:
		questions, current_question_index, correct_answers, \
			quiz_messages, keyboard_state = await get_state_values(state, data_keys)
	except KeyError as exception:
		logger.info(f"У пользователя {callback.from_user.username} возникла проблема при запуске теста: {exception}")
		await return_to_menu(callback, state)
		return

	if keyboard_state:
		# был ответ
		previous_question: EgeQuestion = questions[current_question_index - 1]
		answer = "".join([str(number) for state, number in zip(keyboard_state, range(1, 6)) if state])
		answer_response_text, is_correct = previous_question.estimate_task(answer)
		if is_correct:
			correct_answers += 1
			await state.update_data(correct_answers=correct_answers)
		await add_solved_task(callback.from_user.id, callback.from_user.username, is_correct)
		await callback.message.edit_text(answer_response_text, reply_markup=None)
	else:
		await callback.message.delete()

	keyboard_state = [False, False, False, False, False]
	await state.update_data(current_question_index=current_question_index + 1, keyboard_state=keyboard_state)

	if current_question_index < len(questions):
		task: EgeQuestion = questions[current_question_index]
		quiz_keyboard = await keyboards.generate_for_ege(task, keyboard_state)
		text = questions[current_question_index].task_text()
		message = await callback.message.answer(text=text, reply_markup=quiz_keyboard.as_markup())
		await state.update_data(quiz_messages=quiz_messages + [message])
	else:
		await state.set_state(Quiz.results)
		text = f"Вы прошли тест. Ваш результат: <b>{correct_answers}/{len(questions)}</b>"
		return_keyboard = await keyboards.get_quiz_return_keyboard()
		await callback.message.answer(text=text, reply_markup=return_keyboard.as_markup())

@router.callback_query(Text(text="done_quiz"))
async def done_quiz(callback: CallbackQuery, state: FSMContext):
	data_keys = ["quiz_messages", "correct_answers", "questions", "tasks_type"]
	try:
		quiz_messages, correct_answers, questions, tasks_type = await get_state_values(state, data_keys)
	except KeyError as exception:
		quiz_messages = []
		tasks_type = "error"
		correct_answers = 0
		questions = []
	for message in quiz_messages:
		try:
			await message.delete()
		except TelegramBadRequest as exception:
			logger.warning(f"Не удалось удалить сообщение теста: {exception}")
	quiz_info = f"{tasks_type.upper()}({correct_answers}/{len(questions)})"
	logger.info(f"Пользователь {callback.from_user.username} закончил тест: {quiz_info}")
	await generate_leaderboard_image()

	await menu(callback, state)
