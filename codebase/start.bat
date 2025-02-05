@echo off
echo Starting Luna Cursor Boost...

REM Create and activate Python virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install Python dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Install npm dependencies if package.json exists
if exist "package.json" (
    echo Installing npm dependencies...
    npm install
)

REM Start Flask backend in a new window
start cmd /k "echo Starting Flask backend... && venv\Scripts\python app.py"

REM Start React frontend
echo Starting React frontend...
npm start 