import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from prompts import chat_prompt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3-Coder-Next:novita")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TIMEOUT = int(os.getenv("TIMEOUT", "60"))

if not HF_TOKEN:
    logger.error("HF_TOKEN not set")
    raise ValueError(
        "HF_TOKEN not found! Get it from: https://huggingface.co/settings/tokens\n"
        "Add to .env: HF_TOKEN=hf_..."
    )

try:
    llm = ChatOpenAI(
        model=HF_MODEL,
        api_key=HF_TOKEN,
        base_url="https://router.huggingface.co/v1",
        temperature=TEMPERATURE,
        request_timeout=TIMEOUT,
    )
    logger.info(f"✅ LLM ready: {HF_MODEL}")
except Exception as e:
    logger.error(f"❌ LLM init failed: {e}")
    raise

chat_chain = chat_prompt | llm  # Prompt → LLM

# Session storage: session_id -> {lc_history, raw_history}
_STORE: Dict[str, Dict[str, Any]] = {}

def _ensure_session(session_id: str):
    if session_id not in _STORE:
        _STORE[session_id] = {
            "lc_history": InMemoryChatMessageHistory(),
            "raw_history": []  # list of {"role": "human"/"ai", "content": "..."}
        }
    return _STORE[session_id]

def get_history(session_id: str):
    return _ensure_session(session_id)["lc_history"]

chat_with_memory = RunnableWithMessageHistory(
    chat_chain,
    get_history,
    input_messages_key="question",
    history_messages_key="history",
)

def chat(question: str, session_id: str = "default") -> str:
    """Chat with memory. Handles errors gracefully."""
    question = (question or "").strip()
    if not question:
        return "❌ اكتب رسالة أولاً"

    if not isinstance(session_id, str) or not session_id:
        session_id = "default"

    try:
        sess = _ensure_session(session_id)
        sess["raw_history"].append({"role": "human", "content": question})
        logger.debug(f"[{session_id}] Q: {question[:50]}...")

        # استدعاء LLM مع memory
        msg = chat_with_memory.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}}
        )
        answer = msg.content
        sess["raw_history"].append({"role": "ai", "content": answer})
        logger.debug(f"[{session_id}] A: {answer[:50]}...")
        return answer
        
    except Exception as e:
        logger.error(f"[{session_id}] Error: {str(e)}")
        # Remove user msg if LLM failed
        if sess["raw_history"] and sess["raw_history"][-1]["role"] == "human":
            sess["raw_history"].pop()
        return f"❌ خطأ: {str(e)[:100]}"

def get_raw_history(session_id: str = "default") -> List[dict]:
    """Get conversation history."""
    history = _ensure_session(session_id)["raw_history"]
    logger.debug(f"[{session_id}] Retrieved {len(history)} messages")
    return list(history)

def clear_session(session_id: str = "default") -> bool:
    """Clear session history. Returns True if cleared."""
    if session_id not in _STORE:
        logger.info(f"Session {session_id} doesn't exist")
        return False
    _STORE[session_id] = {
        "lc_history": InMemoryChatMessageHistory(),
        "raw_history": []
    }
    logger.info(f"✅ Cleared: {session_id}")
    return True

if __name__ == "__main__":
    try:
        session_id = input("Session ID (مثلاً student1): ").strip() or "default"
        logger.info(f"Session started: {session_id}")
        print(f"✅ Session: {session_id} | Commands: /history, /clear, exit")

        while True:
            try:
                q = input("\n📝 سؤال: ").strip()
                if not q:
                    continue
                    
                if q.lower() == "exit":
                    print("👋 تم الإغلاق")
                    break

                if q.lower() == "/history":
                    history = get_raw_history(session_id)
                    print("\n📋 HISTORY:")
                    if history:
                        for i, item in enumerate(history, 1):
                            emoji = "👤" if item["role"] == "human" else "🤖"
                            print(f"{i:02d}. {emoji} {item['content'][:80]}")
                    else:
                        print("(No history)")
                    continue

                if q.lower() == "/clear":
                    if clear_session(session_id):
                        print("✅ مسح الجلسة")
                    continue

                try:
                    answer = chat(q, session_id=session_id)
                    print(f"\n🤖 {answer}")
                except Exception as e:
                    logger.error(f"Chat error: {e}")
                    print(f"❌ {str(e)}")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n👋 تم الإغلاق")
                break
                
    except Exception as e:
        logger.error(f"Fatal: {e}")
        print(f"❌ Fatal: {e}")