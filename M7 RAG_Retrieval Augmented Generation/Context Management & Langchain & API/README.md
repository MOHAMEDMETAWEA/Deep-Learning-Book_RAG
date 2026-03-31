# LangChain Chat with Memory & FastAPI 💬

A complete **conversational AI system** built with LangChain that maintains conversation memory, provides context management, and exposes multiple interfaces (CLI, REST API, Web UI) for seamless integration.

## 🎯 Project Overview

This project demonstrates how to build production-ready conversational applications using LangChain, featuring:

- **Conversation Memory** — Maintains full chat history across sessions
- **Context Management** — Retrieves and prioritizes relevant conversation history
- **LLM Integration** — Seamlessly calls HuggingFace/OpenAI models via LangChain
- **FastAPI Server** — REST API for remote chat interaction
- **Gradio Web UI** — Interactive web interface for chat
- **Session Management** — Supports multiple independent conversation sessions
- **Multi-Module Architecture** — Clean separation: prompts, memory, API, UI

### Key Features

✅ **LangChain Framework** — Prompts, chains, and memory abstraction  
✅ **Conversation Persistence** — In-memory and raw history tracking  
✅ **Multi-Session Support** — Isolated conversations per user/session  
✅ **FastAPI Backend** — Production-ready REST API  
✅ **Gradio Interface** — User-friendly web UI  
✅ **HuggingFace Models** — Access to Qwen, Llama, and other HF models  
✅ **Arabic Language Support** — Full RTL text support  
✅ **Educational Documentation** — Comprehensive guides on memory & context management  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
├──────────────┬──────────────────────────┬──────────────────┤
│ CLI/Python   │ Gradio Web UI            │ REST API Clients │
│ (prompt)     │ (browser)                │ (curl/SDK)       │
└──────────────┴──────────────────────────┴──────────────────┘
               │                          │
               └──────────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  FastAPI Server      │
                   │  (api.py)            │
                   │  /chat /history /    │
                   │  /clear /health      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Chat Logic          │
                   │  (app.py)            │
                   │  • Session Manager   │
                   │  • Memory Storage    │
                   └──────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────┐
        │                     │                 │
        ▼                     ▼                 ▼
   ┌────────────┐      ┌─────────────┐  ┌──────────────┐
   │ Prompts    │      │ LangChain   │  │ In-Memory    │
   │ (prompts   │      │ Chain       │  │ Session      │
   │  .py)      │      │ (LLM calls) │  │ Store        │
   └────────────┘      └─────────────┘  └──────────────┘
                             │
                             ▼
                   ┌──────────────────────┐
                   │ HuggingFace API      │
                   │ (or OpenAI)          │
                   │ Qwen/Llama/GPT       │
                   └──────────────────────┘
```

---

## 📂 Project Structure

```
Context Management & Langchain & API/
└── Langchain_Chat with Memory/
    └── Langchain_ Chat/
        ├── README.md                          ← This file
        ├── requirements.txt                   ← Python dependencies
        ├── .env.example                       ← Environment template
        │
        ├── app.py                             ← Core chat logic
        │   ├── LLM initialization
        │   ├── Session management
        │   ├── Memory storage & retrieval
        │   └── Chat function
        │
        ├── api.py                             ← FastAPI server
        │   ├── /health endpoint
        │   ├── /chat endpoint (POST)
        │   ├── /history endpoint (GET)
        │   └── /clear endpoint (POST)
        │
        ├── ui_gradio_api.py                   ← Web interface
        │   ├── Gradio chatbot UI
        │   ├── Session management UI
        │   └── History viewer
        │
        ├── prompts.py                         ← LangChain prompts
        │   └── ChatPromptTemplate definition
        │
        ├── combined_0_1_2.pdf                 ← Reference documentation
        │
        └── Documentation/
            ├── 0) Chatbot_Memory.md           ← Memory concepts
            ├── 1) LangChain_in_This_Project.md ← LangChain overview
            ├── 2) Context_Management.md       ← Context strategies
            ├── 3) Student_Task_1_Window_Memory.md ← Task 1
            └── 4) Student_Task_2_Summary_Buffer.md ← Task 2
