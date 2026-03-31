# FastAPI server for LangChain chat
# Run: uvicorn api:api --reload --host 127.0.0.1 --port 8000

import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import chat, clear_session, get_raw_history

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
api = FastAPI(
    title="LangChain Chat API",
    version="2.0",
    description="Conversational AI withMemory Management"
)

# Add CORS middleware for cross-origin requests
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request/Response Models ───────────────────────────────────────

class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: str = Field(default="default", min_length=1, max_length=50)
    question: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    answer: str

class HistoryItem(BaseModel):
    """History item model"""
    role: str = Field(..., pattern="^(human|ai)$")
    content: str

class HistoryResponse(BaseModel):
    """History response model"""
    session_id: str
    history: List[HistoryItem]

class ClearRequest(BaseModel):
    """Clear request model"""
    session_id: str = Field(..., min_length=1, max_length=50)

class ClearResponse(BaseModel):
    """Clear response model"""
    status: str
    session_id: str
    cleared: bool

# ─── API Endpoints ────────────────────────────────────────────────

@api.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    return {"status": "ok", "version": "2.0"}

@api.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(req: ChatRequest):
    """Send a message and get response with memory"""
    try:
        logger.info(f"Chat request: session={req.session_id}, q_len={len(req.question)}")
        
        # Validate session_id
        if not req.session_id or len(req.session_id) > 50:
            raise ValueError("Invalid session_id")
            
        answer = chat(req.question, req.session_id)
        logger.info(f"Chat success: session={req.session_id}")
        return ChatResponse(session_id=req.session_id, answer=answer)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)[:100]}"
        )

@api.get("/history/{session_id}", response_model=HistoryResponse, tags=["History"])
def history(session_id: str):
    """Get conversation history for a session"""
    try:
        if not session_id or len(session_id) > 50:
            raise ValueError("Invalid session_id")
            
        raw_history = get_raw_history(session_id)
        history_items = [
            HistoryItem(role=item["role"], content=item["content"])
            for item in raw_history
        ]
        logger.info(f"History retrieved: session={session_id}, count={len(history_items)}")
        return HistoryResponse(session_id=session_id, history=history_items)
        
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get history: {str(e)[:100]}"
        )

@api.post("/clear", response_model=ClearResponse, tags=["Session"])
def clear(req: ClearRequest):
    """Clear conversation history for a session"""
    try:
        if not req.session_id or len(req.session_id) > 50:
            raise ValueError("Invalid session_id")
            
        cleared = clear_session(req.session_id)
        logger.info(f"Session cleared: {req.session_id}, success={cleared}")
        return ClearResponse(
            status="success" if cleared else "not_found",
            session_id=req.session_id,
            cleared=cleared
        )
        
    except Exception as e:
        logger.error(f"Clear error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear: {str(e)[:100]}"
        )

# ─── Error Handlers ───────────────────────────────────────────────

@api.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return {
        "detail": f"Validation error: {str(exc)}",
        "status_code": 400
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run(
        api,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
