from sqlalchemy import Column, Integer, String

from .main import Database


class User(Database.BASE):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, autoincrement=True)
	telegram_id = Column(Integer, nullable=False)
	username = Column(String, nullable=True)
	solved_tasks = Column(Integer, default=0)
	solved_correctly = Column(Integer, default=0)


def register_models():
	Database.BASE.metadata.create_all(Database().engine)
