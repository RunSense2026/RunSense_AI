import os
import uuid
import threading
from pathlib import Path

from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI

load_dotenv()

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")
OPENAI_TTS_FORMAT = os.getenv("OPENAI_TTS_FORMAT", "mp3")
OPENAI_TTS_SPEED = float(os.getenv("OPENAI_TTS_SPEED", "1.0"))

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def delete_file_later(file_path: str, delay_seconds: int = 300):
    def delete_file():
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"오디오 파일 삭제 완료: {file_path}", flush=True)
        except Exception as e:
            print(f"오디오 파일 삭제 실패: {e}", flush=True)

    timer = threading.Timer(delay_seconds, delete_file)
    timer.daemon = True
    timer.start()


def create_gtts_file(text: str) -> str:
    file_name = f"coach_{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    tts = gTTS(text=text, lang="ko", slow=False)
    tts.save(file_path)

    delete_file_later(file_path, delay_seconds=300)

    print("TTS 사용: gTTS", flush=True)

    return f"/audio/{file_name}"


def create_openai_tts_file(text: str) -> str:
    if openai_client is None:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 없습니다.")

    file_name = f"coach_{uuid.uuid4().hex}.{OPENAI_TTS_FORMAT}"
    file_path = Path(AUDIO_DIR) / file_name

    with openai_client.audio.speech.with_streaming_response.create(
        model=OPENAI_TTS_MODEL,
        voice=OPENAI_TTS_VOICE,
        input=text,
        response_format=OPENAI_TTS_FORMAT,
        speed=OPENAI_TTS_SPEED,
    ) as response:
        response.stream_to_file(file_path)

    delete_file_later(str(file_path), delay_seconds=300)

    print("TTS 사용: OpenAI TTS", flush=True)

    return f"/audio/{file_name}"


def create_tts_file(text: str) -> str:
    try:
        return create_openai_tts_file(text)

    except Exception as e:
        print("OpenAI TTS 오류:", e, flush=True)
        return create_gtts_file(text)