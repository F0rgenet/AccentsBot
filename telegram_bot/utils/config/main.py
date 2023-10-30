import os
from configparser import ConfigParser, ParsingError, DuplicateOptionError, DuplicateSectionError
from .models import ConfigData
from dataclasses import asdict
from loguru import logger
import time

class BotConfig(object):
	def __init__(self, file_path: str):
		self.config = ConfigParser()
		self.model = ConfigData()
		self.model_fields = list(asdict(self.model).keys())
		self.section = str(self.model)

		self.file_exists = False

		self.file_path = file_path
		self.validate_config()

	def get_data(self):
		try:
			items = self.config.items(self.section)
			if items:
				return {data[0]: data[1] for data in items}
		except Exception as exception:
			logger.warning(f"Невозможно получить данные из файла конфигурации: {exception}")
			self.delete_config_file()
			self.validate_config()
			return {}

	def wrong_field(self, field):
		data = self.ask_field_value(field)
		self.config.set(self.section, field, data)
		self.write_config_to_file()

	@staticmethod
	def ask_field_value(field):
		time.sleep(0.05)
		data = input(f"Укажите значение для '{field}': ")
		return data

	def check_file_exists(self):
		try:
			open(self.file_path)
		except FileNotFoundError:
			logger.warning(f"Файла конфигурации не существует по пути {self.file_path}")
			return False
		self.file_exists = True
		return True

	def read_file(self):
		try:
			self.config.read(self.file_path, encoding="UTF-8")
		except (ParsingError, DuplicateOptionError, DuplicateSectionError) as exception:
			logger.warning(f"Файл конфигурации повреждён: {exception}")
			return False
		return True

	def check_file_bot_section(self):
		if self.section not in self.config.sections():
			logger.warning(f"Секция отсутствует в файле конфигурации: {self.section}")
			return False
		return True

	def check_file_section_fields(self):
		config_fields = self.config.options(self.section)
		change_file = False
		for field in config_fields:
			if field not in self.model_fields:
				self.config.remove_option(self.section, field)
				logger.warning(f"Удалено лишнее поле в файле конфигурации: {field}")
				change_file = True

		missing_fields = set(self.model_fields).difference(set(config_fields))
		for field in self.model_fields:
			if field not in missing_fields: continue
			data = self.ask_field_value(field)
			self.config.set(self.section, field, data)
			logger.info(f"В конфиг записано отсутствующее значение: '{field} = {data}'")
			change_file = True

		if change_file:
			self.write_config_to_file()

	def write_config_to_file(self):
		if self.section not in self.config.sections():
			self.config.add_section(self.section)

		with open(self.file_path, "w", encoding="UTF-8") as file:
			self.config.write(file)
		if self.file_exists:
			action = "обновлён"
		else:
			action = "создан"
			self.file_exists = True
		logger.info(f"Файл конфигурации бота {action}")

	def delete_config_file(self):
		try:
			os.remove(self.file_path)
		except Exception as exception:
			logger.error(f"Ошибка при удалении файла конфигурации: {exception}")
		logger.info(f"Файл конфигурации по пути {self.file_path} удалён")

	def validate_config(self):
		if not self.check_file_exists():
			self.write_config_to_file()

		if not self.read_file():
			self.write_config_to_file()

		if not self.check_file_bot_section():
			self.write_config_to_file()

		self.check_file_section_fields()

		logger.info("Файл конфигурации бота проверен")
