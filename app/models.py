from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base


class GoldPurchase(Base):
    __tablename__ = "gold_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    amount_inr = Column(Float, nullable=False)  # how much they paid
    gold_price_per_gram = Column(Float, nullable=False)
    grams_purchased = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="success")
