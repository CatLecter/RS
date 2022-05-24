from http.client import CONFLICT, CREATED

from auth_api.api.v1.schemas.role import RoleSchema
from auth_api.commons.jwt_utils import user_has_role
from auth_api.extensions import db
from auth_api.models.user import Role
from flask import request
from flask_restful import Resource


class RoleResource(Resource):
    """Ресурс представляющий роль пользователя.

    ---
    get:
      tags:
        - api/roles
      summary: Получить данные о роли.
      description: Возвращает данные о роли по ее UUID.
      parameters:
        - in: path
          name: role_uuid
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
                  role: RoleSchema
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
        - api/roles
      summary: Обновить данные роли.
      description: Обновляет данные роли по ее UUID.
      parameters:
        - in: path
          name: role_uuid
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              RoleSchema
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
                    example: Role updated.
                  role: RoleSchema
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
        - api/roles
      summary: Удалить роль.
      description: Удаляет роль по ее UUID.
      parameters:
        - in: path
          name: role_uuid
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
                    example: Role deleted.
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
    """

    @user_has_role("administrator", "editor")
    def get(self, name):
        schema = RoleSchema()
        role = Role.query.filter_by(name=name).first()
        return {"role": schema.dump(role)}

    @user_has_role("administrator")
    def put(self, name):
        schema = RoleSchema(partial=True)
        role = Role.query.filter_by(name=name).first()
        role = schema.load(request.json, instance=role)

        db.session.commit()

        return {"msg": "Role updated.", "role": schema.dump(role)}

    @user_has_role("administrator")
    def delete(self, name):
        role = Role.query.filter_by(name=name).first()
        db.session.delete(role)
        db.session.commit()

        return {"msg": "Role deleted."}


class RoleList(Resource):
    """Ресурс создания и получения списка всех ролей.

    ---
    get:
      tags:
        - api/roles
      summary: Получить список ролей.
      description: Возвращает список всех ролей из базы.
      responses:
        200:
          description: Успех
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      $ref: '#/components/schemas/RoleSchema'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
    post:
      tags:
        - api/roles
      summary: Создать новую роль.
      description: Создает новую роль.
      requestBody:
        content:
          application/json:
            schema:
              RoleSchema
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
                    example: Role created.
                  role: RoleSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        409:
          description: Роль уже существует.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Role already exist!
        429:
          $ref: '#/components/responses/TooManyRequests'
    """

    @user_has_role("administrator", "editor")
    def get(self):
        schema = RoleSchema(many=True)
        roles = Role.query.all()
        return {"roles": schema.dump(roles)}

    @user_has_role("administrator")
    def post(self):
        schema = RoleSchema()
        role = schema.load(request.json)

        existing_role = Role.query.filter_by(name=role.name).first()
        if existing_role:
            return {"msg": "Role already exist!"}, CONFLICT

        db.session.add(role)
        db.session.commit()

        return {"msg": "Role created.", "role": schema.dump(role)}, CREATED
