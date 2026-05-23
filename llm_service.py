import os

import google.generativeai as genai

from dotenv import load_dotenv

from prompt_service import build_prompt

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)


model = genai.GenerativeModel(
    "gemini-2.5-flash-lite"
)


# Gemini 호출
def create_coaching_message(data, analysis):

    prompt = build_prompt(data, analysis)

    response = model.generate_content(prompt)

    return response.text

# Gemini 오류 처리

def create_coaching_message(data, analysis):

    prompt = build_prompt(data, analysis)

    try:

        response = model.generate_content(prompt)

        if not response.text:
            return "현재 페이스를 유지해보세요."

        return response.text.strip()

    except Exception as e:

        print("Gemini 오류:", e)

        return "러닝 리듬을 안정적으로 유지해보세요."