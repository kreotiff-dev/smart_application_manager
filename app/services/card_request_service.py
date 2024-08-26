import json
import logging
from typing import Dict, Any
from app.models import CardRequest
from app.adapters.rabbitmq import RabbitMQAdapter
from app.adapters.http_client import HTTPClientAdapter


class CardRequestService:
    def __init__(self, config, http_client: HTTPClientAdapter, rabbitmq: RabbitMQAdapter):
        self.config = config
        self.http_client = http_client
        self.rabbitmq = rabbitmq
        self.logger = logging.getLogger(__name__)

    async def validate_request(self, data: Dict[str, Any]) -> bool:
        try:
            CardRequest(**data)
            return True
        except ValueError as e:
            self.logger.error(f"Invalid request data: {e}")
            return False

    async def send_approval(self, user_id: str, card_request_id: str):
        self.logger.info(f"Sending approval for user_id: {user_id}, card_request_id: {card_request_id}")

        message = {
            "userId": user_id,
            "cardRequestId": card_request_id,
            "status": "APPROVED"
        }

        try:
            await self.rabbitmq.publish(
                message=json.dumps(message),
                exchange=self.config.rabbitmq_exchange,
                routing_key=self.config.rabbitmq_approval_routing_key
            )
            self.logger.info("Approval message published successfully.")
        except Exception as e:
            self.logger.error(f"Failed to publish approval message: {e}", exc_info=True)

    async def generate_card_request(self, card_data: Dict[str, Any]):
        payload = {
            'user_id': card_data['userId'],
            'card_request_id': card_data['cardRequestId'],
            'phone': card_data['phone'],
            'card_type': card_data['cardType'],
            'card_category': card_data['cardCategory'],
            'card_balance': card_data['cardBalance'],
            'currency': card_data['currency'],
            'cardholder_firstname': card_data['firstName'],
            'cardholder_lastname': card_data['lastName']
        }

        await self.http_client.post(self.config.card_generation_url, json=payload)

    async def process_request(self, body, properties):
        self.logger.info("Received message. Starting processing.")
        try:
            self.logger.debug(f"Received body: {body}")
            self.logger.debug(f"Received properties: {properties}")

            if not await self.validate_request(body):
                self.logger.warning("Invalid request data. Skipping...")
                return

            card_data = CardRequest(**body).dict()
            self.logger.info(f"Validated card request data: {card_data}")

            await self.send_approval(
                card_data['userId'],
                card_data['cardRequestId']
            )
            self.logger.info("Approval sent to RabbitMQ")

            await self.generate_card_request(card_data)
            self.logger.info("Card request generated and sent to card generation service")

        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)

