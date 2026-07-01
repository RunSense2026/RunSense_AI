import os
import re
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from prompt_service import build_coaching_prompt, fallback_message

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY 환경변수가 없습니다.")

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")

groq_client = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[*#`]", "", text)
    text = text.replace('"', "").replace("'", "")
    return " ".join(text.split())


def is_valid_message(message: str) -> bool:
    if not message:
        return False

    if len(message) > 80:
        return False

    return True


def create_message_with_gemini(prompt: str) -> str | None:
    try:
        response = gemini_model.generate_content(prompt)
        message = response.text or ""
        message = clean_text(message)

        if not is_valid_message(message):
            return None

        return message

    except Exception as e:
        print("Gemini 오류:", e)
        return None


def create_message_with_groq(prompt: str) -> str | None:
    if groq_client is None:
        print("Groq 오류: GROQ_API_KEY 환경변수가 없습니다.")
        return None

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 러닝 중인 사용자에게 짧게 말해주는 AI 러닝 코치다. "
                        "반드시 한국어로 한 문장만 말하고, 40자 이내로 답해라."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.4,
            max_tokens=80,
        )

        message = response.choices[0].message.content or ""
        message = clean_text(message)

        if not is_valid_message(message):
            return None

        return message

    except Exception as e:
        print("Groq 오류:", e)
        return None


def create_coaching_message(data, analysis: dict) -> str:

    prompt = build_coaching_prompt(data, analysis)

    gemini_message = create_message_with_gemini(prompt)

    if gemini_message:
        print("LLM 사용: Gemini", flush=True)
        return gemini_message

    groq_message = create_message_with_groq(prompt)

    if groq_message:
        print("LLM 사용: Groq", flush=True)
        return groq_message

    print("LLM 사용: fallback", flush=True)
    return fallback_message(analysis)

