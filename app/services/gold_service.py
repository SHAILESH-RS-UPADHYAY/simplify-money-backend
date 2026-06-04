import httpx
from sqlalchemy.orm import Session
from app.models import GoldPurchase
from app.config import FALLBACK_GOLD_PRICE


def fetch_gold_price():
    """try to get live gold price, fall back to hardcoded if anything goes wrong"""
    try:
        # Fetch current USD to INR exchange rate
        usd_to_inr = 95.71  # Default fallback exchange rate
        try:
            fx_resp = httpx.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=3.0)
            if fx_resp.status_code == 200:
                rates = fx_resp.json().get("rates", {})
                usd_to_inr = rates.get("INR", 95.71)
        except Exception:
            pass  # Silently fall back to default if FX API fails

        # using a public gold price endpoint (no key needed)
        # this returns price per troy ounce in USD, we convert to INR per gram
        resp = httpx.get(
            "https://api.gold-api.com/price/XAU",
            timeout=5.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            usd_per_ounce = data.get("price", 0)
            if usd_per_ounce > 0:
                # conversion: 1 troy ounce = 31.1035g
                # add ~15% for Indian import duty + AIDC + GST
                inr_per_gram = (usd_per_ounce * usd_to_inr) / 31.1035
                inr_per_gram *= 1.15  # import duty + GST markup
                return round(inr_per_gram, 2)
    except Exception:
        pass  # any error -> use fallback

    return FALLBACK_GOLD_PRICE


def buy_gold(user_name: str, amount_inr: float, db: Session):
    """process a gold purchase and save it to the database"""

    if amount_inr <= 0:
        raise ValueError("Amount must be greater than zero")

    price_per_gram = fetch_gold_price()
    grams = round(amount_inr / price_per_gram, 4)

    purchase = GoldPurchase(
        user_name=user_name,
        amount_inr=amount_inr,
        gold_price_per_gram=price_per_gram,
        grams_purchased=grams,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return {
        "message": f"Gold purchase successful! {user_name} bought {grams}g of 24K digital gold.",
        "transaction_id": purchase.id,
        "user_name": purchase.user_name,
        "amount_inr": purchase.amount_inr,
        "gold_price_per_gram": purchase.gold_price_per_gram,
        "grams_purchased": purchase.grams_purchased,
        "purchased_at": purchase.created_at,
    }


def get_all_purchases(db: Session):
    return db.query(GoldPurchase).order_by(GoldPurchase.created_at.desc()).all()
