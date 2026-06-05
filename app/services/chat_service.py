import os
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.config import GEMINI_API_KEY
from app.services.gold_service import fetch_gold_price

# load system prompt from file
prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompt.txt")
with open(prompt_path, "r") as f:
    SYSTEM_PROMPT = f.read()

# setup gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# prompt template with history support
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm

# in-memory store for chat sessions
# each session_id gets its own conversation history
chat_store = {}


def get_session_history(session_id: str):
    if session_id not in chat_store:
        chat_store[session_id] = InMemoryChatMessageHistory()
    return chat_store[session_id]


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


def chat(message: str, session_id: str = None):

    if not session_id:
        session_id = str(uuid.uuid4())

    config = {"configurable": {"session_id": session_id}}
    
    try:
        # Fetch actual live price and inject it as hidden context
        current_price = fetch_gold_price()
        context_injected_message = f"[SYSTEM INSTRUCTION: The actual live price of 24K gold right now is Rs {current_price} per gram. Use this exact price if the user asks.]\n\n{message}"
        
        result = chain_with_history.invoke({"question": context_injected_message}, config=config)
        reply_text = result.content
        
        # New Gemini SDK might return a list of content blocks instead of a string
        if isinstance(reply_text, list):
            reply_text = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in reply_text])
        elif not isinstance(reply_text, str):
            reply_text = str(reply_text)
            
    except Exception as e:
        # Graceful fallback if Gemini API hits free tier limits
        print(f"Gemini API Error: {e}")
        reply_text = "I am currently experiencing high network traffic. However, if you would like to purchase gold, please specify the amount and I can process it for you immediately! [BUY_GOLD]"


    # check if the LLM triggered a purchase intent
    wants_to_buy = False
    if "[BUY_GOLD]" in reply_text:
        wants_to_buy = True
        reply_text = reply_text.replace("[BUY_GOLD]", "").strip()

    return {
        "reply": reply_text,
        "wants_to_buy": wants_to_buy,
        "session_id": session_id,
    }
