# 🪙 Simplify Money — Gold Investment AI Backend

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)

> **🚀 Live Demo:** [https://simplify-money-backend.onrender.com/docs](https://simplify-money-backend.onrender.com/docs)
>
> Open the link above to interact with the API directly via Swagger UI. No setup required.

An AI-powered conversational backend for digital gold investment, inspired by Kuber AI. Users can chat with an AI financial advisor that understands purchase intent, fetches live gold prices, and logs transactions — all through a REST API.

---

## How It Works

**Request lifecycle:**
> `User Query` ➜ `FastAPI Router` ➜ `LangChain (Session Memory)` ➜ `Gemini 1.5 Flash` ➜ `Intent Parser` ➜ `Execution`

1. User sends a message to `/chat` (e.g. *"I want to invest 5000 in gold"*).
2. LangChain maintains session history so the AI remembers previous messages in the conversation.
3. Gemini 1.5 Flash processes the message and appends `[BUY_GOLD]` internally if it detects purchase intent.
4. The backend strips the marker before returning the response, and sets `wants_to_buy: true` in the JSON so the frontend knows to trigger a purchase flow.
5. When `/buy-gold` is called, the price engine fetches live USD spot price, converts using a real-time FX rate API (USD→INR), and applies Indian import duty + GST (~15%) to match domestic pricing.
6. Transaction is saved to the database.

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| `GET` | `/` | Health check — confirms server is running |
| `POST` | `/chat` | Chat with the AI gold advisor (supports multi-turn) |
| `POST` | `/buy-gold` | Execute a gold purchase (name + amount in INR) |
| `GET` | `/gold-price` | Returns current 24K gold price per gram in INR |
| `GET` | `/purchases` | Lists all recorded transactions |

## Why These Technical Choices

- **FastAPI over Flask/Django** — I needed async support for external API calls (Gemini + gold price + FX rate). FastAPI handles this natively. The auto-generated `/docs` page was a bonus for quick testing.
- **SQLite over Postgres** — Intentional for this assignment. Reviewers can clone and run the app in 30 seconds flat without provisioning a database server. In production, I'd swap this for a managed Postgres instance.
- **Gemini 1.5 Flash over heavier models** — Latency matters for chat interfaces. Flash gives good enough reasoning for intent detection at much lower response times compared to Pro or GPT-4 class models.
- **Defensive error handling** — The Gemini API can hit rate limits under load. I wrapped the LLM call in a try/except that returns a graceful fallback response instead of crashing the server. This keeps the API functional even when the AI layer is temporarily down.

## Known Limitations & What I'd Improve

- **Cold starts on free tier:** Render spins down the server after ~15 min of inactivity. First request after that can take 30-50 seconds. Would fix this with a paid plan or a keep-alive cron job.
- **In-memory chat history:** Currently using LangChain's `InMemoryChatMessageHistory`, which means chat context is lost on server restart. A production version needs Redis or a database-backed session store.
- **No auth:** All endpoints are open for ease of testing. A real deployment would need JWT tokens and user-to-session mapping.
- **Gold price delta:** The price engine uses a free-tier gold API + exchange rate API. Prices may lag slightly behind official MCX/IBJA rates, but the architecture supports swapping in a premium data source.

---

## Project Structure

```
simplify-money-ai-intern/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app, routes, middleware
│   ├── config.py              # env vars and constants
│   ├── database.py            # SQLAlchemy engine and session
│   ├── models.py              # GoldPurchase table definition
│   ├── schemas.py             # Pydantic request/response models
│   ├── prompts/
│   │   └── system_prompt.txt  # AI persona and behavior rules
│   └── services/
│       ├── chat_service.py    # LangChain + Gemini conversation logic
│       └── gold_service.py    # Live pricing, FX conversion, transactions
├── requirements.txt
├── .env.example
└── .gitignore
```

## Run It Locally

```bash
# 1. Clone
git clone https://github.com/SHAILESH-RS-UPADHYAY/simplify-money-backend.git
cd simplify-money-backend

# 2. Install
pip install -r requirements.txt

# 3. Set up env
cp .env.example .env
# open .env and paste your Gemini API key

# 4. Start
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) and start testing.
