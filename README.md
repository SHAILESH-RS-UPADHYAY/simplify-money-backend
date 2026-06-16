<div align="center">

# 💰 Simplify Money - Gold Investment AI Backend

**An AI-powered conversational backend for digital gold investment.**<br/>
*Users can chat with an AI financial advisor that understands purchase intent, fetches live gold prices, and logs transactions.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)

> 🌐 **Live Demo:** [simplify-money-backend.onrender.com/docs](https://simplify-money-backend.onrender.com/docs)<br/>
> *Open the link above to interact with the API directly via Swagger UI. No setup required.*

</div>

---

## ⚙️ How It Works

**Request lifecycle:**
> `User Query` ➔ `FastAPI Router` ➔ `LangChain (Session Memory)` ➔ `Gemini 1.5 Flash` ➔ `Intent Parser` ➔ `Execution`

1. User sends a message to `/chat` (e.g., *"I want to invest 5000 in gold"*).
2. LangChain maintains session history so the AI remembers context.
3. Gemini 1.5 Flash processes the message and internally appends `[BUY_GOLD]` if it detects purchase intent.
4. The backend strips the marker before returning the response and flags `wants_to_buy: true` in the JSON, signaling the frontend to trigger a purchase flow.
5. When `/buy-gold` is called, the price engine fetches the live USD spot price, converts it using a real-time FX rate API (USD ➔ INR), and applies Indian import duty + GST (~15%) to match domestic pricing.
6. The transaction is securely saved to the database.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check - confirms the server is running. |
| `POST` | `/chat` | Chat with the AI gold advisor (supports multi-turn). |
| `POST` | `/buy-gold` | Execute a gold purchase (requires name + amount in INR). |
| `GET` | `/gold-price` | Returns the current 24K gold price per gram in INR. |
| `GET` | `/purchases` | Lists all recorded transactions. |

---

## 🧠 Why These Technical Choices?

*   **FastAPI over Flask/Django:** Essential for async support required by external API calls (Gemini, Gold Price, FX Rate). The auto-generated `/docs` page accelerates testing.
*   **SQLite over Postgres:** Chosen intentionally to allow reviewers to clone and run the app in under 30 seconds without provisioning a database server. For production, a managed Postgres instance is recommended.
*   **Gemini 1.5 Flash over Heavier Models:** Latency is critical for chat interfaces. Flash delivers excellent reasoning for intent detection at significantly lower response times compared to Pro or GPT-4.
*   **Defensive Error Handling:** The Gemini API can hit rate limits under load. The LLM call is wrapped in a robust `try/except` block that returns a graceful fallback response, keeping the API functional even if the AI layer experiences downtime.

---

## 🚧 Known Limitations & Future Improvements

*   **Cold Starts on Free Tier:** Render spins down the server after ~15 minutes of inactivity. The first request after a spin-down may take 30-50 seconds. This is easily resolved with a paid plan or keep-alive cron jobs.
*   **In-Memory Chat History:** Currently utilizing LangChain's `InMemoryChatMessageHistory`, meaning context is lost upon server restart. A production build requires a Redis or database-backed session store.
*   **No Auth:** All endpoints are open to facilitate testing. A real deployment must incorporate JWT tokens and user-to-session mapping.
*   **Gold Price Delta:** The price engine utilizes a free-tier gold API alongside an exchange rate API. Prices may lag slightly behind official MCX/IBJA rates, but the architecture seamlessly supports swapping in premium data sources.

---

## 📁 Project Structure

```text
simplify-money-ai-intern/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app, routes, middleware
│   ├── config.py             # Environment variables and constants
│   ├── database.py           # SQLAlchemy engine and session
│   ├── models.py             # GoldPurchase table definition
│   ├── schemas.py            # Pydantic request/response models
│   ├── prompts/
│   │   └── system_prompt.txt # AI persona and behavior rules
│   └── services/
│       ├── chat_service.py   # LangChain + Gemini conversation logic
│       └── gold_service.py   # Live pricing, FX conversion, transactions
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 💻 Run It Locally

**1. Clone the repository**
```bash
git clone https://github.com/SHAILESH-RS-UPADHYAY/simplify-money-backend.git
cd simplify-money-backend
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
# Open .env and paste your Gemini API key
```

**4. Start the server**
```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to start interacting with the API!
