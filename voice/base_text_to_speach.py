from abc import ABC, abstractmethod
from typing import Literal


class TextToSpeach(ABC):
    def __init__(self, voices: dict[str, list], url: str, voice_languages: dict):  # lang: ['voice_id',]
        self.voices = voices
        self.url = url
        self.voice_languages = voice_languages

    @abstractmethod
    async def text_to_speach(text: str, voice_id: str, user_id: int) -> str:
        pass

    @abstractmethod
    async def get_voices(self, gender: Literal["man", "woman"]) -> list[str]:
        pass

    @abstractmethod
    async def save_audio(self, audio_data: str, user_id: int) -> str:
        pass