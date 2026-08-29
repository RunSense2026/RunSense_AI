import os
import re

from dotenv import load_dotenv

from lthr_prompt_service import (
    build_lthr_coaching_prompt,
    lthr_fallback_message,
)

from lthr_schema import (
    LTHRCoachingRequest,
)


# =========================================================
# Gemini
#
# 패키지가 없어도 서버 전체가 죽지 않도록 처리
# =========================================================

try:

    import google.generativeai as genai

except ImportError:

    genai = None


# =========================================================
# Groq
# =========================================================

try:

    from groq import Groq

except ImportError:

    Groq = None


load_dotenv()


# =========================================================
# 환경변수
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash-lite",
)


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.1-8b-instant",
)


# =========================================================
# Gemini 초기화
# =========================================================

gemini_model = None


if (
    genai is not None
    and GEMINI_API_KEY
):

    try:

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        gemini_model = (
            genai.GenerativeModel(
                GEMINI_MODEL
            )
        )

    except Exception as e:

        print(
            "LTHR Gemini 초기화 오류:",
            e,
            flush=True,
        )


# =========================================================
# Groq 초기화
# =========================================================

groq_client = None


if (
    Groq is not None
    and GROQ_API_KEY
):

    try:

        groq_client = Groq(
            api_key=GROQ_API_KEY
        )

    except Exception as e:

        print(
            "LTHR Groq 초기화 오류:",
            e,
            flush=True,
        )


# =========================================================
# LLM 응답 정리
# =========================================================

def _clean_message(
    message: str,
) -> str:

    cleaned = (
        message
        .strip()
        .replace(
            "```",
            "",
        )
    )

    cleaned = re.sub(
        r'^[\"\'“”]+|[\"\'“”]+$',
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    )

    return (
        cleaned.strip()
    )


# =========================================================
# Gemini 호출
# =========================================================

def _create_with_gemini(
    prompt: str,
) -> str | None:

    if gemini_model is None:
        return None

    try:

        response = (
            gemini_model.generate_content(
                prompt
            )
        )

        if (
            response
            and response.text
        ):

            message = (
                response.text
            )

        else:

            message = ""

        message = (
            _clean_message(
                message
            )
        )

        if not message:
            return None

        return message

    except Exception as e:

        print(
            "LTHR Gemini 오류:",
            e,
            flush=True,
        )

        return None


# =========================================================
# Groq 호출
# =========================================================

def _create_with_groq(
    prompt: str,
) -> str | None:

    if groq_client is None:
        return None

    try:

        response = (
            groq_client
            .chat
            .completions
            .create(

                model=GROQ_MODEL,

                messages=[
                    {
                        "role":
                            "user",

                        "content":
                            prompt,
                    }
                ],

                temperature=0.4,

                max_tokens=180,
            )
        )

        message = (
            response
            .choices[0]
            .message
            .content
            or ""
        )

        message = (
            _clean_message(
                message
            )
        )

        if not message:
            return None

        return message

    except Exception as e:

        print(
            "LTHR Groq 오류:",
            e,
            flush=True,
        )

        return None


# =========================================================
# 최종 LTHR AI 코칭 생성
#
# Gemini
# ↓
# Groq
# ↓
# fallback
# =========================================================

def create_lthr_coaching_message(
    data: LTHRCoachingRequest,
) -> str:

    prompt = (
        build_lthr_coaching_prompt(
            data
        )
    )

    # Gemini
    gemini_message = (
        _create_with_gemini(
            prompt
        )
    )

    if gemini_message:

        print(
            "LTHR LLM 사용: Gemini",
            flush=True,
        )

        return gemini_message

    # Groq
    groq_message = (
        _create_with_groq(
            prompt
        )
    )

    if groq_message:

        print(
            "LTHR LLM 사용: Groq",
            flush=True,
        )

        return groq_message

    # fallback
    print(
        "LTHR LLM 사용: fallback",
        flush=True,
    )

    return (
        lthr_fallback_message(
            data
        )
    )