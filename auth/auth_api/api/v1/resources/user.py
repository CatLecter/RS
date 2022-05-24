from http.client import CONFLICT, CREATED

from auth_api.api.v1.schemas.user import UserSchema
from auth_api.commons.jwt_utils import (
    create_extended_access_token,
    deactivate_access_token,
    deactivate_all_refresh_tokens,
    get_user_uuid_from_token,
    user_has_role,
)
from auth_api.commons.pagination import paginate
from auth_api.extensions import db
from auth_api.models import User
from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restful import Resource
from sqlalchemy import or_


class MeResource(Resource):
    """Ресурс представляющий текущего пользователя (на основе access-токена).

    ---
    get:
      tags:
        - api/users/me
      summary: Получить данные о себе.
      description: Возвращает данные о текущем пользователе на основе access-токена.
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                  type: object
                  properties:
                    user: UserSchema
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    put:
      tags:
        - api/users/me
      summary: Обновить свои данные (username, password, email).
      description: Обновляет данные текущего пользователя на основе access-токена.
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Update is successful. Please use new access_token.
                  user: UserSchema
                  access_token:
                    type: string
                    example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    delete:
      tags:
        - api/users/me
      summary: Удалить (заблокировать) свой аккаунт.
      description: Удаляет (блокирует) аккаунт на основе access-токена.
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Your account has been blocked.
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """

    method_decorators = [jwt_required()]

    def get(self):
        access_token = get_jwt()
        user_data = {
            "uuid": access_token["user_uuid"],
            "username": access_token["username"],
            "email": access_token["email"],
            "is_superuser": access_token["is_superuser"],
            "created_at": access_token["created_at"],
            "roles": access_token["roles"],
        }
        return {"user": user_data}

    def put(self):
        access_token = get_jwt()
        user_uuid = get_user_uuid_from_token(access_token)
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_uuid)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        deactivate_access_token(access_token)
        refresh_uuid = access_token["refresh_uuid"]
        new_access_token = create_extended_access_token(user_uuid, refresh_uuid)

        return {
            "msg": "Update is successful. Please use new access_token.",
            "user": schema.dump(user),
            "access_token": new_access_token,
        }

    def delete(self):
        access_token = get_jwt()
        user_uuid = get_user_uuid_from_token(access_token)
        user = User.query.get(user_uuid)
        user.is_active = False
        db.session.commit()

        deactivate_access_token(access_token)
        deactivate_all_refresh_tokens(user_uuid)
        return {"msg": "Your account has been blocked."}


class UserResource(Resource):
    """Ресурс представляющий единичного пользователя.

    ---
    get:
      tags:
        - api/users
      summary: Получить данные о пользователе.
      description: Возвращает данные о пользователе по его UUID.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  user: UserSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        404:
          $ref: '#/components/responses/NotFound'
        429:
          $ref: '#/components/responses/TooManyRequests'
    put:
      tags:
        - api/users
      summary: Обновить данные пользователя (username, password, email).
      description: Обновляет данные пользователя по его UUID.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: user updated
                  user: UserSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        404:
          $ref: '#/components/responses/NotFound'
        429:
          $ref: '#/components/responses/TooManyRequests'
    delete:
      tags:
        - api/users
      summary: Удалить (заблокировать) пользователя.
      description: Удаляет (блокирует) аккаунт по его UUID.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: User has been blocked.
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        404:
          $ref: '#/components/responses/NotFound'
        409:
          description: Пользователь уже удален (заблокирован).
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: The user is already blocked.
        429:
          $ref: '#/components/responses/TooManyRequests'
    """

    @user_has_role("administrator", "editor")
    def get(self, user_uuid):
        schema = UserSchema()
        user = User.query.get_or_404(user_uuid)
        return {"user": schema.dump(user)}

    @user_has_role("administrator")
    def put(self, user_uuid):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_uuid)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        return {"msg": "Update is successful.", "user": schema.dump(user)}

    @user_has_role("administrator")
    def delete(self, user_uuid):
        user = User.query.get_or_404(user_uuid)
        if not user.is_active:
            return {"msg": "The user is already blocked."}, CONFLICT

        user.is_active = False
        db.session.commit()

        deactivate_all_refresh_tokens(user_uuid)
        return {"msg": "User has been blocked."}


class UserList(Resource):
    """Ресурс создания и получения списка всех пользователей.

    ---
    get:
      tags:
        - api/users
      summary: Получить список пользователей.
      description: Возвращает список всех активных пользователей из базы.
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items:
                          $ref: '#/components/schemas/UserSchema'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
    post:
      tags:
        - api/users
      summary: Создать нового пользователя.
      description: Создает нового пользователя на основе переданных данных.
      requestBody:
        content:
          application/json:
            schema:
              UserSchema
      responses:
        201:
          description: Объект создан
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
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        409:
          description: Пользователь уже существует.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Username or email is already taken!
        429:
          $ref: '#/components/responses/TooManyRequests'
    """

    @user_has_role("administrator", "editor")
    def get(self):
        schema = UserSchema(many=True)
        query = User.query.filter_by(is_active=True)
        return paginate(query, schema)

    @user_has_role("administrator")
    def post(self):
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
