@echo off
REM Start the FastAPI server
start cmd /k uvicorn api:app --reload

REM Give some time for the FastAPI server to start
timeout /t 5

REM Start the Streamlit app
start cmd /k streamlit run app.py

exit
