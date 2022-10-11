from logging import getLogger, basicConfig

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from config.settings import app_settings, APP_LOGLEVEL, LOGGING_FORMAT
from .models import (
    BaseMeta,
    User,
    Child
)

basicConfig(level=APP_LOGLEVEL, format=LOGGING_FORMAT)
__logger__ = getLogger(__name__)

db_engine = create_engine(app_settings.database.url)


def initialize_db():
    """
    Initializes database if it's not yet
    """

    BaseMeta.metadata.create_all(db_engine)


async def register_user(user_id: int, username: str) -> None:
    """
    Сохраняет в базу нового пользователя бота
    :param user_id: идентификатор телеграм пользователя
    :param username: имя пользователя
    """

    await User.objects.create(id=user_id, username=username)


async def get_user(user_id: int) -> int | None:
    """
    Ищет в базе пользователя по его идентификатору телеграм
    :param user_id: идентификатор пользователя в телеграм
    :return: идентификатор пользователя в телеграм
    """

    return await User.objects.get_or_none(id=user_id)


async def add_child(user_id: int, name: str, birthday: str) -> bool:
    """
    Добавляет ребёнка в базу, закрепляя его за пользователем
    :param user_id: telegram user id
    :param name: child's name
    :param birthday: child's birthday
    :return:
    """

    try:
        chld = Child(userid=user_id, name=name, birthday=birthday)
        await chld.save()
        return True
    except IntegrityError as ex:
        __logger__.error(f"Duplicate child record: {user_id} - {name} - {birthday}", "Child add error", exc_info=ex)
        return False
