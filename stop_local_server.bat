@echo off
echo Stopping local embedding/reranker server...
taskkill /f /fi "WINDOWTITLE eq *local_embed*" /im python.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq local_embed*" /im python.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9997" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo Server stopped. GPU memory freed.
