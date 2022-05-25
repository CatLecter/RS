from auth_api.extensions import db, ma
from auth_api.models.user import Role
from marshmallow_sqlalchemy import auto_field


class RoleSchema(ma.SQLAlchemyAutoSchema):
    uuid = auto_field(example="768b49ca-02d9-4524-9f13-3ac70f0cd7eb")
    name = auto_field(required=True, example="subscriber")

    class Meta:
        model = Role
        sqla_session = db.session
        load_instance = True
        fields = (
            "uuid",
            "name",
        )
        dump_only = ("uuid",)
