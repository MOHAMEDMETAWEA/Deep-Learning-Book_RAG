import streamlit as st
import requests
import json
import os
from config import API_URL

# --- CONFIG ---
# Default fallback if not set in config; however, config.API_URL should be the primary source.
HISTORY_FILE = "chat_history.json"

st.set_page_config(
    page_title="Deep Learning RAG",
    page_icon="🧠",
    layout="wide"
)

# --- PERSISTENCE HELPERS ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(messages):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

# --- STYLING ---
st.markdown("""
<style>
    .source-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .score-tag {
        font-weight: bold;
        color: #2e7d32;
    }
    .chapter-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

if "chapters" not in st.session_state:
    st.session_state.chapters = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ RAG Settings")
    api_base = st.text_input("API URL", value=API_URL)
    
    st.divider()
    st.subheader("🔍 Advanced Filtering")
    
    # Fetch chapters
    if not st.session_state.chapters:
        try:
            r = requests.get(f"{api_base}/chapters", timeout=10)
            if r.status_code == 200:
                st.session_state.chapters = r.json().get("chapters", [])
                if not st.session_state.chapters:
                    st.warning("⚠️ No chapters found for this document in the database.")
            else:
                st.error(f"❌ Failed to load chapters: API returned {r.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the Backend API. Please ensure the backend is running (e.g. via run_system.bat) and retry.")
        except Exception as e:
            st.error(f"❌ Could not connect to API for chapters. Error details: {e}")

    selected_chapters = st.multiselect(
        "Filter by Chapters",
        options=st.session_state.chapters,
        help="Only search within selected chapters. Leave empty for full book search."
    )

    st.divider()
    st.caption("📏 Scope by Page Range")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        min_page = st.number_input("Min Page", value=0, min_value=0, step=1)
    with col_p2:
        max_page = st.number_input("Max Page", value=1000, min_value=0, step=1)

    st.divider()
    st.caption("🏷️ Section/Headline Search")
    section_filter = st.text_input(
        "Focus on Section",
        placeholder="e.g. Backpropagation",
        help="Search only within sections/headlines matching this keyword."
    )
    
    if st.button("🔄 Refresh Chapters"):
        st.session_state.chapters = []
        st.rerun()

    st.divider()
    if st.button("🧹 Clear Conversation History"):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

    st.divider()
    st.markdown("""
    ### 📖 About
    This RAG system is built on the **Deep Learning** book by Ian Goodfellow.

    **Features:**
    - Hybrid Search (Vector + Keyword)
    - Query Expansion
    - Multi-stage Reranking
    - **Chapter Filtering** (New!)
    - **Persistent History** (New!)
    """)

# --- MAIN UI ---
st.title("🧠 Deep Learning Book — AI Assistant")
st.markdown("Ask anything about Deep Learning, Neural Networks, or Optimization.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chunks" in message and message["role"] == "assistant":
            with st.expander("📚 View Sources & Retrieval Details"):
                for i, chunk in enumerate(message["chunks"]):
                    pg = f"Pages: {chunk.get('page_start', '?')}-{chunk.get('page_end', '?')}"
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {i+1}:</strong> {chunk.get('section', 'General')}<br/>
                        <span class="chapter-tag">{chunk.get('chapter', 'Unknown Chapter')}</span> | 
                        <span>{pg}</span> |
                        <span class="score-tag">Score: {chunk.get('final_score', 0):.4f}</span>
                        <hr/>
                        {chunk.get('content', '')}
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("What is backpropagation?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Searching and thinking...")

        try:
            payload = {
                "question": prompt,
                "filter_chapters": selected_chapters if selected_chapters else None,
                "min_page": int(min_page) if min_page > 0 else None,
                "max_page": int(max_page) if max_page < 1000 else None,
                "filter_section": section_filter if section_filter else None
            }
            response = requests.post(
                f"{api_base}/ask",
                json=payload,
                timeout=45
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("Generated Answer", "No answer generated.")
                chunks = data.get("Top Retrieved Chunks", [])
                expansion = data.get("Query Expansion", {})

                # Show expansion details
                expanded_q = expansion.get("expanded", "")
                if expanded_q and expanded_q.lower() != prompt.lower():
                    st.info(f"✨ Expanded Query: `{expanded_q}`")

                message_placeholder.markdown(answer)

                # Add to history
                new_msg = {
                    "role": "assistant",
                    "content": answer,
                    "chunks": chunks
                }
                st.session_state.messages.append(new_msg)
                save_history(st.session_state.messages)

                # Show sources
                with st.expander("📚 View Sources & Retrieval Details"):
                    for i, chunk in enumerate(chunks):
                        pg = f"Pages: {chunk.get('page_start', '?')}-{chunk.get('page_end', '?')}"
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>Source {i+1}:</strong> {chunk.get('section', 'General')}<br/>
                            <span class="chapter-tag">{chunk.get('chapter', 'Unknown Chapter')}</span> | 
                            <span>{pg}</span> |
                            <span class="score-tag">Score: {chunk.get('final_score', 0):.4f}</span>
                            <hr/>
                            {chunk.get('content', '')}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                message_placeholder.error(error_msg)

        except requests.exceptions.ConnectionError:
            message_placeholder.error("❌ Failed to connect to the Backend API. Ensure the backend server is running and retry.")
        except Exception as e:
            message_placeholder.error(f"❌ Failed to connect to API: {e}")

# --- FOOTER ---
st.divider()
st.caption("DEPI Generative & Agentic AI Professional - RAG Project v2.2")
