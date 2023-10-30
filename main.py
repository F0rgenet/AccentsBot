from telegram_bot import startup
import asyncio
from loguru import logger

logger.add("logs/accents.log", rotation="1 day")


@logger.catch()
def main():
	loop = asyncio.new_event_loop()
	loop.run_until_complete(startup())


if __name__ == '__main__':
	main()
