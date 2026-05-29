from run_schema import CoachingRequest


def analyze_run(data: CoachingRequest) -> dict:
    issues = []

    if data.heart_rate >= 175:
        issues.append("심박수 높음")

    if data.cadence < 160:
        issues.append("케이던스 낮음")

    if data.pronation_type == "overpronation":
        issues.append("과회내 경향")

    if data.pronation_type == "supination":
        issues.append("회외 경향")

    if data.heel_strike_rate is not None and data.heel_strike_rate >= 80:
        issues.append("뒤꿈치 착지 비율 높음")

    if data.foot_side in ["left", "right"] and data.pronation_type:
        issues.append(f"{data.foot_side} 발 착지 패턴 확인 필요")

    if data.hitmap_json:
        heel_pressure = data.hitmap_json.get("heel", 0)
        forefoot_pressure = data.hitmap_json.get("forefoot", 0)

        if heel_pressure >= 70:
            issues.append("뒤꿈치 압력 집중")

        if forefoot_pressure >= 70:
            issues.append("앞발 압력 집중")

    if not issues:
        issues.append("특이사항 없음")

    if "심박수 높음" in issues:
        focus_point = "호흡 안정과 페이스 조절"
        rec_exercise = "가벼운 조깅과 호흡 조절 훈련"

    elif "케이던스 낮음" in issues:
        focus_point = "케이던스 유지"
        rec_exercise = "짧은 보폭 러닝과 리듬 훈련"

    elif "과회내 경향" in issues:
        focus_point = "발목 안정성"
        rec_exercise = "발목 안정화 운동과 밸런스 훈련"

    elif "회외 경향" in issues:
        focus_point = "착지 균형 개선"
        rec_exercise = "발바닥 전체 착지 연습"

    elif "뒤꿈치 착지 비율 높음" in issues or "뒤꿈치 압력 집중" in issues:
        focus_point = "착지 자세 개선"
        rec_exercise = "미드풋 착지 연습"

    elif "앞발 압력 집중" in issues:
        focus_point = "앞발 부담 완화"
        rec_exercise = "종아리 스트레칭과 보폭 조절 훈련"

    else:
        focus_point = "현재 리듬 유지"
        rec_exercise = "가벼운 지속주"

    return {
        "issues": issues,
        "focus_point": focus_point,
        "rec_exercise": rec_exercise,
    }