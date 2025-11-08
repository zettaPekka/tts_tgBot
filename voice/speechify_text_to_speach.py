import aiofiles
from dotenv import load_dotenv
import aiohttp

import base64
from datetime import datetime
import os
from typing import Literal


from .base_text_to_speach import TextToSpeach


load_dotenv()


class SpeechifyTextToSpeach(TextToSpeach):
    def __init__(self, voices: dict[str, list], url: str, voice_languages):
        self.voices = voices
        self.url = url
        self.voice_languages = voice_languages

    async def text_to_speach(self, text: str, voice_id: str, user_id: int) -> str:
        model = "simba-multilingual"

        headers = {
            "Authorization": f'Bearer {os.getenv("TTS_TOKEN")}',
            "Content-Type": "application/json",
        }

        body = {"input": text, "voice_id": voice_id, "model": model}

        async with aiohttp.ClientSession(headers=headers) as sess:
            async with sess.post(self.url, json=body) as res:
                res = await res.json()
                audio_data = res["audio_data"]
                return await self.save_audio(audio_data, user_id)

    async def save_audio(self, audio_data: str, user_id: int) -> str:
        path = f"audio/audio_{datetime.now().timestamp()}_{user_id}.wav"
        audio_bytes = base64.b64decode(audio_data)

        async with aiofiles.open(path, "wb") as f:
            await f.write(audio_bytes)

        return path

    async def get_voices(self, gender: Literal["man", "woman"]) -> list[str]:
        return self.voices[gender]


speechify_text_to_speach = SpeechifyTextToSpeach(
    voices={
        "man": ["mikhail", "fedor", "vladislav", "oliver", "george", "henry"],
        "woman": ["olga", "ludmila", "irina", "lisa", "lindsey", "evelyn"],
    },
    url="https://api.sws.speechify.com/v1/audio/speech",
    voice_languages = {
        "mikhail": "RU 🇷🇺",
        "fedor": "RU 🇷🇺",
        "vladislav": "RU 🇷🇺",
        "oliver": "EN 🇺🇸",
        "george": "EN 🇺🇸",
        "henry": "EN 🇺🇸",
        "olga": "RU 🇷🇺",
        "ludmila": "RU 🇷🇺",
        "irina": "RU 🇷🇺",
        "lisa": "EN 🇺🇸",
        "lindsey": "EN 🇺🇸",
        "evelyn": "EN 🇺🇸",
    }
)
