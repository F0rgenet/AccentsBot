from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
from aiogram.exceptions import TelegramUnauthorizedError
from telegram_bot.database import register_models
from telegram_bot.utils import BotConfig
from .handlers import router as handlers_router

from utils.accents_quiz import AccentsQuizManager
from utils.leaderboard.images import generate_leaderboard_image


async def on_startup(dispatcher: Dispatcher):
	register_models()
	await generate_leaderboard_image()
	AccentsQuizManager().xml_manager.parse()
	dispatcher.include_router(handlers_router)

	logger.info("Бот запущен")


async def startup():
	config = BotConfig("telegram_bot/config.ini")

	fsm_storage = MemoryStorage()
	dispatcher = Dispatcher(storage=fsm_storage)
	dispatcher.startup.register(on_startup)

	bot = None
	while not bot:
		try:
			bot = Bot(token=config.get_data()["token"], parse_mode="HTML")
			await dispatcher.start_polling(bot)
		except (TokenValidationError, TelegramUnauthorizedError):
			logger.warning("Токен некорректен")
			config.wrong_field("token")
