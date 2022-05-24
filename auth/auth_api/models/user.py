import datetime
import uuid as uuid_

from auth_api.extensions import db, pwd_context
from auth_api.models.custom_field_types import GUID
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    """Basic user model"""

    __tablename__ = "users"

    uuid = db.Column(GUID(), primary_key=True, default=uuid_.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    roles = db.relationship(
        "Role",
        secondary="links_users_roles",
    )
    is_totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(255))
    social_id = db.Column(db.String(255))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = pwd_context.hash(value)

    def __repr__(self):
        return "<User %s>" % self.username


class Role(db.Model):
    __tablename__ = "roles"

    uuid = db.Column(GUID(), primary_key=True, default=uuid_.uuid4)
    name = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return "<Role %s>" % self.username


class UsersRoles(db.Model):
    __tablename__ = "links_users_roles"

    uuid = db.Column(GUID(), primary_key=True, default=uuid_.uuid4)
    users_uuid = db.Column(GUID(), db.ForeignKey("users.uuid"))
    roles_uuid = db.Column(GUID(), db.ForeignKey("roles.uuid"))


def create_auth_partition(target, connection, **kw) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_desktop PARTITION OF auth_history FOR VALUES IN ('desktop');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_tablet PARTITION OF auth_history FOR VALUES IN ('tablet');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_mobile PARTITION OF auth_history FOR VALUES IN ('mobile');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_other PARTITION OF auth_history FOR VALUES IN ('other');"""
    )


class AuthHistory(db.Model):
    __tablename__ = "auth_history"
    __table_args__ = (
        PrimaryKeyConstraint("uuid", "device"),
        {
            "postgresql_partition_by": "LIST (device)",
            "listeners": [("after_create", create_auth_partition)],
        },
    )

    uuid = db.Column(GUID(), default=uuid_.uuid4)
    user_uuid = db.Column(GUID(), db.ForeignKey("users.uuid"))
    user_agent = db.Column(db.String(200), nullable=False)
    device = db.Column(db.String(40), nullable=False)
    ip_address = db.Column(db.String(40), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
