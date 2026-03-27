"""этот модуль берет данные из переменных окружения и возвращает их не показывая чувствительные данные"""

from dataclasses import dataclass
from environs import Env

# валидация данных для постгреса
@dataclass
class Postrges:
    user: str
    password: str
    db: str
    url: str

# валидация данных для итогового класса конфигурации
@dataclass
class Config:
    postrges: Postrges

# подстановка всех чувствительных данных из .env
def load_config(path: str | None = None):
    env = Env()
    env.read_env(path) # путь к .env. По умолчанию None, ищет в корне проекта
    return Config(
        postrges=Postrges(
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            db=env("POSTGRES_DB"),
            url=env("POSTGRES_URL"),
                          )
    )

# получаем обьект конфига, который и используем в других модулях при необходимости
config = load_config()