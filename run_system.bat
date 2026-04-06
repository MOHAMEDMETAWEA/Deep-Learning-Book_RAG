@echo off
TITLE Deep Learning RAG System Launcher
echo ===================================================
echo 🚀 Starting Deep Learning RAG System...
echo ===================================================

:: Check for virtual environment and activate it if present
if exist venv\Scripts\activate (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo [1/3] No virtual environment found. Using system python.
)

:: Start the Backend API in a separate window to avoid background crashes and allow monitoring
echo [2/3] Launching FastAPI Backend (Port 8000)...
start "RAG Backend API" cmd /k "python -m uvicorn rag_api:app --port 8000"

:: Wait for API to initialize (increased to 10 seconds due to embedding model load time)
echo [3/4] Waiting 10 seconds for API to spin up...
timeout /t 10 /nobreak > NUL

:: Start the Streamlit Frontend
echo [4/4] Launching Streamlit Frontend (Port 8501)...
streamlit run frontend.py

:: Use pause to keep the window open so the user can see logs.
pause
