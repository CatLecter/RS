import os

import click
from auth_api.extensions import db
from auth_api.models import User
from auth_api.models.user import Role
from flask.cli import with_appcontext
from sqlalchemy import or_


@click.command()
@click.option(
    "--username",
    "-u",
    help="Superuser name.",
)
@click.option(
    "--email",
    "-e",
    help="Superuser email.",
)
@click.option(
    "--password",
    "-p",
    help="Superuser password.",
)
@with_appcontext
def createsuperuser(username, email, password):
    """Создание суперпользователя."""

    if username is None:
        username = os.getenv("AUTHAPI_SUPERUSER_NAME")
    if email is None:
        email = os.getenv("AUTHAPI_SUPERUSER_EMAIL")
    if password is None:
        password = os.getenv("AUTHAPI_SUPERUSER_PASSWORD")

    new_superuser = User(
        username=username,
        email=email,
        password=password,
        is_active=True,
        is_superuser=True,
    )

    existing_superuser = User.query.filter(
        or_(User.username == new_superuser.username, User.email == new_superuser.email)
    ).first()

    if existing_superuser:
        click.echo(f"{new_superuser.username} ({new_superuser.email}) already created!")
        return
    db.session.add(new_superuser)
    db.session.commit()
    click.echo("Superuser created!")


@click.command()
@with_appcontext
def loaddata():
    """Инициализация базы данных."""
    roles = ["guest", "subscriber", "contributor", "editor", "administrator"]
    for role in roles:
        db.session.add(Role(name=role))
    db.session.commit()
    click.echo(f"Load roles: {len(roles)}")
