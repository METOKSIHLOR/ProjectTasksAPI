"""Просто инициализация редиса, ни больше, ни меньше:)"""
import redis
from src.config.config import config

storage = redis.Redis(host=config.redis.host,
                      port=config.redis.port,
                      db=config.redis.db,
                      decode_responses=True)