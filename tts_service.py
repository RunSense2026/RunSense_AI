import os
import uuid
from gtts import gTTS

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


def create_tts_file(text: str) -> str:
    file_name = f"coach_{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    tts = gTTS(text=text, lang="ko", slow=False)
    tts.save(file_path)

    return f"/audio/{file_name}"