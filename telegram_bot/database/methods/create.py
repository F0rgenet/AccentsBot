from sqlalchemy.exc import NoResultFound

from loguru import logger
from random import choice, randint
from itertools import chain

from telegram_bot.database.main import Database
from telegram_bot.database.models import User


async def create_user(telegram_id: int, username: str):
	session = Database().session
	if not username:
		# TODO: temporary
		# TODO: fix same name
		characters = [chr(i) for i in chain(range(97, 123), range(48, 58))]
		username = "".join([choice(characters) for _ in range(randint(5, 10))])
	try:
		session.query(User.telegram_id).filter(User.telegram_id == telegram_id).one()
	except NoResultFound:
		logger.info(f"В базу данных добавлен пользователь (id:{telegram_id})")
		session.add(User(telegram_id=telegram_id, username=username))
	session.commit()
