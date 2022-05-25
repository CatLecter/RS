import os
from functools import lru_cache
from pathlib import Path
from typing import Any, List

import yaml
from pydantic import BaseSettings
from pydantic.types import FilePath
from yaml import Loader

settings_path = Path(__file__).parent / "settings.yaml"
with settings_path.open("r") as f:
    yaml_settings = yaml.load(f, Loader=Loader)


class Elastic(BaseSettings):
    host: str
    port: int


class PostgressDsn(BaseSettings):
    host: str
    port: int
    dbname: str
    user: str
    password: str
    options: str


class Queries(BaseSettings):
    extract: FilePath
    enrich: FilePath


class ETLTaskPG(BaseSettings):
    table: str
    queries: Queries


class ETLTaskES(BaseSettings):
    index: str
    mapping: FilePath
    settings: FilePath


class ETLTask(BaseSettings):
    chunk_size: int
    data_class: Any
    pg: ETLTaskPG
    es: ETLTaskES


class Settings(BaseSettings):
    cycles_delay: int

    elastic: Elastic
    postgress_dsn: PostgressDsn
    etl_tasks: List[ETLTask]


@lru_cache()
def get_settings() -> Settings:
    settings = Settings(**yaml_settings)
    settings.postgress_dsn.user = os.environ["POSTGRES_USER"]
    settings.postgress_dsn.password = os.environ["POSTGRES_PASSWORD"]
    return settings
