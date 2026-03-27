"""Данный модуль служит для хеширования и декодирования паролей пользователя"""

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Хешируем пароль"""
    safe_password = password[:72]
    return pwd_context.hash(safe_password)

def verify_password(password: str, hashed: str) -> bool:
    """Проверяем совпадает ли хешированный пароль в бд с введенным пользователем"""
    safe_password = password[:72]
    return pwd_context.verify(safe_password, hashed)