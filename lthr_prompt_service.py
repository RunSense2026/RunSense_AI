from lthr_schema import LTHRCoachingRequest


def build_lthr_coaching_prompt(
    data: LTHRCoachingRequest,
) -> str:
    """
    LTHR 테스트 결과를 기반으로
    AI 코치에게 전달할 프롬프트를 생성합니다.
    """

    zone_text = "\n".join(
        (
            f"- {zone.zone} "
            f"{zone.name}: "
            f"{zone.percentage}% "
            f"({zone.duration_seconds}초)"
        )
        for zone in data.zones
    )

    # 이전 LTHR
    if data.previous_lthr is not None:
        previous_text = f"{data.previous_lthr} bpm"
    else:
        previous_text = "최초 측정"

    # 이전 대비 변화량
    if data.lthr_difference is not None:
        difference_text = f"{data.lthr_difference:+d} bpm"
    else:
        difference_text = "비교값 없음"

    prompt = f"""
너는 LTHR 테스트 결과를 분석하는 AI 러닝 코치다.

[LTHR 테스트 결과]

- 현재 LTHR: {data.lthr} bpm
- 이전 LTHR: {previous_text}
- 이전 측정 대비 변화: {difference_text}
- 최고 심박수: {data.max_heart_rate} bpm
- 전체 평균 심박수: {data.average_heart_rate} bpm

[Training Zone 분포]

{zone_text}

[응답 조건]

- 반드시 한국어만 사용한다.
- 최대 2문장으로 작성한다.
- 현재 테스트 결과에서 가장 중요한 특징을 설명한다.
- LTHR 변화량과 Training Zone 분포를 함께 고려한다.
- 사용자가 다음 러닝에서 실천할 수 있는 간단한 조언을 포함한다.
- 의학적 진단은 하지 않는다.
- LTHR이 상승했다고 해서 운동 능력이 반드시 향상됐다고 단정하지 않는다.
- 지나치게 전문적인 표현을 사용하지 않는다.
- 마크다운을 사용하지 않는다.
- 제목을 출력하지 않는다.
- 따옴표를 사용하지 않는다.
""".strip()

    return prompt


def lthr_fallback_message(
    data: LTHRCoachingRequest,
) -> str:
    """
    Gemini와 Groq 호출이 모두 실패했을 때
    사용할 규칙 기반 LTHR 코칭 문장입니다.
    """

    zone_map = {
        zone.zone: zone.percentage
        for zone in data.zones
    }

    z1 = zone_map.get("Z1", 0)
    z2 = zone_map.get("Z2", 0)
    z3 = zone_map.get("Z3", 0)
    z4 = zone_map.get("Z4", 0)
    z5 = zone_map.get("Z5", 0)

    high_intensity = z4 + z5

    # 이전 LTHR보다 상승
    if (
        data.lthr_difference is not None
        and data.lthr_difference > 0
    ):
        if high_intensity >= 50:
            return (
                f"지난 측정보다 LTHR이 "
                f"{data.lthr_difference}bpm 높게 측정되었고 "
                "역치 이상 구간의 비중도 높았습니다. "
                "다음 러닝에서는 가벼운 회복 주행을 병행해보세요."
            )

        return (
            f"지난 측정보다 LTHR이 "
            f"{data.lthr_difference}bpm 높게 측정되었습니다. "
            "현재 훈련 리듬을 유지하면서 다음 측정 결과도 함께 비교해보세요."
        )

    # 이전 LTHR보다 감소
    if (
        data.lthr_difference is not None
        and data.lthr_difference < 0
    ):
        return (
            f"지난 측정보다 LTHR이 "
            f"{abs(data.lthr_difference)}bpm 낮게 측정되었습니다. "
            "현재 컨디션을 확인하며 훈련 강도를 조절하고 충분히 회복해보세요."
        )

    # 고강도 비율이 높은 경우
    if high_intensity >= 50:
        return (
            "역치 이상 구간의 비중이 높게 나타났습니다. "
            "다음 러닝에서는 회복 구간을 충분히 확보해보세요."
        )

    # Z2 비율이 높은 경우
    if z2 >= 40:
        return (
            "유산소 구간을 안정적으로 유지한 테스트였습니다. "
            "현재 기반을 유지하면서 템포 훈련을 조금씩 추가해보세요."
        )

    # Z5가 특히 높은 경우
    if z5 >= 25:
        return (
            "고강도 구간의 비중이 비교적 높게 나타났습니다. "
            "다음 훈련에서는 강도를 낮춘 회복 러닝을 함께 진행해보세요."
        )

    # Z1이 지나치게 높은 경우
    if z1 >= 50:
        return (
            "회복 구간의 비중이 높게 나타났습니다. "
            "컨디션이 괜찮다면 다음 테스트에서는 목표 강도를 조금 더 안정적으로 유지해보세요."
        )

    # 기본 응답
    return (
        "현재 LTHR과 트레이닝 존 분포를 기준으로 훈련 강도를 조절해보세요. "
        "다음 테스트도 비슷한 조건에서 진행해 변화 추이를 확인해보세요."
    )