```

---

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites

```bash
# Requires: Python 3.9+
python --version

# Get API keys:
# - HuggingFace: https://huggingface.co/settings/tokens
# - OpenAI (optional): https://platform.openai.com/api-keys
```

### 2. Install

```bash
# Navigate to project
cd "Context Management & Langchain & API/Langchain_Chat with Memory/Langchain_ Chat"

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your credentials
# HF_TOKEN=hf_...
# HF_MODEL=Qwen/Qwen3-Coder-Next:novita  (optional)
```

### 4. Run

Choose one interface:

#### Option A: Start FastAPI Server

```bash
uvicorn api:api --reload --host 127.0.0.1 --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Option B: Start Gradio Web UI

```bash
python ui_gradio_api.py
```

**Output:**
```
Running on local URL:  http://127.0.0.1:7860
```

#### Option C: Python Interactive

```python
from app import chat, get_raw_history, clear_session

# Chat
answer = chat("مرحبا", session_id="user1")
print(answer)

# View history
history = get_raw_history("user1")
print(history)

# Clear session if needed
clear_session("user1")
```

---

## 📖 Usage Guides

### Option 1: Web UI (Easiest)

1. Run Gradio: `python ui_gradio_api.py`
2. Open browser: `http://127.0.0.1:7860`
3. Enter session ID (e.g., "user1")
4. Type questions and chat
5. Click "Show History" to see conversation log
6. Click "Clear History" to reset session

**Features:**
- ✅ Conversational interface
- ✅ Real-time response
- ✅ Session persistence across reloads
- ✅ History viewer
- ✅ Clear session button

### Option 2: REST API (Programmatic)

Start server:
```bash
uvicorn api:api --reload --host 127.0.0.1 --port 8000
```

#### Health Check

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok"}
```

#### Send Message

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user1", "question": "السلام عليكم"}'

# Response:
# {
#   "session_id": "user1",
#   "answer": "وعليكم السلام ورحمة الله وبركاته..."
# }
```

#### Get Conversation History

```bash
curl http://127.0.0.1:8000/history/user1

# Response:
# {
#   "session_id": "user1",
#   "history": [
#     {"role": "human", "content": "مرحبا"},
#     {"role": "ai", "content": "مرحبا..."}
#   ]
# }
```

#### Clear Session

```bash
curl -X POST http://127.0.0.1:8000/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user1"}'

# Response:
# {"status": "cleared", "session_id": "user1"}
```

### Option 3: Python SDK (Integration)

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
SESSION_ID = "user1"

# Send message
response = requests.post(
    f"{BASE_URL}/chat",
    json={"session_id": SESSION_ID, "question": "What is AI?"},
    timeout=60
)
answer = response.json()["answer"]
print(f"Assistant: {answer}")

# Get history
history_response = requests.get(f"{BASE_URL}/history/{SESSION_ID}")
history = history_response.json()["history"]
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# Clear
requests.post(f"{BASE_URL}/clear", json={"session_id": SESSION_ID})
```

### Option 4: Direct Python (In-Process)

```python
from app import chat, get_raw_history, clear_session

# Chat with a session
response = chat("Hello!", session_id="student1")
print(response)

# Get full history
history = get_raw_history("student1")
for msg in history:
    print(f"[{msg['role']}] {msg['content']}")

# Clear session
clear_session("student1")
```

---

## ⚙️ Configuration Details

### Environment Variables (`.env`)

```env
# Required: HuggingFace Token
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Optional: Model name (defaults to Qwen)
HF_MODEL=Qwen/Qwen3-Coder-Next:novita

