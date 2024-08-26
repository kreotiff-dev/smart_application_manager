import asyncio
import logging
import signal
from config import Config
from app.services.card_request_service import CardRequestService
from app.adapters.rabbitmq import RabbitMQAdapter
from app.adapters.http_client import HTTPClientAdapter
from app.utils.logging import setup_logging


async def main():
    config = Config()
    setup_logging(config)
    consume_task = None

    logging.info("Config object created successfully!")
    logging.debug(f"Config values: {config.model_dump()}")

    http_client = HTTPClientAdapter(config)
    rabbitmq = RabbitMQAdapter(config)

    service = CardRequestService(config, http_client, rabbitmq)

    try:
        await rabbitmq.connect()
        logging.info("Successfully connected to RabbitMQ")

        consume_task = asyncio.create_task(
            rabbitmq.consume("card_application_requests", service.process_request)
        )
        logging.info("Started consuming messages from 'card_application_requests' queue")

        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

        await stop_event.wait()
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
    finally:
        if 'consume_task' in locals():
            consume_task.cancel()
            try:
                await consume_task
            except asyncio.CancelledError:
                pass
        await rabbitmq.disconnect()
        logging.info("Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
