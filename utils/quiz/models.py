from dataclasses import dataclass
from typing import Union
from abc import abstractmethod, ABCMeta


class BaseQuestion(metaclass=ABCMeta):
	@abstractmethod
	def task_text(self) -> str: pass

	@abstractmethod
	def estimate_task(self, user_answer: Union[str, int]) -> tuple[str, bool]: pass

@dataclass()
class TestQuestion(BaseQuestion):
	options: list[str]
	answer: str
	answer_index: int
	context: str = None

	def task_text(self) -> str:
		return f"Выберите <b>верный</b> вариант постановки ударения в слове:"

	def estimate_task(self, user_answer: int) -> tuple[str, bool]:
		if user_answer == self.answer_index:
			text = f"[✅]<b>Верно</b>!"
			state = True
		else:
			correct_answer = self.options[self.answer_index]
			text = f"[❌]<b>Неверно</b>\nОтвет был: {correct_answer}\nВаш ответ: {self.options[user_answer]}"
			state = False
		return text, state

@dataclass()
class EgeQuestion(BaseQuestion):
	options: list[str]
	answer: str
	task_type: str
	task_description: str
	wrong_type_answer: str
	explanations: list[str]

	def task_text(self) -> str:
		options = "\n".join([f"{i+1}) {elem}" for i, elem in enumerate(self.options)])
		return f"{self.task_description}\n{options}"

	def estimate_task(self, user_answer: str) -> tuple[str, bool]:
		if user_answer == self.answer:
			text = f"[✅]<b>Верно</b>!"
			state = True
		else:
			addition = ""
			if user_answer == self.wrong_type_answer:
				addition = f"\nВы невнимательно прочитали задание, там было написано <b>{self.task_type}</b>"

			explanation_data = "\n".join([f"{i+1}) {elem}" for i, elem in enumerate(self.explanations)])
			explanation = f"Пояснение:\n{explanation_data}"
			correct_answer = self.answer
			text = f"[❌]<b>Неверно</b>\nОтвет был: {correct_answer}\nВаш ответ: {user_answer}\n{explanation}{addition}"
			state = False
		return text, state

@dataclass()
class Word(object):
	content: str
	context: str = None

	def __str__(self):
		if self.context:
			return f"{self.content} ({self.context})"
		else:
			return f"{self.content}"


@dataclass()
class Category(object):
	name: str
	title: str
