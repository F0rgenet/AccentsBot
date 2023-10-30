from sqlalchemy.exc import NoResultFound

from telegram_bot.database.main import Database
from telegram_bot.database.models import User
from telegram_bot.database.methods import create_user

from loguru import logger


async def add_solved_task(telegram_id: int, username: str, correct: bool):
	session = Database().session
	try:
		session.query(User.telegram_id).filter(User.telegram_id == telegram_id).one()
		user_filter = session.query(User).filter(User.telegram_id == telegram_id)
		user = user_filter.one()
		user_filter.update(values={User.solved_tasks: user.solved_tasks + 1})
		if correct:
			user_filter.update(values={User.solved_correctly: user.solved_correctly + 1})
		session.commit()
	except NoResultFound:
		logger.error(f"Пользователя не было в базе данных: id={telegram_id}")
		await create_user(telegram_id, username)
