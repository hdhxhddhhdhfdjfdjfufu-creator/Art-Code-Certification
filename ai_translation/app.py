import json
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI

# Resolve paths relative to this file so they work regardless of cwd
BASE_DIR    = Path(__file__).parent
STATIC_DIR  = BASE_DIR / "static"
INDEX_HTML  = STATIC_DIR / "index.html"

app = FastAPI(title="AI Sync Translation")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            text = msg.get("text", "").strip()
            target_lang = msg.get("target_lang", "zh")
            is_final = msg.get("isFinal", True)

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
                    "isFinal": is_final,
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                }))

    except WebSocketDisconnect:
        pass
