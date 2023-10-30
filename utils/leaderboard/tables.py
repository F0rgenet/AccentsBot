from telegram_bot.database.methods import get_leaderboard_data
from telegram_bot.database.models import User
from prettytable import PrettyTable


async def get_table():
	table = PrettyTable(["никнейм", "всего", "верно", "правильность"])
	table.align["никнейм"] = "l"
	table.align["решено всего"] = "l"
	table.align["решено верно"] = "l"
	table.align["процент"] = "l"
	users: list[User] = await get_leaderboard_data()
	if not users: return "Никого нет :("
	for user in users:
		coefficient = round(user.solved_correctly / user.solved_tasks * 100, 2)
		table.add_row([user.username, user.solved_tasks, user.solved_correctly, f"{coefficient}%"])
	return str(table)
