from typing import List, Optional, Union

from pydantic import BaseSettings, SecretStr


class KafkaConfig(BaseSettings):
    class Config:
        env_prefix = "KAFKA_"

    bootstrap_servers: Union[List[str], str] = "127.0.0.1"
    security_protocol: str = "SASL_SSL"
    sasl_mechanism: str = "SCRAM-SHA-512"
    sasl_plain_username: Optional[str]
    sasl_plain_password: Optional[SecretStr]
    ssl_cafile: Optional[str] = None
