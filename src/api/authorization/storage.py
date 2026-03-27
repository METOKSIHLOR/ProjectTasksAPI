"""Просто инициализация редиса, ни больше, ни меньше:)"""
import redis

storage = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)