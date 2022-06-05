import sqlalchemy as db
from sqlalchemy import Column, Integer, MetaData, String, Table

engine = db.create_engine("sqlite:///event_generator/db/users.db", echo=True)

TABLE_NAME = "users_test"

META_DATA = MetaData(bind=engine.connect())
META_DATA.reflect()
metadata = MetaData(engine)
if not engine.dialect.has_table(engine.connect(), TABLE_NAME):

    users = Table(
        TABLE_NAME,
        metadata,
        Column("Id", Integer, primary_key=True, nullable=False),
        Column("login", String),
        Column("password", String),
        Column("email", String),
        Column("token_1", String),
        Column("token_2", String),
    )

    metadata.create_all(engine)
else:
    users = META_DATA.tables[TABLE_NAME]
