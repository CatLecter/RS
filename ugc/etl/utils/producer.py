import asyncio
from datetime import datetime
from random import choice
from uuid import uuid4

from ugc.ugc.src.db.kafka import get_event_broker
from ugc.ugc.src.engines.message_broker.kafka import KafkaProducerEngine


async def main():
    producer: KafkaProducerEngine = get_event_broker()  # type: ignore

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
