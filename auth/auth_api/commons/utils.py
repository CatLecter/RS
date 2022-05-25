import secrets
import string
from datetime import datetime

from auth_api.extensions import rate_limiter_db, settings
from flask import request
from user_agents import parse


def get_device_type(user_agent: str) -> str:
    """Возвращает тип устройства пользователя на основе анализа user-agent."""
    user_agent = parse(user_agent)
    if user_agent.is_mobile:
        return "mobile"
    elif user_agent.is_tablet:
        return "tablet"
    elif user_agent.is_pc:
        return "desktop"
    else:
        return "other"


def is_rate_limit_exceeded():
    """Превышен ли лимит запросов с определенного ip?"""
    pipe = rate_limiter_db.pipeline()
    now = datetime.now()
    key = f"{request.remote_addr}:{now.minute}"
    pipe.incr(key, 1)
    pipe.expire(key, 59)
    result = pipe.execute()
    requests_number = result[0]
    return requests_number > settings.flask.requests_from_ip_per_minute


def generate_password(length=20):
    """Генерирует пароль."""
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits

    all_symbols = lower + upper + num
    password = ""
    for _ in range(length):
        password += secrets.choice(all_symbols)
    return password
