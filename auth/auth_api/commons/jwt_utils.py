import uuid as _uuid
from functools import wraps
from http.client import BAD_REQUEST, FORBIDDEN
from typing import Dict

from auth_api.commons.jaeger_utils import trace
from auth_api.extensions import active_refresh_tokens, blocked_access_tokens, settings
from auth_api.models import User
from flask import current_app, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    verify_jwt_in_request,
)


def user_has_role(*required_roles):
    """Декоратор, разрешающий использование ендпоинта только пользователям с определенной ролью."""

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            is_superuser = claims.get("is_superuser", False)
            if is_superuser:
                return fn(*args, **kwargs)
            roles = set(claims.get("roles", []))
            required = set(required_roles)
            if len(roles.intersection(required)) > 0:
                return fn(*args, **kwargs)
            else:
                return {"msg": "Access denied!"}, FORBIDDEN

        return decorator

    return wrapper


@trace
def create_tokens(user_uuid: _uuid.UUID) -> (str, str):
    """Возвращает access и refresh токены."""
    refresh_token = create_extended_refresh_token(user_uuid)
    refresh_uuid = get_uuid_from_encoded_refresh_token(refresh_token)
    access_token = create_extended_access_token(user_uuid, refresh_uuid)
    return access_token, refresh_token


@trace
def create_extended_access_token(user_uuid: _uuid.UUID, refresh_uuid: _uuid.UUID):
    """Возвращает access-токен с дополнительными данными."""
    user = User.query.get(user_uuid)
    if not user.is_active:
        return jsonify({"msg": "Your account is blocked."}), FORBIDDEN
    access_token = create_access_token(
        identity=user.uuid,
        additional_claims={
            "refresh_uuid": str(refresh_uuid),
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat(),
            "roles": [role.name for role in user.roles],
        },
    )
    return access_token


@trace
def create_extended_refresh_token(user_uuid: _uuid.UUID):
    """Возвращает refresh-токен с дополнительными данными."""
    refresh_token = create_refresh_token(identity=str(user_uuid))
    activate_refresh_token(refresh_token)
    return refresh_token


@trace
def activate_refresh_token(encoded_refresh_token: str):
    """Добавляет refresh-токен в базу активных refresh-токенов."""
    refresh_token = decode_token(encoded_refresh_token)
    refresh_uuid = get_token_uuid_from_token(refresh_token)
    user_uuid = get_user_uuid_from_token(refresh_token)
    active_refresh_tokens.sadd(user_uuid, refresh_uuid)
    active_refresh_tokens.expire(user_uuid, settings.jwt.refresh.expires)


@trace
def deactivate_access_token(access_token: Dict):
    """Добавляет access-токен в базу заблокированных access-токенов."""
    access_uuid = get_token_uuid_from_token(access_token)
    exp_time = get_token_exp_from_token(access_token)
    blocked_access_tokens.set(access_uuid, "", ex=exp_time)


@trace
def deactivate_refresh_token(refresh_token: Dict):
    """Удаляет refresh-токен из базы активных refresh-токенов."""
    refresh_uuid = get_token_uuid_from_token(refresh_token)
    user_uuid = get_user_uuid_from_token(refresh_token)
    active_refresh_tokens.srem(user_uuid, refresh_uuid)


@trace
def deactivate_refresh_token_by_access_token(access_token: Dict):
    """Блокирует refresh-токен связанный с access-токеном."""
    refresh_uuid = access_token["refresh_uuid"]
    user_uuid = get_user_uuid_from_token(access_token)
    active_refresh_tokens.srem(user_uuid, refresh_uuid)


@trace
def deactivate_all_refresh_tokens(user_uuid: str):
    """Удаляет все refresh-токены пользователя из базы активных refresh-токенов."""
    active_refresh_tokens.delete(str(user_uuid))


@trace
def get_uuid_from_encoded_refresh_token(encoded_refresh_token: str):
    """Возвращает uuid зашифрованного refresh-токена."""
    refresh_token = decode_token(encoded_refresh_token)
    refresh_uuid = get_token_uuid_from_token(refresh_token)
    return refresh_uuid


@trace
def get_user_uuid_from_token(token: Dict):
    """Возвращает UUID пользователя из JWT токена."""
    return token[current_app.config["JWT_IDENTITY_CLAIM"]]


@trace
def get_token_uuid_from_token(token: Dict):
    """Возвращает UUID токена из JWT токена."""
    return token["jti"]


@trace
def get_token_exp_from_token(token: Dict):
    """Возвращает время жизни токена из JWT токена."""
    return token["exp"]


@trace
def is_active_token(token: Dict):
    """Проверяет, активен ли переданный токен."""
    token_type = token["type"]
    if token_type == "access":
        return is_active_access_token(token)
    elif token_type == "refresh":
        return is_active_refresh_token(token)
    else:
        return jsonify({"msg": "Unknown token type."}), BAD_REQUEST


@trace
def is_active_refresh_token(refresh_token: Dict):
    """Проверяет, активен ли переданный refresh-токен."""
    refresh_uuid = get_token_uuid_from_token(refresh_token)
    user_uuid = get_user_uuid_from_token(refresh_token)
    return active_refresh_tokens.sismember(user_uuid, refresh_uuid)


@trace
def is_active_access_token(access_token: Dict):
    """Проверяет, активен ли переданный access-токен."""
    access_uuid = get_token_uuid_from_token(access_token)
    token_in_blocklist = blocked_access_tokens.get(access_uuid)
    return token_in_blocklist is None
