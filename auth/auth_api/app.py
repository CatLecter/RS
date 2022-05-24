from auth_api import manage
from auth_api.api.v1.views import blueprint as api_blueprint
from auth_api.auth.v1.views import blueprint as auth_blueprint
from auth_api.commons.fast_json import ORJSONDecoder, ORJSONEncoder
from auth_api.extensions import apispec, db, jwt, migrate, settings, tracing
from auth_api.oauth.v1.views import blueprint as oauth_blueprint
from auth_api.settings.settings import Settings
from flask import Flask


def create_app():
    """Application factory, used to create application"""
    app = Flask("auth_api")

    configure_app(app, settings)
    configure_extensions(app)
    configure_cli(app)
    configure_apispec(app)
    register_blueprints(app)

    return app


def configure_app(app, app_settings: Settings):
    app.json_encoder = ORJSONEncoder
    app.json_decoder = ORJSONDecoder
    app.config["DEBUG"] = app_settings.flask.debug
    app.config["TESTING"] = app_settings.flask.testing
    app.config["SECRET_KEY"] = app_settings.flask.secret_key

    app.config["JWT_IDENTITY_CLAIM"] = app_settings.jwt.identity_claim
    app.config["JWT_SECRET_KEY"] = app_settings.jwt.secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = app_settings.jwt.access.expires
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = app_settings.jwt.refresh.expires

    app.config["SQLALCHEMY_DATABASE_URI"] = app_settings.alchemy.database_uri
    app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = app_settings.alchemy.track_modifications

    # app.before_request(before_request)


# def before_request():
#     # Для логирования в Jaeger нам требуется $request_id,
#     #  это простая защита, чтобы nginx не забыли настроить правильно.
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         raise RuntimeError('Header "X-Request-Id" is required!')
#
#     # Ограничение количества запросов
#     if is_rate_limit_exceeded():
#         return jsonify({'msg': 'Too many requests.'}), TOO_MANY_REQUESTS


def configure_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    tracing.init_app(app)


def configure_cli(app):
    app.cli.add_command(manage.createsuperuser)
    app.cli.add_command(manage.loaddata)


def configure_apispec(app):
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer", "example": 9},
                "pages": {"type": "integer", "example": 1},
                "next": {
                    "type": "string",
                    "example": "/path/to/endpoint?page=1&per_page=50",
                },
                "prev": {
                    "type": "string",
                    "example": "/path/to/endpoint?page=1&per_page=50",
                },
            }
        },
    )
    apispec.spec.components.schema(
        "Tokens",
        {
            "properties": {
                "access_token": {
                    "type": "string",
                    "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                },
                "refresh_token": {
                    "type": "string",
                    "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                },
            }
        },
    )
    apispec.spec.components.schema(
        "Message",
        {
            "type": "object",
            "properties": {
                "msg": {"type": "string", "example": "Сообщение пользователю."},
            },
        },
    )
    apispec.spec.components.schema(
        "ErrorMessage",
        {
            "type": "object",
            "properties": {
                "msg": {"type": "string", "example": "Подробности ошибки."},
            },
        },
    )
    apispec.spec.components.response(
        "BadRequest",
        {
            "description": "Ошибка в переданных данных. Подробности в тексте ошибки.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorMessage",
                    },
                },
            },
        },
    )
    apispec.spec.components.response(
        "Unauthorized",
        {
            "description": "Ошибка авторизации.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorMessage",
                    },
                },
            },
        },
    )
    apispec.spec.components.response(
        "AccessDenied",
        {
            "description": "Доступ запрещён.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorMessage",
                    },
                },
            },
        },
    )
    apispec.spec.components.response(
        "NotFound",
        {
            "description": "Объект не найден.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorMessage",
                    },
                },
            },
        },
    )
    apispec.spec.components.response(
        "TooManyRequests",
        {
            "description": "Превышен лимит запросов.",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorMessage",
                    },
                },
            },
        },
    )


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(oauth_blueprint)
    app.register_blueprint(api_blueprint)