# Available HF Models:
# - Qwen/Qwen3-Coder-Next:novita
# - meta-llama/Llama-2-7b-chat
# - mistralai/Mistral-7B-Instruct-v0.2
# - google/flan-t5-large
```

### LLM Configuration (`app.py`)

```python
llm = ChatOpenAI(
    model=HF_MODEL,                              # Model name
    api_key=HF_TOKEN,                            # HF API key
    base_url="https://router.huggingface.co/v1", # HF endpoint
    temperature=0.2,                             # Lower = more deterministic
)
```

**Temperature explained:**
- `0.0` — Deterministic, always same answer
- `0.5` — Balanced creativity + consistency
- `1.0` — Maximum creativity, random responses
- `>1.0` — Very unpredictable

### Memory Configuration

The system tracks **two types of memory**:

#### 1. **LangChain History** (for LLM)
```python
InMemoryChatMessageHistory()  # What the LLM sees
```
- Structured message objects
- Automatically passed to prompt
- Format: `HumanMessage`, `AIMessage`

#### 2. **Raw History** (for debugging/audit)
```python
sess["raw_history"] = [
    {"role": "human", "content": "..."},
    {"role": "ai", "content": "..."}
]
```
- Persistent JSON-serializable format
- Returned by `/history` API
- Easy to log or persist to database

---

## 🔌 API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send message and get response |
| `GET` | `/history/{session_id}` | Retrieve conversation history |
| `POST` | `/clear` | Clear session history |

### Request/Response Models

#### `POST /chat`

**Request:**
```json
{
  "session_id": "user1",
  "question": "What is LangChain?"
}
```

**Response:**
```json
{
  "session_id": "user1",
  "answer": "LangChain is a framework for building LLM-powered applications..."
}
```

#### `GET /history/{session_id}`

**Request:**
```
GET /history/user1
```

**Response:**
```json
{
  "session_id": "user1",
  "history": [
    {"role": "human", "content": "Hi"},
    {"role": "ai", "content": "Hello! How can I help?"}
  ]
}
```

#### `POST /clear`

**Request:**
```json
{
  "session_id": "user1"
}
```

**Response:**
```json
{
  "status": "cleared",
  "session_id": "user1"
}
```

---

## 🧠 Understanding Memory

### Problem Without Memory

```
User:  "My name is Alice"
Bot:   "Nice to meet you, Alice!"

User:  "What's my name?"
Bot:   ❌ "I don't know"  (forgot!)
```

### Memory Solution

```
User:  "My name is Alice"
Bot:   "Nice to meet you, Alice!"
[Memory: {role: "human", content: "My name is Alice"}]
[Memory: {role: "ai", content: "Nice to meet you, Alice!"}]

User:  "What's my name?"
Bot Program:
  ✓ Retrieve memory
  ✓ Build prompt: "System prompt + [Memory] + New question"
  ✓ Send to LLM
  
Bot:   "Your name is Alice"  ✅ (remembered!)
```

### Two Types of Memory in This Code

#### Type 1: **LangChain History** (Structured)

What the LLM sees:
```python
from langchain_core.chat_history import InMemoryChatMessageHistory

history = InMemoryChatMessageHistory()
history.add_user_message("Hello")
history.add_ai_message("Hi there")

# LLM sees it as:
# [HumanMessage(content="Hello"), AIMessage(content="Hi there")]
```

#### Type 2: **Raw History** (Serializable)

For debugging/logging:
```python
raw_history = [
    {"role": "human", "content": "Hello"},
    {"role": "ai", "content": "Hi there"}
]
# Can be saved to JSON, database, file
```

### Session Management

```python
# Multiple independent sessions
chat("Hello", session_id="alice")    # Alice's conversation
chat("Hi", session_id="bob")         # Bob's conversation (separate)

# Each has its own memory
history_alice = get_raw_history("alice")  # Only Alice's messages
history_bob = get_raw_history("bob")      # Only Bob's messages

