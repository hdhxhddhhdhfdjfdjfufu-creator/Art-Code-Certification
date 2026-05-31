#!/bin/bash
set -e

echo "================================================"
echo "  AI 同步翻译 - 一键启动"
echo "================================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌ 未找到 Python3，请先安装：https://www.python.org/downloads/"
  read -p "按回车键退出..."
  exit 1
fi

# Install dependencies
echo "📦 安装依赖..."
python3 -m pip install -r requirements.txt -q

# Ask for API Key if not set
if [ -z "$DEEPSEEK_API_KEY" ]; then
  echo ""
  echo "🔑 请输入你的 DeepSeek API Key"
  echo "   （去 platform.deepseek.com 获取，没有可先注册）"
  read -p "   API Key: " DEEPSEEK_API_KEY
  export DEEPSEEK_API_KEY
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
  echo "❌ API Key 不能为空"
  read -p "按回车键退出..."
  exit 1
fi

echo ""
echo "✅ 启动服务中..."
echo "   本地地址：http://localhost:8000"
echo ""
echo "   iPad 访问请另开终端运行：ngrok http 8000"
echo "   停止服务请按 Ctrl+C"
echo "================================================"
echo ""

# Open browser after 1.5s
(sleep 1.5 && open "http://localhost:8000") &

python3 -m uvicorn ai_translation.app:app --host 0.0.0.0 --port 8000
