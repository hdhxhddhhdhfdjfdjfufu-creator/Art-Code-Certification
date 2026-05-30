import json
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI

app = FastAPI(title="AI Sync Translation")
app.mount("/static", StaticFiles(directory="ai_translation/static"), name="static")

client = AsyncOpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

LANGUAGES = {
    "zh": "Chinese (Simplified)",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
}


@app.get("/")
async def root():
    with open("ai_translation/static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            text = msg.get("text", "").strip()
            target_lang = msg.get("target_lang", "zh")

            if not text:
                continue

            if not client.api_key:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "未设置 DEEPSEEK_API_KEY 环境变量",
                }))
                continue

            target_lang_name = LANGUAGES.get(target_lang, "Chinese")

            try:
                stream = await client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"You are a professional simultaneous interpreter. "
                                f"Translate the input text to {target_lang_name}. "
                                f"Output ONLY the translation. No explanations, no extra text."
                            ),
                        },
                        {"role": "user", "content": text},
                    ],
                    stream=True,
                    max_tokens=1000,
                    temperature=0.3,
                )

                full_translation = ""
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_translation += delta
                        await websocket.send_text(json.dumps({
                            "type": "chunk",
                            "content": delta,
                        }))

                await websocket.send_text(json.dumps({
                    "type": "done",
                    "translation": full_translation,
                    "original": text,
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                }))

    except WebSocketDisconnect:
        pass