# Clear on demand
clear_session("alice")  # Only clears Alice's history
```

---

## 🎓 Educational Materials

This project includes comprehensive documentation for learning:

### 📄 Included Guides

1. **0) Chatbot_Memory.md**
   - What memory is
   - Why we need it
   - How it works in this code
   - Production-level alternatives

2. **1) LangChain_in_This_Project.md**
   - Introduction to LangChain
   - When to use LangChain
   - Components: prompts, chains, memory

3. **2) Context_Management.md**
   - How to manage conversation context
   - Strategies: window, summary, hybrid
   - Trade-offs explained

4. **3) Student_Task_1_Window_Memory.md**
   - **Task:** Implement window-based memory
   - Only keep last N messages
   - Use case: token limit constraints

5. **4) Student_Task_2_Summary_Buffer.md**
   - **Task:** Implement summary buffer
   - Summarize old messages, keep recent
   - Use case: long conversations

### 🎯 Tasks

**Task 1: Window Memory Strategy**
- Keep only the last 10 messages
- When conversation grows, drop oldest messages
- Implement in a new file: `memory_window.py`

**Task 2: Summary Buffer Strategy**
- Summarize messages older than 5 exchanges
- Keep all recent messages intact
- Implement in file: `memory_summary.py`

---

## 🐛 Troubleshooting

### Issue: "HF_TOKEN environment variable not set"

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your token
# HF_TOKEN=hf_...

# Verify it's loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('HF_TOKEN'))"
```

### Issue: "Connection refused" when calling API

**Solution:**
Make sure FastAPI server is running:
```bash
# In terminal 1:
uvicorn api:api --reload --host 127.0.0.1 --port 8000

# In terminal 2:
curl http://127.0.0.1:8000/health  # Should return {"status": "ok"}
```

### Issue: "Module not found: langchain"

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import langchain; print(langchain.__version__)"
```

### Issue: "Gradio server won't launch"

**Solution:**
```bash
# Check if port 7860 is in use
# Kill process or use different port
python ui_gradio_api.py  # Uses 7860 by default

# Or manually specify port (edit ui_gradio_api.py last line):
# demo.launch(server_name="127.0.0.1", server_port=7861)
```

### Issue: "API returns empty response"

**Solution:**
Check API logs for errors:
```bash
# Start with verbose output
uvicorn api:api --reload --host 127.0.0.1 --port 8000 --log-level debug

# Also verify HF_TOKEN is valid:
curl -H "Authorization: Bearer YOUR_TOKEN" https://api-inference.huggingface.co/models
```

### Issue: "Slow responses (>30 seconds)"

**Solution:**
- Check internet connection to HuggingFace
- Try a smaller model: `HF_MODEL=google/flan-t5-base`
- Lower `temperature` in app.py
- Check HF quota: https://huggingface.co/settings/tokens

---

## 📊 System Architecture Details

### Data Flow: User Message → Response

```
1. User types message
   ↓
2. Gradio/API receives: {"session_id": "user1", "question": "Hello"}
   ↓
3. api.chat_endpoint() → app.chat()
   ↓
4. _ensure_session("user1") creates if doesn't exist:
   {
     "lc_history": InMemoryChatMessageHistory(),
     "raw_history": []
   }
   ↓
5. app.raw_history.append({"role": "human", "content": "Hello"})
   ↓
6. chat_with_memory.invoke() calls LLM:
   - Retrieves lc_history (all previous messages)
   - Builds prompt:
     "System: أنت مساعد عربي... [History] [New question]"
   - Sends to HF API
   ↓
7. LLM returns response
   ↓
8. app.raw_history.append({"role": "ai", "content": "Response..."})
   ↓
9. Response returned to Gradio/API
   ↓
10. User sees response
```

### Session Storage

In-memory dictionary:
```python
_STORE = {
    "user1": {
        "lc_history": InMemoryChatMessageHistory([...]),
        "raw_history": [
            {"role": "human", "content": "..."},
            {"role": "ai", "content": "..."}
        ]
    },
    "user2": {
        "lc_history": InMemoryChatMessageHistory([...]),
        "raw_history": [...]
    }
}
```

⚠️ **Note:** In-memory storage is lost on server restart. For persistence, see "Production Deployment" below.

---

## 🚀 Production Deployment

### Persistence Layer (Add to app.py)

```python
import json
from datetime import datetime

def save_session(session_id: str):
    """Save session to disk"""
    raw_history = get_raw_history(session_id)
    filename = f"sessions/{session_id}.json"
    with open(filename, "w") as f:
        json.dump(raw_history, f)

