import base64
from datetime import datetime
import os
from abc import ABC, abstractmethod
from typing import Literal

import aiofiles
from dotenv import load_dotenv
import aiohttp


load_dotenv()


class TextToSpeach(ABC):
    def __init__(self, voices: dict[str, list], url: str):  # lang: ['voice_id',]
        self.voices = voices
        self.url = url

    @abstractmethod
    async def text_to_speach(text: str, voice_id: str, user_id: int) -> str:
        pass

    @abstractmethod
    async def get_voices(self, gender: Literal["man", "woman"]) -> list[str]:
        pass

    @abstractmethod
    async def save_audio(self, audio_data: str, user_id: int) -> str:
        pass


class SpeechifyTextToSpeach(TextToSpeach):
    def __init__(self, voices: dict[str, list], url: str):
        self.voices = voices
        self.url = url

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
)
