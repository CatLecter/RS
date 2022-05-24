from pathlib import Path

from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    ELASTIC_HOST: str = Field("http://127.0.0.1", env="ELASTIC_HOST")
    ELASTIC_PORT: str = Field("9200", env="ELASTIC_PORT")
    REDIS_HOST: str = Field("127.0.0.1", env="REDIS_HOST")
    REDIS_PORT: str = Field("6379", env="REDIS_PORT")
    SERVICE_URL: str = Field("127.0.0.1", env="SERVICE_URL")
    SERVICE_PORT: str = Field("8000", env="SERVICE_PORT")

    expected_responses_dir: Path = Field(
        Path(__file__).parent.joinpath("testdata/expected")
    )
    indexes_dir: Path = Field(Path(__file__).parent.joinpath("testdata/indexes"))
    data_dir: Path = Field(Path(__file__).parent.joinpath("testdata/data_for_indexes"))

    class Config:
        env_file = ".env"


config: TestSettings = TestSettings()
