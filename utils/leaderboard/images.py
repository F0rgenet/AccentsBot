from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import aiofiles
from loguru import logger

from utils.leaderboard.tables import get_table


async def generate_image_with_text(file_name: str, text: str, font_size: int, indent: int = 25, xy: tuple = (0, 0)):
	font = ImageFont.truetype("data/fonts/consolas.ttf", font_size)
	left, top, right, bottom = font.getbbox(text)
	width, height = right - left, bottom - top
	image_size = (width + indent + xy[0], height + indent + xy[1])
	image = Image.new('RGB', image_size, color=(24, 37, 51))
	draw = ImageDraw.Draw(image)
	text_x = (image_size[0] // 2) - (width // 2) - left
	text_y = (image_size[1] // 2) - (height // 2) - top
	draw.text((text_x, text_y), text, (167, 180, 194), font=font, anchor="mm")
	image.save(f"data/images/{file_name}")


async def get_accents_image():
	try:
		async with aiofiles.open("data/images/accents.png", "rb") as image_file:
			image = await image_file.read()
	except FileNotFoundError:
		logger.info("Файл изображения ударений не найден, создаём...")
		await generate_accents_image()
		async with aiofiles.open("data/images/accents.png", "rb") as image_file:
			image = await image_file.read()
	return image


async def generate_accents_image():
	with open("bot/data/accents.txt", encoding="UTF-8") as file:
		accents = file.read()

	await generate_image_with_text("accents.png", accents, 41, xy=(50, 0))


async def get_leaderboard_image():
	try:
		async with aiofiles.open("data/images/leaderboard.png", "rb") as image_file:
			image = await image_file.read()
	except FileNotFoundError:
		logger.info("Файл изображения таблицы лидеров не найден, создаём...")
		await generate_leaderboard_image()
		async with aiofiles.open("data/images/leaderboard.png", "rb") as image_file:
			image = await image_file.read()
	return image


async def generate_leaderboard_image():
	table = await get_table()
	await generate_image_with_text("leaderboard.png", table, 41)
