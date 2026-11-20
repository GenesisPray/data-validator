@echo off
title MedBalance Data Validator
echo =========================================================
echo   Starting MedBalance Data Validator Web App...
echo =========================================================
echo.

:: Open default browser to the web app
start "" "index.html"

:: Also start the local Python server
echo Starting Python Web Server on port 8000...
echo You can also access the server at: http://localhost:8000
python server.py

pause

