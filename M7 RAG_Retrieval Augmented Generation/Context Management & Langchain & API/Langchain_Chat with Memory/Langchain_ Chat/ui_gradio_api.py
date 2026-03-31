# run:  python ui_gradio_api.py

import requests
import gradio as gr

API_BASE = "http://127.0.0.1:8000"

def api_chat(message, history, session_id):
    message = (message or "").strip()
    if not message:
        return "", history

    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json={"session_id": session_id, "question": message},
            timeout=60
        )
        r.raise_for_status()
        answer = r.json()["answer"]
    except Exception as e:
        answer = f"API error: {e}"

    history = history or []
    history.append((message, answer))
    return "", history

def api_clear(session_id):
    try:
        r = requests.post(f"{API_BASE}/clear", json={"session_id": session_id}, timeout=30)
        r.raise_for_status()
        # بعد clear نخلي واجهة الشات فاضية
        return []
    except Exception as e:
        # لو فشل، ما نمسح الواجهة
        return gr.update(), f"API error: {e}"


def clear_and_update(sid):
    try:
        r = requests.post(f"{API_BASE}/clear", json={"session_id": sid}, timeout=30)
        r.raise_for_status()
        return [], f"Cleared session: {sid}"
    except Exception as e:
        return gr.update(), f"API error: {e}"

def fetch_history(sid):
    """Fetch and display history with error handling"""
    if not sid or len(sid) > 50:
        return "(❌ Invalid session ID)"
    
    try:
        r = requests.get(f"{API_BASE}/history/{sid}", timeout=30)
        r.raise_for_status()
        items = r.json().get("history", [])
        
        if not items:
            return "(📭 No history yet)"
            
        lines = []
        for i, it in enumerate(items, 1):
            emoji = "👤" if it.get("role") == "human" else "🤖"
            content = it.get("content", "")[:100]
            lines.append(f"{i:02d}. {emoji} {content}")
        return "\n".join(lines)
        
    except requests.exceptions.Timeout:
        return "(❌ Request timeout - API server not responding)"
    except requests.exceptions.ConnectionError:
        return f"(❌ Cannot connect: {API_BASE})"
    except Exception as e:
        return f"(❌ Error: {str(e)[:100]})"


with gr.Blocks(title="Chat via FastAPI") as demo:
    gr.Markdown("## Gradio UI (calls FastAPI backend)")

    session_id = gr.Textbox(label="Session ID", value="student1")
    chatbot = gr.Chatbot(label="Chat")
    msg = gr.Textbox(label="Message")
    status = gr.Markdown("")
    history_box = gr.Textbox(label="Session History (raw)", lines=10)

    with gr.Row():
        clear_btn = gr.Button("Clear History")
        show_btn = gr.Button("Show History")

    msg.submit(api_chat, inputs=[msg, chatbot, session_id], outputs=[msg, chatbot])

    clear_btn.click(clear_and_update, inputs=[session_id], outputs=[chatbot, status])
    show_btn.click(fetch_history, inputs=[session_id], outputs=[history_box])

demo.launch()