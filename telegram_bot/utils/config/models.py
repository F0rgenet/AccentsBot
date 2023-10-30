from dataclasses import dataclass

@dataclass()
class ConfigData(object):
	token: str = ""

	def __str__(self):
		return f"AccentsBotConfig"