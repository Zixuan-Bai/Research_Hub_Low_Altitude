@echo off
setlocal
cd /d "%~dp0"

python -m streamlit run scripts\review_app.py
if errorlevel 1 (
  echo.
  echo Streamlit 启动失败。请先确认已经运行：
  echo pip install -r requirements.txt
  echo.
  pause
)
