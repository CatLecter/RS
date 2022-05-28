import asyncio
import ssl
from datetime import datetime
from random import choice
from typing import Any, Dict
from uuid import uuid4

from aiokafka import AIOKafkaProducer

from ugc.etl.config import KafkaConfig
from ugc.etl.utils import serializer


async def main():

    cfg = KafkaConfig

    params: Dict[str, Any] = dict(
        loop=asyncio.get_event_loop(),
        bootstrap_servers=cfg.bootstrap_servers,
        security_protocol=cfg.security_protocol,
        sasl_mechanism=cfg.sasl_mechanism,
        value_serializer=serializer,
    )
    if cfg.sasl_plain_username:
        params["sasl_plain_username"] = cfg.sasl_plain_username
    if cfg.sasl_plain_password:
        params["sasl_plain_password"] = cfg.sasl_plain_password.get_secret_value()
    if "SSL" in cfg.security_protocol:
        params["ssl_context"] = ssl.create_default_context(cafile=cfg.ssl_cafile)
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

    for _ in range(5):
        value = {
            "user_uuid": uuid4(),
            "movie_uuid": uuid4(),
            "datetime": datetime.now(),
            "liked": choice([1, 0]),
        }
        await producer.send("likes", value)
        print("Sent value:", value)
        await asyncio.sleep(1)

    await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
