@echo off
chcp 65001 >nul
echo ================================================
echo   AI 同步翻译 - 一键启动
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装：https://www.python.org/downloads/
    echo    安装时记得勾选 "Add Python to PATH"
    pause
    exit /b 1
)

:: Install dependencies
echo 📦 安装依赖...
python -m pip install -r requirements.txt -q

:: Ask for API Key if not set
if "%DEEPSEEK_API_KEY%"=="" (
    echo.
    echo 🔑 请输入你的 DeepSeek API Key
    echo    （去 platform.deepseek.com 获取）
    set /p DEEPSEEK_API_KEY=   API Key:
)

if "%DEEPSEEK_API_KEY%"=="" (
    echo ❌ API Key 不能为空
    pause
    exit /b 1
)

echo.
echo ✅ 启动服务中...
echo    本地地址：http://localhost:8000
echo.
echo    iPad 访问请另开命令行运行：ngrok http 8000
echo    停止服务请关闭此窗口
echo ================================================
echo.

:: Open browser
start "" "http://localhost:8000"

python -m uvicorn ai_translation.app:app --host 0.0.0.0 --port 8000
