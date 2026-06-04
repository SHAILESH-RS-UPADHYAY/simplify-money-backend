from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.schemas import ChatRequest, ChatResponse, GoldBuyRequest, GoldBuyResponse
from app.services import chat_service, gold_service

# create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Simplify Money Gold AI",
    description="AI-powered gold investment assistant inspired by Kuber AI",
    version="1.0.0",
)

# add CORS middleware so frontend can call these APIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Simplify Money Gold AI is running. Visit /docs to try the API."}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Chat with the AI gold advisor. It remembers your conversation."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        result = chat_service.chat(req.message, req.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/buy-gold", response_model=GoldBuyResponse)
def buy_gold_endpoint(req: GoldBuyRequest, db: Session = Depends(get_db)):
    """Buy digital gold. Specify your name and amount in INR."""
    try:
        result = gold_service.buy_gold(req.user_name, req.amount_inr, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")


@app.get("/purchases")
def get_purchases(db: Session = Depends(get_db)):
    """Get all gold purchases."""
    purchases = gold_service.get_all_purchases(db)
    return {"total": len(purchases), "purchases": purchases}


@app.get("/gold-price")
def get_gold_price():
    price = gold_service.fetch_gold_price()
    return {"gold_price_per_gram_inr": price, "unit": "INR/gram", "purity": "24K"}
