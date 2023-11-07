from loguru import logger
from aiogram import Bot, Dispatcher
from decouple import config
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
from aiogram.exceptions import TelegramUnauthorizedError
from telegram_bot.database import register_models
from .handlers import router as handlers_router

from utils.accents_quiz import AccentsQuizManager
from utils.leaderboard.images import generate_leaderboard_image


async def on_startup(dispatcher: Dispatcher):
	with open("logs/test.txt", "w") as file:
		file.write("test")
	register_models()
	await generate_leaderboard_image()
	AccentsQuizManager().xml_manager.parse()
	dispatcher.include_router(handlers_router)
	logger.info("Бот запущен")


async def startup():
	fsm_storage = MemoryStorage()
	dispatcher = Dispatcher(storage=fsm_storage)
	dispatcher.startup.register(on_startup)
	try:
		bot = Bot(token=config("TELEGRAM_BOT_TOKEN"), parse_mode="HTML")
		await dispatcher.start_polling(bot)
	except (TokenValidationError, TelegramUnauthorizedError):
		logger.warning("Токен некорректен")