def load_session(session_id: str):
    """Load session from disk"""
    filename = f"sessions/{session_id}.json"
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
```

### Deployment Options

#### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run FastAPI
CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (API + UI)

```yaml
version: '3'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HF_TOKEN=${HF_TOKEN}
    command: uvicorn api:api --host 0.0.0.0 --port 8000

  web:
    build: .
    ports:
      - "7860:7860"
    environment:
      - HF_TOKEN=${HF_TOKEN}
    command: python ui_gradio_api.py
```

#### Cloud Platforms

- **Hugging Face Spaces** — Deploy Gradio app (free)
- **Railway** — Deploy FastAPI (free tier)
- **Render** — Full stack deployment
- **AWS Lambda** — Serverless API

---

## 🔐 Security Notes

1. **Never commit `.env`** — It contains API keys
   ```bash
   # .gitignore already includes:
   .env
   .env.local
   ```

2. **Use environment variables** — Never hardcode secrets:
   ```python
   # ❌ Bad:
   api_key = "hf_xxx..."
   
   # ✅ Good:
   import os
   api_key = os.getenv("HF_TOKEN")
   ```

3. **Rotate API keys** — Especially if exposed:
   - HF: https://huggingface.co/settings/tokens
   - OpenAI: https://platform.openai.com/api-keys

4. **Rate Limiting** — Add to production API:
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

---

## 📚 Learning Path

### Beginner

1. Run Gradio UI and chat
2. Read `0) Chatbot_Memory.md`
3. Try Task 1: Window Memory

### Intermediate

1. Read `1) LangChain_in_This_Project.md`
2. Modify prompts in `prompts.py`
3. Try Task 2: Summary Buffer
4. Test API endpoints with cURL

### Advanced

1. Read `2) Context_Management.md`
2. Implement persistent storage (JSON/DB)
3. Implement semantic caching
4. Deploy to Hugging Face Spaces or cloud
5. Add authentication & rate limiting

---

## 📞 Support

**Need Help?**

1. Check `README.md` in this directory (you're reading it!)
2. Review markdown guides in the folder
3. Check FastAPI docs: http://localhost:8000/docs (when running)
4. Check Gradio code in `ui_gradio_api.py`

**Common Questions:**

Q: Can I use OpenAI instead of HuggingFace?
A: Yes! Change `base_url` in `app.py` and use OpenAI endpoint + API key

Q: How do I add database persistence?
A: Replace in-memory `_STORE` with SQLite/PostgreSQL

Q: Can I run Gradio and FastAPI together?
A: No, but you can use separate processes or one calls the other

Q: How do I deploy to production?
A: See "Production Deployment" section above

---

## 📅 Changelog

### v1.0 (Current)
- ✅ LangChain chat with memory
- ✅ FastAPI server with `/chat` `/history` `/clear` endpoints
- ✅ Gradio web UI with session management
- ✅ Arabic language support
- ✅ Two types of memory (LangChain + raw history)
- ✅ Educational documentation
- ✅ Task exercises (window & summary memory)
- ✅ Comprehensive README

---

## 🎓 Key Concepts

### LangChain Components Used

| Component | Purpose | File |
|-----------|---------|------|
| `ChatPromptTemplate` | Define prompt structure | `prompts.py` |
| `ChatOpenAI` | LLM wrapper | `app.py` |
| `RunnableWithMessageHistory` | Auto-manage conversation | `app.py` |
| `InMemoryChatMessageHistory` | Store messages | `app.py` |

### Data Structures

**Session:**
```python
{
    "lc_history": InMemoryChatMessageHistory,  # For LLM
    "raw_history": [...]                       # For API
}
```

**Message (raw):**
```python
{"role": "human|ai", "content": "text"}
```

### API Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid input (missing question) |
| 500 | Server error (missing HF_TOKEN) |

---

## 🚀 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Setup `.env` with HF_TOKEN
3. ✅ Run Gradio: `python ui_gradio_api.py`
4. ✅ Chat in browser: http://127.0.0.1:7860
5. ✅ Read memory documentation
6. ✅ Try Task 1 & Task 2

---

**Happy chatting! 💬✨**
