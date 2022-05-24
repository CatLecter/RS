from auth_api.extensions import db, ma
from auth_api.models.user import AuthHistory
from marshmallow_sqlalchemy import auto_field


class AuthHistorySchema(ma.SQLAlchemyAutoSchema):
    user_agent = auto_field(
        example="Chrome/98.0.4758.109 Safari/537.36 OPR/84.0.4316.31 (Edition Yx 05)"
    )
    ip_address = auto_field(example="127.0.0.1")
    date = auto_field("created_at", dump_only=True)
    device = auto_field(example="mobile")

    class Meta:
        model = AuthHistory
        sqla_session = db.session
        load_instance = True
        exclude = (
            "uuid",
            "created_at",
        )
