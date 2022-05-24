from http.client import BAD_REQUEST, CONFLICT, CREATED, FORBIDDEN

import pyotp
from auth_api.api.v1.schemas.user import UserSchema
from auth_api.commons.jwt_utils import (
    create_tokens,
    deactivate_access_token,
    deactivate_all_refresh_tokens,
    deactivate_refresh_token,
    deactivate_refresh_token_by_access_token,
    get_user_uuid_from_token,
    is_active_token,
)
from auth_api.commons.utils import get_device_type
from auth_api.extensions import apispec, db, jwt, pwd_context
from auth_api.models import User
from auth_api.models.user import AuthHistory
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from marshmallow import ValidationError
from sqlalchemy import or_

blueprint = Blueprint("auth", __name__, url_prefix="/auth/v1")


@blueprint.route("/signup", methods=["POST"])
def signup():
    """Регистрация пользователя.

    ---
    post:
      tags:
        - auth
      summary: Регистрация пользователя.
      description: Создает пользователя в базе данных.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: CoolUser
                password:
                  type: string
                  example: Super$ecret!
                email:
                  type: string
                  example: user@example.com
      responses:
        201:
          description: Регистрация прошла успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: User created.
                  user: UserSchema
        400:
          $ref: '#/components/responses/BadRequest'
        409:
          description: Такое имя пользователя или email уже существуют.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorMessage'
        429:
          $ref: '#/components/responses/TooManyRequests'
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request."}), BAD_REQUEST

    schema = UserSchema()
    user = schema.load(request.json)

    existing_user = User.query.filter(
        or_(User.username == user.username, User.email == user.email)
    ).first()
    if existing_user:
        return {"msg": "Username or email is already taken!"}, CONFLICT

    db.session.add(user)
    db.session.commit()

    return {"msg": "User created.", "user": schema.dump(user)}, CREATED


@blueprint.route("/login", methods=["POST"])
def login():
    """Аутентификация пользователя для получения токенов.

    ---
    post:
      tags:
        - auth
      summary: Аутентификация пользователя.
      description: Проверяет подлинность учетных данных пользователя и возвращает токены.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: CoolUser
                password:
                  type: string
                  example: Super$ecret!
                totp_code:
                  type: string
                  example: '123456'
              required:
                - username
                - password
      responses:
        200:
          description: Аутентификация прошла успешно.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Tokens'
        400:
          $ref: '#/components/responses/BadRequest'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
      security: []
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), BAD_REQUEST

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), BAD_REQUEST

    user = User.query.filter_by(username=username).first()

    if user is None or not pwd_context.verify(password, user.password):
        return jsonify({"msg": "Bad credentials."}), BAD_REQUEST

    if not user.is_active:
        return jsonify({"msg": "Your account is blocked."}), FORBIDDEN

    if user.is_totp_enabled:
        totp_code = request.json.get("totp_code", "")
        secret = user.two_factor_secret
        totp = pyotp.TOTP(secret)

        if not totp.verify(totp_code):
            return {"msg": "Wrong totp code."}, BAD_REQUEST

    db.session.add(
        AuthHistory(
            user_uuid=user.uuid,
            user_agent=request.user_agent.string,
            ip_address=request.remote_addr,
            device=get_device_type(request.user_agent.string),
        )
    )
    db.session.commit()

    access_token, refresh_token = create_tokens(user.uuid)
    ret = {"access_token": access_token, "refresh_token": refresh_token}
    return jsonify(ret)


@blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Получение новой пары токенов с помощью refresh-токена.

    ---
    post:
      tags:
        - auth
      summary: Получение новой пары токенов.
      description: Возвращает новую пару токенов с помощью refresh-токена переданного в заголовке `Authorization`.
      responses:
        200:
          description: Обновление токенов прошло успешно.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Tokens'
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    refresh_token = get_jwt()
    user_uuid = get_user_uuid_from_token(refresh_token)

    deactivate_refresh_token(refresh_token)

    access_token, refresh_token = create_tokens(user_uuid)
    ret = {"access_token": access_token, "refresh_token": refresh_token}
    return jsonify(ret)


@blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Выход из аккаунта.

    ---
    post:
      tags:
        - auth
      summary: Выход из аккаунта.
      description: Отзыв access и refresh токена.
      responses:
        200:
          description: Выход успешно осуществлен.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: You have been logged out.
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    access_token = get_jwt()
    deactivate_access_token(access_token)
    deactivate_refresh_token_by_access_token(access_token)

    return jsonify({"msg": "You have been logged out."})


@blueprint.route("/logout_all", methods=["POST"])
@jwt_required()
def logout_all():
    """Выход из всех аккаунтов.

    ---
    post:
      tags:
        - auth
      summary: Выход из всех аккаунтов
      description: Отзыв всех токенов авторизации.
      responses:
        200:
          description: Выход успешно осуществлен.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: You have been logged out from all devices.
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    access_token = get_jwt()
    deactivate_access_token(access_token)
    user_uuid = get_user_uuid_from_token(access_token)
    deactivate_all_refresh_tokens(user_uuid)
    return jsonify({"msg": "You have been logged out from all devices."})


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    return not is_active_token(jwt_payload)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Возвращает json-ошибку при ошибках валидации marshmallow.

    Это позволит избежать необходимости оборачивать в try/catch ошибки ValidationErrors во всех ендпоинтах, возвращая
    корректный json-ответ со статусом 400 (Bad Request).
    """
    return jsonify(e.messages), BAD_REQUEST


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=signup, app=app)
    apispec.spec.path(view=login, app=app)
    apispec.spec.path(view=refresh, app=app)
    apispec.spec.path(view=logout, app=app)
    apispec.spec.path(view=logout_all, app=app)
