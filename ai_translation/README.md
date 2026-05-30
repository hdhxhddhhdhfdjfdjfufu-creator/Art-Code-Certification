# AI 同步翻译

实时语音翻译工具：麦克风输入 → 浏览器语音识别 → DeepSeek 流式翻译 → TTS 语音播报。

## 技术架构

```
浏览器 Web Speech API (STT)
       ↓  WebSocket (文字)
FastAPI 后端
       ↓  DeepSeek API (流式)
浏览器 实时显示 + TTS 朗读
```

## 快速开始

**1. 安装依赖**
```bash
cd ai_translation
pip install -r requirements.txt
```

**2. 设置 DeepSeek API Key**
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```
> 在 [platform.deepseek.com](https://platform.deepseek.com) 获取 API Key

**3. 启动服务**
```bash
# 在项目根目录运行
uvicorn ai_translation.app:app --reload --host 0.0.0.0 --port 8000
```

**4. 打开浏览器**
```
http://localhost:8000
```
> 推荐使用 Chrome 或 Edge（语音识别支持最好）

## 功能

- 实时语音识别（支持中/英/日/韩/法/德/西/意/俄）
- DeepSeek 流式翻译，逐词实时显示
- TTS 语音播报译文，可手动或自动触发
- 翻译历史记录
- 语言一键互换
- 深色主题 UI

## 支持语言

| 识别 | 翻译输出 |
|------|---------|
| 中文 / English / 日本語 / 한국어 | 同上 + Français / Deutsch / Español / Italiano / Русский |
