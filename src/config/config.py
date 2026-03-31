"""этот модуль берет данные из переменных окружения и возвращает их не показывая чувствительные данные"""
from dataclasses import dataclass
from environs import Env

# валидация данных для постгреса
@dataclass
class Postgres:
    user: str
    password: str
    db: str
    url: str

@dataclass
class Redis:
    host: str
    port: int
    db: int

@dataclass
class CORS:
    origins: list
    methods: list
    headers: list

# валидация данных для итогового класса конфигурации
@dataclass
class Config:
    postgres: Postgres
    redis: Redis
    cors: CORS 

# подстановка всех чувствительных данных из .env
def load_config(path: str | None = None):
    env = Env()
    env.read_env(path) # путь к .env. По умолчанию None, ищет в корне проекта
    return Config(
        postgres=Postgres(
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            db=env("POSTGRES_DB"),
            url=env("POSTGRES_URL"),
                          ),
        redis=Redis(host=env("REDIS_HOST"),
                    port=env.int("REDIS_PORT"),
                    db=env.int("REDIS_DB"),
                    ),
        cors=CORS(
            origins=env.list("ALLOW_ORIGINS"),
            methods=env.list("ALLOW_METHODS"),
            headers=env.list("ALLOW_HEADERS")
        )
    )

# получаем обьект конфига, который и используем в других модулях при необходимости
config = load_config()
