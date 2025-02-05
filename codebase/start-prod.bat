@echo off
echo Starting Luna Cursor Boost in Production Mode...

REM Set environment variables
set FLASK_ENV=production
set FLASK_DEBUG=0

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

REM Build React frontend
echo Building React frontend...
npm run build

REM Start production server using gunicorn
echo Starting production server...
venv\Scripts\gunicorn --bind 0.0.0.0:5000 wsgi:app 