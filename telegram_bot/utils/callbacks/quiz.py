from typing import Union
from aiogram.filters.callback_data import CallbackData


class QuizTasksCountCallback(CallbackData, prefix="quiz_tasks_count"):
	tasks_count: int


class QuizTasksTypeCallback(CallbackData, prefix="quiz_tasks_type"):
	tasks_type: str


class QuizEgeKeyboardCallback(CallbackData, prefix="quiz_ege_keyboard"):
	index: int


class QuizCallback(CallbackData, prefix="accents_quiz"):
	answer: Union[int, str]
