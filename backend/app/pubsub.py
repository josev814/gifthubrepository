import os, json, asyncio
from typing import Callable, List

import aio_pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://rabbit:rabbit@rabbitmq:5672/")
EXCHANGE_NAME = "gift_events"

class PubSub:
    def __init__(self):
        self._connection = None
        self._channel = None
        self._exchange = None
        self._task = None
        self._callbacks: List[Callable[[dict], None]] = []

    async def connect(self):
        self._connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        self._exchange = await self._channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT, durable=True)

        queue = await self._channel.declare_queue(exclusive=True)
        await queue.bind(self._exchange)

        async def _consume():
            async with queue.iterator() as qi:
                async for message in qi:
                    async with message.process():
                        try:
                            payload = json.loads(message.body.decode())
                        except Exception:
                            payload = {"type":"raw","data":message.body.decode()}
                        for cb in list(self._callbacks):
                            try:
                                await cb(payload)
                            except Exception:
                                pass

        self._task = asyncio.create_task(_consume())

    async def publish(self, message: dict):
        if not self._exchange:
            await self.connect()
        body = json.dumps(message).encode()
        await self._exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
            routing_key=""
        )

    def register_callback(self, cb):
        self._callbacks.append(cb)
    
    async def close(self):
        if self._connection:
            await self._connection.close()

pubsub = PubSub()
