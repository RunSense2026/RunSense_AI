import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from prompt_service import build_coaching_prompt, fallback_message

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY 환경변수가 없습니다.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[*#`]", "", text)
    text = text.replace('"', "").replace("'", "")
    return " ".join(text.split())


def create_coaching_message(data, analysis: dict) -> str:
    prompt = build_coaching_prompt(data, analysis)

    try:
        response = model.generate_content(prompt)
        message = response.text or ""
        message = clean_text(message)

        if not message:
            return fallback_message(analysis)

        if len(message) > 80:
            return fallback_message(analysis)

        return message

    except Exception as e:
        print("Gemini 오류:", e)
        return fallback_message(analysis)