import sqlalchemy.orm.attributes

from telegram_bot.database.main import Database
from telegram_bot.database.models import User


async def get_leaderboard_data():
	users = [user for user in Database().session.query(User).all() if user.solved_tasks]
	users.sort(key=lambda user: user.solved_correctly/user.solved_tasks, reverse=True)
	return users
