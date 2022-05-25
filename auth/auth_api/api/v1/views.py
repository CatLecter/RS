from http.client import BAD_REQUEST, CONFLICT

import pyotp
from auth_api.api.v1.resources.role import RoleList, RoleResource
from auth_api.api.v1.resources.user import MeResource, UserList, UserResource
from auth_api.api.v1.schemas.auth_history import AuthHistorySchema
from auth_api.api.v1.schemas.role import RoleSchema
from auth_api.api.v1.schemas.totp_request import TOTPRequestSchema
from auth_api.api.v1.schemas.user import UserSchema
from auth_api.commons.jwt_utils import get_user_uuid_from_token, user_has_role
from auth_api.commons.pagination import paginate
from auth_api.extensions import apispec, db
from auth_api.models.user import AuthHistory, Role, User
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restful import Api
from marshmallow import ValidationError

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(MeResource, "/users/me", endpoint="current_user")
api.add_resource(UserResource, "/users/<uuid:user_uuid>", endpoint="user_by_uuid")
api.add_resource(UserList, "/users", endpoint="users")

api.add_resource(RoleResource, "/roles/<uuid:role_uuid>", endpoint="role_by_uuid")
api.add_resource(RoleList, "/roles", endpoint="roles")


@blueprint.route("/users/me/history", methods=["GET"])
@jwt_required()
def get_self_history():
    """Получение истории своих логинов.

    ---
    get:
      tags:
        - api/users/me
      summary: Получение истории своих логинов.
      description: Возвращает список всех своих логинов.
      responses:
        200:
          description: История логинов получена успешно.
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items: AuthHistorySchema
        401:
          $ref: '#/components/responses/Unauthorized'
    """
    token = get_jwt()
    user_uuid = token["user_uuid"]
    auth_history = AuthHistory.query.filter_by(user_uuid=user_uuid).order_by(
        AuthHistory.created_at.desc()
    )
    schema = AuthHistorySchema(many=True)

    return paginate(auth_history, schema)


@blueprint.route("/users/me/totp/link", methods=["GET"])
@jwt_required()
def get_totp_link():
    """Получение totp ссылки.

    ---
    get:
      tags:
        - api/users/me/totp
      summary: Получение totp ссылки.
      description: Возвращает totp_link.
      responses:
        200:
          description: totp_link получена успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  totp_link:
                    type: string
                    example: otpauth://totp/PractixMovie:admin?secret=33HCRQNTDON7YD...
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    token = get_jwt()
    user_uuid = get_user_uuid_from_token(token)

    user = User.query.filter_by(uuid=user_uuid).first()
    if user.two_factor_secret is None:
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        db.session.commit()
    else:
        secret = user.two_factor_secret

    totp = pyotp.TOTP(secret)
    provisioning_url = totp.provisioning_uri(
        name=user.username, issuer_name="PractixMovie"
    )

    return {"totp_link": provisioning_url}


@blueprint.route("/users/me/totp/change_status", methods=["PUT"])
@jwt_required()
def change_totp_status():
    """Изменение статуса двухфакторной аутентификации.

    ---
    put:
      tags:
        - api/users/me/totp
      summary: Активация, деактивация totp.
      description: Позволяет включить или выключить двухфакторную аутентификацию.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                totp_code:
                  type: string
                  example: '123456'
                totp_status:
                  type: boolean
      responses:
        200:
          description: totp_status изменён успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Totp status changed.
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        409:
          description: Данный статус уже установлен.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: This status has already been established.
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    token = get_jwt()
    user_uuid = get_user_uuid_from_token(token)

    user = User.query.filter_by(uuid=user_uuid).first()
    schema = TOTPRequestSchema()
    totp_request = schema.load(request.json)
    totp_status = totp_request.get("totp_status")
    totp_code = totp_request.get("totp_code")

    if totp_status == user.is_totp_enabled:
        return {"msg": "This status has already been established."}, CONFLICT

    secret = user.two_factor_secret
    totp = pyotp.TOTP(secret)

    if not totp.verify(totp_code):
        return {"msg": "Wrong totp code."}, BAD_REQUEST

    user.is_totp_enabled = totp_status
    db.session.commit()

    return {"msg": f"Totp status changed to: {totp_status}"}


