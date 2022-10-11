import datetime
from logging import basicConfig, getLogger

import ormar
from databases import Database
from sqlalchemy import MetaData

from config.settings import app_settings, APP_LOGLEVEL, LOGGING_FORMAT


basicConfig(level=APP_LOGLEVEL, format=LOGGING_FORMAT)
__logger__ = getLogger(__name__)


class BaseMeta(ormar.ModelMeta):
    database: Database = Database(app_settings.database.url)
    metadata = MetaData()


class User(ormar.Model):
    """
    Telegram users, registered with the bot
    """

    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True, autoincrement=False)
    username: str = ormar.String(max_length=50)
    registered: bool = ormar.Boolean(default=False)
    registered_at: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())


class Child(ormar.Model):
    """
    A child object
    """

    class Meta(BaseMeta):
        tablename = "children"

    id: int = ormar.Integer(primary_key=True)
    userid: int = ormar.Integer()
    name: str = ormar.String(max_length=100)
    birthday: datetime.date = ormar.Date()


class Task(ormar.Model):
    """
    A Task object
    """

    class Meta(BaseMeta):
        tablename = "tasks"

        constraints = [
            ormar.CheckColumns("start_time < end_time", name="time_check"),
            ]

    id: int = ormar.Integer(primary_key=True)
    user_id: int = ormar.ForeignKey(User, on_delete=ormar.ReferentialAction.CASCADE)
    performer_id: int = ormar.ForeignKey(Child, on_delete=ormar.ReferentialAction.CASCADE)
    title: str = ormar.String(max_length=50)
    description: str = ormar.String(max_length=200, default="")
    start_time: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())
    end_time: datetime.datetime = ormar.DateTime(default=datetime.datetime.now() + datetime.timedelta(days=1.0))
