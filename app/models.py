from pydantic import BaseModel


class CardRequest(BaseModel):
    userId: int
    app_id: str
    cardType: str
    cardCategory: str
    cardBalance: float
    currency: str
    firstName: str
    lastName: str
    cardRequestId: int
    phone: str
