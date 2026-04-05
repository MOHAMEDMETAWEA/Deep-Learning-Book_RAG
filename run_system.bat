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

:: Start the Backend API in the background
echo [2/3] Launching FastAPI Backend (Port 8000)...
start /b python -m uvicorn rag_api:app --reload --port 8000

:: Wait for API to initialize
echo [3/4] Waiting 5 seconds for API to spin up...
timeout /t 5 /nobreak > NUL

:: Start the Streamlit Frontend
echo [4/4] Launching Streamlit Frontend (Port 8501)...
streamlit run frontend.py

:: If the command above exits, the background tasks are still running.
:: We use pause to keep the window open so the user can see logs.
pause
