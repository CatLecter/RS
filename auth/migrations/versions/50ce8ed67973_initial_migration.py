"""Initial migration.

Revision ID: 50ce8ed67973
Revises:
Create Date: 2022-03-15 22:33:17.897089

"""
import auth_api
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "50ce8ed67973"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "roles",
        sa.Column("uuid", auth_api.models.custom_field_types.GUID(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("uuid", auth_api.models.custom_field_types.GUID(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=80), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "auth_history",
        sa.Column("uuid", auth_api.models.custom_field_types.GUID(), nullable=False),
        sa.Column(
            "user_uuid", auth_api.models.custom_field_types.GUID(), nullable=True
        ),
        sa.Column("user_agent", sa.String(length=200), nullable=False),
        sa.Column("device", sa.String(length=40), nullable=False),
        sa.Column("ip_address", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ("user_uuid",),
            ["users.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid", "device"),
        postgresql_partition_by="LIST (device)",
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_desktop PARTITION OF auth_history FOR VALUES IN ('desktop');"""
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_tablet PARTITION OF auth_history FOR VALUES IN ('tablet');"""
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_mobile PARTITION OF auth_history FOR VALUES IN ('mobile');"""
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS auth_history_other PARTITION OF auth_history FOR VALUES IN ('other');"""
    )

    op.create_table(
        "links_users_roles",
        sa.Column("uuid", auth_api.models.custom_field_types.GUID(), nullable=False),
        sa.Column(
            "users_uuid", auth_api.models.custom_field_types.GUID(), nullable=True
        ),
        sa.Column(
            "roles_uuid", auth_api.models.custom_field_types.GUID(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ("roles_uuid",),
            ["roles.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ("users_uuid",),
            ["users.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )


def downgrade():
    op.drop_table("links_users_roles")
    op.drop_table("auth_history")
    op.drop_table("auth_history_other")
    op.drop_table("auth_history_mobile")
    op.drop_table("auth_history_tablet")
    op.drop_table("auth_history_desktop")
    op.drop_table("users")
    op.drop_table("roles")
