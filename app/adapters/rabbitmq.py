import json

import aio_pika
import logging
from app.config import Config


class RabbitMQAdapter:
    def __init__(self, config: Config):
        self.config = config
        self.connection = None
        self.channel = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                login=self.config.rabbitmq_username,
                password=self.config.rabbitmq_password,
                virtualhost=self.config.rabbitmq_vhost
            )
            self.channel = await self.connection.channel()
            logging.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logging.info("Disconnected from RabbitMQ")
        except Exception as e:
            logging.error(f"Error during RabbitMQ disconnection: {e}")

    async def consume(self, queue_name: str, callback):
        queue = await self.channel.declare_queue(queue_name, durable=True)
        logging.info(f"Starting to consume messages from queue: {queue_name}")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logging.info(f"Received message from queue: {queue_name}")
                try:
                    async with message.process():
                        await callback(json.loads(message.body), message.properties)
                    logging.info(f"Finished processing message from queue: {queue_name}")
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                    # продумать логику поведения при возникновении ошибки(повторная обработка? или отправка в очередь ошибок?

    async def publish(self, exchange: str, routing_key: str, message: str):
        exchange_instance = await self.channel.get_exchange(exchange)
        await exchange_instance.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=routing_key
        )
