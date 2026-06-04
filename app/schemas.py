from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---- chat endpoint ----

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # to keep track of conversation


class ChatResponse(BaseModel):
    reply: str
    wants_to_buy: bool = False  # true when user agrees to purchase
    session_id: str


# ---- gold purchase endpoint ----

class GoldBuyRequest(BaseModel):
    user_name: str
    amount_inr: float  # how much rupees to spend


class GoldBuyResponse(BaseModel):
    message: str
    transaction_id: int
    user_name: str
    amount_inr: float
    gold_price_per_gram: float
    grams_purchased: float
    purchased_at: datetime
