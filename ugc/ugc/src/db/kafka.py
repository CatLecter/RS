import asyncio
import logging
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer

from ..core.config import KafkaConfig
from ..engines.message_broker.general import GeneralProducerEngine
from ..engines.message_broker.kafka import KafkaProducerEngine
from .utils import serializer

logger = logging.getLogger(__name__)
event_broker: Optional[GeneralProducerEngine] = None


async def get_event_broker() -> GeneralProducerEngine:
    global event_broker
    if not event_broker:
        cfg = KafkaConfig()
        params: Dict[str, Any] = dict(
            loop=asyncio.get_event_loop(),
            bootstrap_servers=cfg.bootstrap_servers,
            value_serializer=serializer,
        )
        kafka_producer = AIOKafkaProducer(**params)
        await kafka_producer.start()
        event_broker = KafkaProducerEngine(producer=kafka_producer)
    return event_broker
