from pydantic import BaseModel, BaseSettings, validator
from pydantic.env_settings import SettingsSourceCallable
from pathlib import Path
from enum import Enum
import re
import logging

APP_LOGLEVEL = logging.DEBUG  # logging.INFO | logging.WARNING | logging.ERROR
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s: %(message)s'

logging.basicConfig(level=APP_LOGLEVEL, format=LOGGING_FORMAT)
__logger__ = logging.getLogger(__name__)


class TelegramBot(BaseModel):
    """
    Telegram bot settings
    """

    api_token: str
    user_name: str


class DatabaseType(Enum):
    SQLITE = 0  # alias for sqlalchemy dialect sqlite
    POSTGRESQL = 1  # alias for sqlalchemy dialect postgresql
    MYSQL = 2  # alias for sqlalchemy dialect mysql
    MSSQL = 3  # alias for sqlalchemy dialect mssql


class DatabaseSettings(BaseModel):
    """
    Database metadata
    The typical form of a database url is:
    dialect+driver://username:password@host:port/database
    """

    dialects_available = ("sqlite", "postgresql", "mysql", "mssql")
    type: DatabaseType | int = DatabaseType.SQLITE
    url: str = "sqlite://"
    driver: str | None
    username: str | None
    password: str | None
    host: str | None
    port: str | None
    database: str | None

    @validator("type")
    def validate_type(cls, value, **kwargs) -> DatabaseType:
        if not isinstance(value, int) and not isinstance(value, DatabaseType):
            raise TypeError("Неверно задан тип БД")
        if isinstance(value, DatabaseType):
            return value
        if isinstance(value, int) and 0 <= value < 4:
            return DatabaseType(value)
        raise ValueError("Неизвестный тип БД")

    @validator("url", always=True)
    def validate_db_url(cls, value: str, values, **kwargs) -> str:
        if "type" in values and values['type'].value:

            assert all(key in values for key in ('username', 'password', 'host', 'port', 'database')), \
                "Не все обязательные параметры заданы"

            if (isinstance(values['type'], DatabaseType) and isinstance(values['username'], str)
                    and isinstance(values['password'], str) and isinstance(values['host'], str)
                    and isinstance(values['port'], int) and isinstance(values['database'], str)):
                return cls.create_db_url_for_non_sqlite(values['type'],
                                                        (f"+{values['driver']}"
                                                         if "driver" in values and isinstance(values['driver'], str)
                                                         else ""),
                                                        values['username'],
                                                        values['password'],
                                                        values['host'],
                                                        values['port'],
                                                        values['database'])
            else:
                raise TypeError("Не правильно задан один из параметров подключения к БД: неверный тип.")
        else:
            assert isinstance(value, str) and len(value) > 0, "Вместо строки подключения передана" \
                                                              " либо пустая строка, либо вообще не строка"
            assert value.find(":") > 0, "Неверный формат строки подключения к БД"

            dialect = value[:value.find(":")].split("+")[0].upper()

            assert dialect in DatabaseType.__members__.keys(), "Неизвестный тип БД"

            regex = (r"^(?P<dialect>postgresql|mysql|mssql)+?"
                     r"(\+(?P<driver>psycopg2|pg8000|mysqldb|pymysql|pyodbc|pymssql))?:\/\/"
                     r"((?P<username>[\w]+)(:(?P<password>[\w\S]+))?@)?(?P<host>[\w\d\-.%]+)(:(?P<port>\d{2,5}))?"
                     r"\/(?P<database>\w+)$")

            m_res = re.match(regex, value)
            if m_res is not None and len(m_res.groups()) > 0:
                return value
            else:
                # absolute path to sqlite sqlite:////absolute/path/to/foo.db
                # relative path to sqlit sqlite:///foo.db
                # sqlite :memory: database sqlite://
                if dialect == "SQLITE":
                    if value.lower() == "sqlite://":
                        return value
                    else:
                        with Path(value[10:]) as db_path:
                            if not db_path.is_absolute():
                                db_path = Path.cwd().joinpath(db_path)
                                __logger__.debug(f"Creating DB file. Current path: {db_path}")
                            if not db_path.exists():
                                db_path.touch()
                            else:
                                return value
                else:
                    raise ValueError("Не удалось распознать строку подключения.")

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.url

    @classmethod
    def create_db_url_for_non_sqlite(cls, dialect: DatabaseType,
                                     driver: str,
                                     username: str,
                                     password: str,
                                     host: str,
                                     port: int,
                                     database: str) -> str:
        return f"{dialect.name.lower()}" \
               f"{driver}" \
               f"://{username}" \
               f":{password}" \
               f"@{host}" \
               f":{port}" \
               f"/{database}"


class Settings(BaseSettings):
    """
    Application settings
    """

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'

        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, file_secret_settings, init_settings

    root_dir = Path.cwd().parent
    tg_bot: TelegramBot
    database: DatabaseSettings


app_settings = Settings(_env_file=Path(Path.cwd(), ".env"))
