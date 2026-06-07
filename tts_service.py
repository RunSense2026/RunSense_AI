import os
import time
import uuid
from gtts import gTTS

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


def cleanup_old_audio_files(hours: int = 24):
    now = time.time()
    expire_seconds = hours * 60 * 60

    for file_name in os.listdir(AUDIO_DIR):
        if not file_name.endswith(".mp3"):
            continue

        file_path = os.path.join(AUDIO_DIR, file_name)

        if not os.path.isfile(file_path):
            continue

        file_age = now - os.path.getmtime(file_path)

        if file_age > expire_seconds:
            os.remove(file_path)


def create_tts_file(text: str) -> str:
    cleanup_old_audio_files(hours=24)

    file_name = f"coach_{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    tts = gTTS(text=text, lang="ko", slow=False)
    tts.save(file_path)

    return f"/audio/{file_name}"