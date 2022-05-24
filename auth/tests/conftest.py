import json
from typing import Dict

import pytest
from auth_api.app import create_app
from auth_api.extensions import db as _db
from auth_api.models import User
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from pytest_factoryboy import register
from tests.factories import UserFactory

register(UserFactory)


@pytest.fixture(scope="session")
def app() -> Flask:
    app = create_app()
    return app


@pytest.fixture
def db(app: Flask) -> SQLAlchemy:
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def admin_user(db: SQLAlchemy) -> User:
    user = User(
        username="admin", email="admin@admin.com", password="admin", is_superuser=True
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def admin_headers(admin_user: User, client: FlaskClient) -> Dict:
    data = {"username": admin_user.username, "password": "admin"}
    rep = client.post(
        "/auth/login",
        data=json.dumps(data),
        headers={"content-type": "application/json"},
    )

    tokens = json.loads(rep.get_data(as_text=True))
    return {
        "content-type": "application/json",
        "authorization": "Bearer %s" % tokens["access_token"],
    }


@pytest.fixture
def admin_refresh_headers(admin_user: User, client: FlaskClient) -> Dict:
    data = {"username": admin_user.username, "password": "admin"}
    rep = client.post(
        "/auth/login",
        data=json.dumps(data),
        headers={"content-type": "application/json"},
    )

    tokens = json.loads(rep.get_data(as_text=True))
    return {
        "content-type": "application/json",
        "authorization": "Bearer %s" % tokens["refresh_token"],
    }
