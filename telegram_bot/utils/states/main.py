from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from typing import Callable

class Menu(StatesGroup):
	main = State()
	accents = State()
	leaderboard = State()
	report = State()

class Quiz(StatesGroup):
	preparing = State()
	solving = State()
	results = State()


async def get_state_values(state: FSMContext, keys: list["str"]):
	result = []
	data = await state.get_data()
	for key in keys:
		result.append(data[key])
	return result
