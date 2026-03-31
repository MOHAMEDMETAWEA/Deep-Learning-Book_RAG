# Langchain Chat with Memory — Project Hub 📚

This directory contains the complete LangChain chatbot project with memory management, session handling, and multiple interfaces.

## 📂 Directory Structure

```
Langchain_Chat with Memory/
└── Langchain_ Chat/
    ├── README.md                          ← START HERE!
    ├── requirements.txt
    ├── .env.example
    ├── app.py                             (Core logic)
    ├── api.py                             (FastAPI)
    ├── ui_gradio_api.py                   (Web UI)
    ├── prompts.py                         (Prompts)
    └── Documentation/
        ├── 0) Chatbot_Memory.md
        ├── 1) LangChain_in_This_Project.md
        ├── 2) Context_Management.md
        ├── 3) Student_Task_1_Window_Memory.md
        └── 4) Student_Task_2_Summary_Buffer.md
```

## 🚀 Getting Started

1. Navigate to the actual project: `cd "Langchain_ Chat"`
2. Read the full README: `README.md`
3. Follow the Quick Start section

## 📖 What This Project Is

A complete implementation of a conversational chatbot using LangChain that:

- ✅ Maintains conversation memory across messages
- ✅ Supports multiple independent sessions
- ✅ Exposes three interfaces:
  - Web UI (Gradio)
  - REST API (FastAPI)
  - Python API (direct calls)
- ✅ Integrates with HuggingFace LLMs
- ✅ Includes comprehensive educational materials

## 🎯 Key Concepts

### Memory
Store conversation history so the LLM can understand context.

### LangChain
Framework for building LLM applications with prompts, chains, and memory abstractions.

### Session Management
Each user gets their own isolated conversation space.

### Fast API
REST API server to expose chat functionality over HTTP.

### Gradio UI
User-friendly web interface for chatting.

## 📊 At a Glance

| Feature | Status |
|---------|--------|
| Conversation Memory | ✅ |
| Multi-Session | ✅ |
| FastAPI Server | ✅ |
| Gradio Web UI | ✅ |
| Arabic Support | ✅ |
| Educational Guides | ✅ |
| Tasks/Exercises | ✅ |

## 🔗 Next Steps

👉 **Enter the project:** `cd Langchain_\ Chat`

👉 **Read full README:** `cat README.md`

👉 **Start coding!** Follow Quick Start section

---

For complete documentation, see `Langchain_ Chat/README.md`
