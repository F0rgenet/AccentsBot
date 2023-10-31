import random
import os

from typing import Literal

from utils.quiz.models import TestQuestion, EgeQuestion, Word, Category
from xml.etree import ElementTree
from utils.singleton import SingletonMeta


class XMLAccentsManager(object):
	# TODO: xml append/remove
	def __init__(self):
		self.categories: list[Category] = []
		self.words: dict[str, list[Word]] = {}

		self.parse()

	async def get_category_title(self, category_name: str):
		for category in self.categories:
			if category_name == category.name:
				return category.title
		return None

	def parse(self):
		self.categories = []
		self.words = {}

		root = ElementTree.parse("data/accents.xml").getroot()
		for xml_category in root:
			self.categories.append(Category(xml_category.tag, xml_category.attrib["title"]))
			self.words[xml_category.tag] = []

			for word in xml_category:
				context = None
				if "context" in word.attrib:
					context = word.attrib["context"]
				data = Word(word.text, context)
				self.words[xml_category.tag].append(data)

	async def get_list(self, categories: Literal["all"] | list[str] = "all"):
		result = []
		for category, words in self.words.items():
			if categories == "all" or category in categories:
				result.extend(words)
		return result

class AccentsQuizManager(metaclass=SingletonMeta):
	def __init__(self):
		self.xml_manager = XMLAccentsManager()

		self.max_options = 3
		self.vowels = "аеёиоэюяуы"

	@staticmethod
	async def check_answer(question: TestQuestion, chosen_index: int):
		if chosen_index == question.answer_index:
			return True
		return False

	@property
	async def accents(self) -> dict:
		result = {}
		for category, elems in self.xml_manager.words.items():
			result[await self.xml_manager.get_category_title(category)] = elems
		return result

	async def get_word_accent_options(self, word: Word) -> tuple[list[str], int, str]:
		answer = word.content

		symbols = word.content.lower().replace("ё", "е")
		options = []
		for i, letter in enumerate(symbols):
			if letter not in self.vowels:
				continue
			option = symbols[:i] + letter.upper() + symbols[i + 1: len(symbols) + 1]
			if option != answer:
				options.append(option)

		options = options[:self.max_options - 1]
		answer_option = answer.replace("Ё", "Е")
		options.append(answer_option)

		random.shuffle(options)
		answer_index = options.index(answer_option)

		return options, answer_index, answer

	async def get_wrong_options(self, word: Word) -> list:
		options, answer_index, answer = await self.get_word_accent_options(word)
		options.pop(answer_index)
		return options

	async def get_ege_question(self, wrong_type: bool = False) -> EgeQuestion:
		words = await self.xml_manager.get_list()

		if not wrong_type:
			task_type = "верно"
		else:
			task_type = random.choice(["верно", "неверно"])
		task_description = f"Укажите варианты ответов, в которых <b>{task_type}</b> выделена буква," \
								f"обозначающая ударный гласный звук. Выберите номера ответов."
		right_options_count = random.randint(2, 4)
		used_words = []
		options = []
		explanation_pairs = []
		right_options = []
		# TODO: fix context
		while len(options) != 5:
			word = random.choice(words)
			if word in used_words: continue
			right_option = word.content.replace("Ё", "Е")
			wrong_option = random.choice(await self.get_wrong_options(word))

			chosen = ""
			if len(right_options) < right_options_count:
				# добавляем верные
				if task_type == "верно":
					chosen = right_option
					right_options.append(right_option)
					options.append(right_option)
				if task_type == "неверно":
					chosen = wrong_option
					right_options.append(wrong_option)
					options.append(wrong_option)
			else:
				# добавляем неверные
				if task_type == "верно":
					chosen = wrong_option
					options.append(wrong_option)
				if task_type == "неверно":
					chosen = right_option
					options.append(right_option)
			explanation_pairs.append((chosen, word.content))
			used_words.append(word)

		explanation = []
		random.shuffle(options)
		answer = ""
		wrong_type_answer = ""
		for option in options:
			for pair in explanation_pairs:
				if pair[0] == option:
					explanation.append(pair[1])

			index = str(options.index(option)+1)
			if option in right_options:
				answer += index
			else:
				wrong_type_answer += index
		return EgeQuestion(options, answer, task_type, task_description, wrong_type_answer, explanation)

	async def get_ege_questions(self, count: int, can_be_wrong_type: bool = False):
		questions = []
		while len(questions) < count:
			question = await self.get_ege_question(can_be_wrong_type)
			if question not in questions:
				questions.append(question)
		return questions

	async def get_test_question(self, categories: Literal["all"] | list[str] = "all") -> TestQuestion:
		words = await self.xml_manager.get_list(categories)
		word: Word = random.choice(words)

		options, answer_index, answer = await self.get_word_accent_options(word)

		return TestQuestion(options, answer, answer_index, word.context)

	async def get_test_questions(self, count: int, categories: Literal["all"] | list[str] = "all") -> list[TestQuestion]:
		questions = []
		while len(questions) < count:
			question = await self.get_test_question(categories)
			if question not in questions:
				questions.append(question)

		return questions
