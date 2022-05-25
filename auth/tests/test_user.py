import uuid
from http.client import BAD_REQUEST, CREATED, NOT_FOUND, OK

from auth_api.extensions import pwd_context
from auth_api.models import User
from flask import url_for
from sqlalchemy import and_


def test_get_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for("api.user_by_uuid", user_uuid=str(uuid.uuid4()))
    rep = client.get(user_url, headers=admin_headers)
    assert rep.status_code == NOT_FOUND

    db.session.add(user)
    db.session.commit()

    # test get_user
    user_url = url_for("api.user_by_uuid", user_uuid=user.uuid)
    rep = client.get(user_url, headers=admin_headers)
    assert rep.status_code == OK

    data = rep.get_json()["user"]
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_put_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for("api.user_by_uuid", user_uuid=str(uuid.uuid4()))
    rep = client.put(user_url, headers=admin_headers)
    assert rep.status_code == NOT_FOUND

    db.session.add(user)
    db.session.commit()

    data = {"username": "updated", "password": "new_password"}

    user_url = url_for("api.user_by_uuid", user_uuid=user.uuid)
    # test update user
    rep = client.put(user_url, json=data, headers=admin_headers)
    assert rep.status_code == OK

    data = rep.get_json()["user"]
    assert data["username"] == "updated"
    assert data["email"] == user.email

    db.session.refresh(user)
    assert pwd_context.verify("new_password", user.password)


def test_delete_user(client, db, user, admin_headers):
    # test 404
    user_url = url_for("api.user_by_uuid", user_uuid=str(uuid.uuid4()))
    rep = client.delete(user_url, headers=admin_headers)
    assert rep.status_code == NOT_FOUND

    db.session.add(user)
    db.session.commit()

    # test get_user

    user_url = url_for("api.user_by_uuid", user_uuid=user.uuid)
    rep = client.delete(user_url, headers=admin_headers)
    assert rep.status_code == OK
    assert (
        db.session.query(User)
        .filter(and_(User.uuid == user.uuid, User.is_active is True))
        .first()
        is None
    )


def test_create_user(client, db, admin_headers):
    # test bad data
    users_url = url_for("api.users")
    data = {"username": "created"}
    rep = client.post(users_url, json=data, headers=admin_headers)
    assert rep.status_code == BAD_REQUEST

    data["password"] = "admin6"
    data["email"] = "create@mail.com"

    rep = client.post(users_url, json=data, headers=admin_headers)
    assert rep.status_code == CREATED

    data = rep.get_json()
    user = db.session.query(User).filter_by(uuid=data["user"]["uuid"]).first()

    assert user.username == "created"
    assert user.email == "create@mail.com"


def test_get_all_user(client, db, user_factory, admin_headers):
    users_url = url_for("api.users")
    users = user_factory.create_batch(30)

    db.session.add_all(users)
    db.session.commit()

    rep = client.get(users_url, headers=admin_headers)
    assert rep.status_code == OK

    results = rep.get_json()
    for user in users:
        assert any(str(u["uuid"]) == str(user.uuid) for u in results["results"])