@blueprint.route("/users/<uuid:user_uuid>/history", methods=["GET"])
@user_has_role("administrator", "editor")
def get_user_history(user_uuid):
    """Получение истории логинов пользователя.

    ---
    get:
      tags:
        - api/users
      summary: Получение истории логинов пользователя.
      description: Возвращает список всех логинов конкретного пользователя заданного по `uuid`.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
      responses:
        200:
          description: История логинов получена успешно.
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResult'
                  - type: object
                    properties:
                      results:
                        type: array
                        items: AuthHistorySchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    auth_history = AuthHistory.query.filter_by(user_uuid=user_uuid)
    schema = AuthHistorySchema(many=True)

    return paginate(auth_history, schema)


@blueprint.route("/users/me/roles", methods=["GET"])
@jwt_required()
def get_self_roles():
    """Получение списка своих ролей.

    ---
    get:
      tags:
        - api/users/me
      summary: Получение списка своих ролей.
      description: Возвращает список всех своих ролей.
      responses:
        200:
          description: Список ролей получен успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  roles:
                    type: array
                    items: RoleSchema
        401:
          $ref: '#/components/responses/Unauthorized'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    token = get_jwt()
    roles = token["roles"]
    return {"roles": roles}


@blueprint.route("/users/<uuid:user_uuid>/roles", methods=["GET"])
@user_has_role("administrator", "editor")
def get_user_roles(user_uuid):
    """Получение ролей пользователя.

    ---
    get:
      tags:
        - api/users
      summary: Получение ролей пользователя.
      description: Возвращает список ролей конкретного пользователя заданного по `uuid`.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
      responses:
        200:
          description: Список ролей успешно получен.
          content:
            application/json:
              schema:
                type: object
                properties:
                  roles:
                    type: array
                    items: RoleSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
    """
    user = User.query.get_or_404(user_uuid)
    schema = RoleSchema(many=True)

    return {"roles": schema.dump(user.roles)}


@blueprint.route(
    "/users/<uuid:user_uuid>/roles/<uuid:role_uuid>", methods=["PUT", "DELETE"]
)
@user_has_role("administrator")
def user_roles(user_uuid, role_uuid):
    """Изменение ролей пользователя.

    ---
    put:
      tags:
        - api/users
      summary: Добавление роли пользователю.
      description: Позволяет добавлять роли пользователю.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
        - in: path
          name: role_uuid
          schema:
            type: string
      responses:
        200:
          description: Добавление роли прошло успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  roles:
                    type: array
                    items: RoleSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        429:
          $ref: '#/components/responses/TooManyRequests'
    delete:
      tags:
        - api/users
      summary: Удаление роли у пользователя.
      description: Позволяет удалить роль у пользователя.
      parameters:
        - in: path
          name: user_uuid
          schema:
            type: string
        - in: path
          name: role_uuid
          schema:
            type: string
      responses:
        200:
          description: Удаление роли прошло успешно.
          content:
            application/json:
              schema:
                type: object
                properties:
                  roles:
                    type: array
                    items: RoleSchema
        400:
          $ref: '#/components/responses/BadRequest'
        401:
          $ref: '#/components/responses/Unauthorized'
        403:
          $ref: '#/components/responses/AccessDenied'
        409:
          description: У данного пользователя нет этой роли.
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: The user does not have this role.
        429:
          $ref: '#/components/responses/TooManyRequests'
    """

    user = User.query.get_or_404(user_uuid)
    role = Role.query.get_or_404(role_uuid)

    if request.method == "PUT":
        user.roles.append(role)
    elif request.method == "DELETE":
        if role in user.roles:
            user.roles.remove(role)
        else:
            return {"msg": "The user does not have this role."}, CONFLICT

    db.session.add(user)
    db.session.commit()

    schema = RoleSchema(many=True)
    return {"roles": schema.dump(user.roles)}


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
    apispec.spec.path(view=RoleResource, app=current_app)
    apispec.spec.path(view=RoleList, app=current_app)
    apispec.spec.path(view=get_self_history, app=current_app)
    apispec.spec.path(view=get_self_roles, app=current_app)
    apispec.spec.path(view=get_user_history, app=current_app)
    apispec.spec.path(view=get_user_roles, app=current_app)
    apispec.spec.path(view=get_totp_link, app=current_app)
    apispec.spec.path(view=change_totp_status, app=current_app)
    apispec.spec.path(view=user_roles, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Возвращает json-ошибку при ошибках валидации marshmallow.

    Это позволит избежать необходимости оборачивать в try/catch ошибки
    ValidationErrors во всех ендпоинтах, возвращая
    корректный json-ответ со статусом 400 (Bad Request).
    """
    return jsonify(e.messages), BAD_REQUEST


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("TOTPRequestSchema", schema=TOTPRequestSchema)
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.components.schema("RoleSchema", schema=RoleSchema)
    apispec.spec.path(view=MeResource, app=current_app)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
