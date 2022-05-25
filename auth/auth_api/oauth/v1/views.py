import uuid
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND

from auth_api.commons.jwt_utils import create_tokens
from auth_api.commons.oauth.clients import OAuthClient
from auth_api.commons.utils import generate_password, get_device_type
from auth_api.extensions import apispec, db
from auth_api.models import User
from auth_api.models.user import AuthHistory
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, request
from marshmallow import ValidationError

blueprint = Blueprint("oauth", __name__, url_prefix="/oauth/v1")


@blueprint.route("/providers", methods=["GET"])
def get_providers_list():
    """Получение списка поддерживаемых провайдеров для OAuth авторизации.

    ---
    get:
      tags:
        - oauth
      summary: Список поддерживаемых OAuth-провайдеров.
      description: Получение списка поддерживаемых провайдеров и их данных для OAuth авторизации.
      responses:
        200:
          description: Список провайдеров успешно получен.
          content:
            application/json:
              schema:
                type: object
                properties:
                  providers:
                    type: array
                    items:
                      type: string
                      example: yandex
        429:
          $ref: '#/components/responses/TooManyRequests'
      security: []
    """
    if OAuthClient.providers is None:
        OAuthClient.load_providers()
    providers = list(OAuthClient.providers.keys())
    providers_data = []
    for provider in providers:
        providers_data.append(
            {
                "name": provider,
                "properties": OAuthClient.get_provider(
                    provider
                ).get_data_for_authorize(),
            }
        )
    return jsonify({"providers": providers_data})


@blueprint.route("/login/<string:provider>", methods=["POST"])
def oauth_login(provider):
    """Аутентификация с помощью токена полученного от OAuth-провайдера.

    ---
    post:
      tags:
        - oauth
      summary: OAuth аутентификация.
      description: Аутентификация с помощью токена полученного от OAuth-провайдера.
      parameters:
        - in: path
          name: provider
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                  example: AAAAAAA00000000000-AAAAAA00000000000000
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
        404:
          $ref: '#/components/responses/NotFound'
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
    provider_oauth = OAuthClient.get_provider(provider)
    if not provider_oauth:
        return jsonify({"msg": "OAuth provider not found."}), NOT_FOUND

    user_info = provider_oauth.get_user_info()
    if not user_info:
        return jsonify({"msg": "Authentication failed."}), FORBIDDEN

    social_id = user_info["social_id"]
    email = user_info["email"]

    user = User.query.filter_by(social_id=social_id).first()
    if user is None:
        email_exist = User.query.filter_by(email=email).first()
        if email_exist:
            email = None

        user = User(
            username=f"Unknown-{uuid.uuid4()}",
            email=email,
            password=generate_password(),
            social_id=social_id,
        )
        db.session.add(user)
        db.session.commit()

    if not user.is_active:
        return jsonify({"msg": "Your account is blocked."}), FORBIDDEN

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


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Возвращает json-ошибку при ошибках валидации marshmallow.

    Это позволит избежать необходимости оборачивать в try/catch ошибки ValidationErrors во всех ендпоинтах, возвращая
    корректный json-ответ со статусом 400 (Bad Request).
    """
    return jsonify(e.messages), BAD_REQUEST


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=get_providers_list, app=app)
    apispec.spec.path(view=oauth_login, app=app)
