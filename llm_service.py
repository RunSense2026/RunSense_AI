import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"

print("현재 모델:", GEMINI_MODEL)

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY 환경변수가 없습니다.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

def create_message(data):
    print("create_message에서 사용하는 모델:", GEMINI_MODEL)

    prompt = f"""
너는 AI 러닝 코치다.

조건:
- 반드시 한국어만 사용
- 반드시 한 문장만 출력
- 설명 금지
- 해설 금지
- 마크다운 금지
- 제목 금지
- 추가 팁 금지
- 따옴표 금지
- 30자 이내
- 러닝 중 음성으로 들을 짧은 코칭만 출력

러닝 데이터:
- 페이스: {data.pace}초/km
- 심박수: {data.heart_rate}bpm
- 케이던스: {data.cadence}spm
"""

    try:
        response = model.generate_content(prompt)

        if not response.text:
            return "러닝 데이터를 확인했습니다. 호흡을 안정시키며 현재 페이스를 유지해보세요."

        return response.text

    except Exception as e:
        return f"Gemini API 오류: {e}"