from auth_api.api.v1.schemas.role import RoleSchema
from auth_api.extensions import db, ma
from auth_api.models import User
from marshmallow.validate import Length
from marshmallow_sqlalchemy import auto_field


class UserSchema(ma.SQLAlchemyAutoSchema):
    uuid = auto_field(example="768b49ca-02d9-4524-9f13-3ac70f0cd7eb")
    username = auto_field(required=True, example="CoolUser")
    password = ma.String(required=True, load_only=True, validate=Length(min=6, max=20))
    email = ma.Email(required=True, validate=Length(max=80))
    roles = ma.Nested(RoleSchema, many=True)
    is_totp_enabled = ma.Boolean(required=False)

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        fields = (
            "uuid",
            "username",
            "password",
            "email",
            "is_active",
            "is_superuser",
            "created_at",
            "roles",
            "is_totp_enabled",
        )
        dump_only = (
            "uuid",
            "is_active",
            "is_superuser",
            "created_at",
            "roles",
            "is_totp_enabled",
        )
