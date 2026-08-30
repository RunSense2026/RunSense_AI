import traceback

from fastapi import (
    APIRouter,
    HTTPException,
)

from lthr_llm_service import (
    create_lthr_coaching_message,
)

from lthr_schema import (
    LTHRAnalyzeRequest,
    LTHRAnalyzeResponse,
    LTHRCoachingRequest,
    LTHRCoachingResponse,
)

from lthr_service import (
    analyze_lthr,
)


router = APIRouter(
    prefix="/lthr",
    tags=["LTHR"],
)


# =========================================================
# LTHR 계산 API
# =========================================================

@router.post(
    "/analyze",

    response_model=
        LTHRAnalyzeResponse,

    summary=
        "LTHR 테스트 결과 계산",

    description="""
30분 LTHR 테스트에서 수집한 심박수 데이터를 분석합니다.

elapsed_seconds는 테스트 시작 이후 경과 시간입니다.

예:
- 0초 = 테스트 시작
- 600초 = 10분
- 1200초 = 20분
- 1800초 = 30분

계산 항목:
- 후반 20분 평균 심박수 기반 LTHR
- 전체 30분 최고 심박수
- 전체 30분 평균 심박수
- 이전 LTHR 대비 변화량
- LTHR 기반 Z1~Z5 Training Zone
- Zone별 체류시간
- Zone별 비율

이 API에서는 DB 저장, 그래프 생성,
Karvonen 계산을 수행하지 않습니다.
""",

    responses={

        200: {
            "description":
                "LTHR 계산 성공"
        },

        400: {
            "description":
                "심박수 데이터 부족 또는 누락"
        },

        422: {
            "description":
                "요청 데이터 형식 오류"
        },

        500: {
            "description":
                "LTHR 계산 서버 오류"
        },
    },
)
def analyze_lthr_test(
    data: LTHRAnalyzeRequest,
):

    try:

        return analyze_lthr(

            samples=(
                data
                .heart_rate_samples
            ),

            previous_lthr=(
                data
                .previous_lthr
            ),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except HTTPException:

        raise

    except Exception:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,

            detail=(
                "LTHR 계산 중 서버 오류가 "
                "발생했습니다."
            ),
        )


# =========================================================
# LTHR 전용 AI 코치 분석
# =========================================================

@router.post(
    "/coaching",

    response_model=
        LTHRCoachingResponse,

    summary=
        "LTHR 테스트 결과 AI 코치 분석",

    description="""
LTHR 테스트 계산 결과를 기반으로
사후 AI 코칭 문장을 생성합니다.

기존 실시간 러닝 AI 코칭과 별개의 기능입니다.

호출 순서:
1. Gemini
2. Gemini 실패 시 Groq
3. 둘 다 실패 시 규칙 기반 fallback

DB 저장은 수행하지 않습니다.
""",

    responses={

        200: {
            "description":
                "LTHR AI 코치 분석 성공"
        },

        422: {
            "description":
                "요청 데이터 형식 오류"
        },

        500: {
            "description":
                "LTHR AI 분석 서버 오류"
        },
    },
)
def create_lthr_coaching(
    data: LTHRCoachingRequest,
):

    try:

        analysis = (
            create_lthr_coaching_message(
                data
            )
        )

        return {
            "analysis":
                analysis
        }

    except Exception:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,

            detail=(
                "LTHR AI 코치 분석 중 "
                "서버 오류가 발생했습니다."
            ),
        )