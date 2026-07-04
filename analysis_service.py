from run_schema import CoachingRequest


def _get_foot_total(foot_data) -> float:
    hitmap = foot_data.hitmap

    return (
        hitmap.forefoot_left
        + hitmap.forefoot_right
        + hitmap.midfoot_left
        + hitmap.midfoot_right
        + hitmap.heel
    )


def _analyze_single_foot(foot_name: str, foot_data) -> list:
    issues = []

    pronation_type = foot_data.pronation_type
    heel_strike_rate = foot_data.heel_strike_rate
    hitmap = foot_data.hitmap

    forefoot_left = hitmap.forefoot_left
    forefoot_right = hitmap.forefoot_right
    midfoot_left = hitmap.midfoot_left
    midfoot_right = hitmap.midfoot_right
    heel = hitmap.heel

    forefoot_total = forefoot_left + forefoot_right
    midfoot_total = midfoot_left + midfoot_right
    foot_total = forefoot_total + midfoot_total + heel

    if pronation_type == "overpronation":
        issues.append(f"{foot_name} 과회내 경향")
    elif pronation_type == "supination":
        issues.append(f"{foot_name} 회외 경향")

    if heel_strike_rate is not None and heel_strike_rate >= 80:
        issues.append(f"{foot_name} 뒤꿈치 착지 비율 높음")

    if foot_total <= 0:
        return issues

    forefoot_ratio = (forefoot_total / foot_total) * 100
    midfoot_ratio = (midfoot_total / foot_total) * 100
    heel_ratio = (heel / foot_total) * 100

    inner_left_total = forefoot_left + midfoot_left
    inner_right_total = forefoot_right + midfoot_right
    inner_gap = abs(inner_left_total - inner_right_total)

    forefoot_gap = abs(forefoot_left - forefoot_right)
    midfoot_gap = abs(midfoot_left - midfoot_right)

    if heel_ratio >= 50:
        issues.append(f"{foot_name} 뒤꿈치 중심 착지")

    if forefoot_ratio >= 60:
        issues.append(f"{foot_name} 앞발 중심 착지")

    if midfoot_ratio <= 10:
        issues.append(f"{foot_name} 중족부 압력 낮음")

    if inner_gap >= 20:
        issues.append(f"{foot_name} 내부 좌우 압력 불균형")

    if forefoot_gap >= 25:
        issues.append(f"{foot_name} 앞발 좌우 압력 차이 큼")

    if midfoot_gap >= 25:
        issues.append(f"{foot_name} 중족부 좌우 압력 차이 큼")

    return issues


def analyze_run(data: CoachingRequest) -> dict:
    issues = []

    if data.heart_rate >= 175:
        issues.append("심박수 높음")

    if data.cadence < 160:
        issues.append("케이던스 낮음")

    left_total = _get_foot_total(data.left_foot)
    right_total = _get_foot_total(data.right_foot)
    total_pressure = left_total + right_total

    if total_pressure > 0:
        left_ratio = (left_total / total_pressure) * 100
        right_ratio = (right_total / total_pressure) * 100
        balance_gap = abs(left_ratio - right_ratio)

        if balance_gap >= 20:
            issues.append("양발 하중 불균형")

        if left_ratio >= 60:
            issues.append("왼발 하중 편중")
        elif right_ratio >= 60:
            issues.append("오른발 하중 편중")

    issues.extend(_analyze_single_foot("왼발", data.left_foot))
    issues.extend(_analyze_single_foot("오른발", data.right_foot))

    if "심박수 높음" in issues and "케이던스 낮음" in issues:
        issues.append("피로 누적 가능성")

    if (
        "왼발 뒤꿈치 착지 비율 높음" in issues
        and "왼발 뒤꿈치 중심 착지" in issues
    ) or (
        "오른발 뒤꿈치 착지 비율 높음" in issues
        and "오른발 뒤꿈치 중심 착지" in issues
    ):
        issues.append("뒤꿈치 착지 습관 강함")

    if "양발 하중 불균형" in issues and (
        "왼발 과회내 경향" in issues
        or "오른발 과회내 경향" in issues
        or "왼발 회외 경향" in issues
        or "오른발 회외 경향" in issues
    ):
        issues.append("발목 안정성 저하 가능성")

    if not issues:
        issues.append("특이사항 없음")

    if "피로 누적 가능성" in issues:
        focus_point = "피로 관리와 페이스 조절"
        rec_exercise = "러닝 강도를 낮추고 충분한 회복 조깅을 진행하세요."
    elif "심박수 높음" in issues:
        focus_point = "호흡 안정과 페이스 조절"
        rec_exercise = "가벼운 조깅과 호흡 조절 훈련"
    elif "케이던스 낮음" in issues:
        focus_point = "케이던스 유지"
        rec_exercise = "짧은 보폭 러닝과 리듬 훈련"
    elif "발목 안정성 저하 가능성" in issues:
        focus_point = "발목 안정성 개선"
        rec_exercise = "발목 안정화 운동과 밸런스 훈련"
    elif "양발 하중 불균형" in issues:
        focus_point = "양발 균형 개선"
        rec_exercise = "좌우 균형 러닝과 한 발 균형 잡기"
    elif "왼발 하중 편중" in issues:
        focus_point = "왼발 하중 편중 개선"
        rec_exercise = "오른발 지지 안정화와 좌우 밸런스 훈련"
    elif "오른발 하중 편중" in issues:
        focus_point = "오른발 하중 편중 개선"
        rec_exercise = "왼발 지지 안정화와 좌우 밸런스 훈련"
    elif "왼발 과회내 경향" in issues or "오른발 과회내 경향" in issues:
        focus_point = "발목 안정성"
        rec_exercise = "발목 안정화 운동과 밸런스 훈련"
    elif "왼발 회외 경향" in issues or "오른발 회외 경향" in issues:
        focus_point = "착지 균형 개선"
        rec_exercise = "발바닥 전체 착지 연습"
    elif "뒤꿈치 착지 습관 강함" in issues:
        focus_point = "뒤꿈치 착지 개선"
        rec_exercise = "미드풋 착지 연습과 보폭 조절 훈련"
    elif "왼발 뒤꿈치 중심 착지" in issues or "오른발 뒤꿈치 중심 착지" in issues:
        focus_point = "뒤꿈치 착지 개선"
        rec_exercise = "미드풋 착지 연습"
    elif "왼발 앞발 중심 착지" in issues or "오른발 앞발 중심 착지" in issues:
        focus_point = "앞발 부담 완화"
        rec_exercise = "종아리 스트레칭과 보폭 조절 훈련"
    elif "왼발 중족부 압력 낮음" in issues or "오른발 중족부 압력 낮음" in issues:
        focus_point = "발바닥 전체 착지 유도"
        rec_exercise = "발 전체로 부드럽게 착지하는 러닝 훈련"
    else:
        focus_point = "현재 리듬 유지"
        rec_exercise = "가벼운 지속주"

    return {
        "issues": issues,
        "focus_point": focus_point,
        "rec_exercise": rec_exercise,
    }