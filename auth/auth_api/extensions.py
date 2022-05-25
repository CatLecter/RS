import redis
from auth_api.commons.apispec import APISpecExt
from auth_api.commons.flask_opentracing import FlaskTracing
from auth_api.settings.settings import Settings
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jaeger_client import Config
from passlib.context import CryptContext

settings = Settings()
db = SQLAlchemy()
jwt = JWTManager()
blocked_access_tokens = redis.Redis(
    host=settings.redis.host, port=settings.redis.port, db=1, decode_responses=True
)
active_refresh_tokens = redis.Redis(
    host=settings.redis.host, port=settings.redis.port, db=2, decode_responses=True
)
rate_limiter_db = redis.Redis(
    host=settings.redis.host, port=settings.redis.port, db=3, decode_responses=True
)
ma = Marshmallow()
migrate = Migrate()
apispec = APISpecExt()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


def setup_jaeger():
    config = Config(
        config={
            "sampler": {
                "type": "const",
                "param": 1,
            },
            "local_agent": {
                "reporting_host": settings.jaeger.host,
                "reporting_port": settings.jaeger.port,
            },
            "logging": True,
        },
        service_name="auth-api",
        validate=True,
    )
    return config.initialize_tracer()


tracer = setup_jaeger()

tracing = FlaskTracing(tracer)
