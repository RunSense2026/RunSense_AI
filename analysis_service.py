from run_schema import CoachingRequest


def analyze_run(data: CoachingRequest) -> dict:
    issues = []

    if data.heart_rate >= 175:
        issues.append("심박수 높음")

    if data.cadence < 160:
        issues.append("케이던스 낮음")

    if data.pronation_type == "overpronation":
        issues.append("과회내 경향")

    elif data.pronation_type == "supination":
        issues.append("회외 경향")

    if data.heel_strike_rate is not None and data.heel_strike_rate >= 80:
        issues.append("뒤꿈치 착지 비율 높음")

    if data.foot_side in ["left", "right"] and data.pronation_type:
        issues.append(f"{data.foot_side} 발 착지 패턴 확인 필요")

    if data.hitmap_json:
        forefoot_left = data.hitmap_json.get("forefoot_left", 0)
        forefoot_right = data.hitmap_json.get("forefoot_right", 0)
        midfoot_left = data.hitmap_json.get("midfoot_left", 0)
        midfoot_right = data.hitmap_json.get("midfoot_right", 0)
        heel = data.hitmap_json.get("heel", 0)

        forefoot_total = forefoot_left + forefoot_right
        midfoot_total = midfoot_left + midfoot_right
        left_total = forefoot_left + midfoot_left
        right_total = forefoot_right + midfoot_right
        total_pressure = forefoot_total + midfoot_total + heel

        if heel >= 70:
            issues.append("뒤꿈치 압력 집중")

        if forefoot_total >= 70:
            issues.append("앞발 압력 집중")

        if midfoot_total <= 10 and total_pressure > 0:
            issues.append("중족부 압력 낮음")

        if total_pressure > 0:
            left_ratio = (left_total / total_pressure) * 100
            right_ratio = (right_total / total_pressure) * 100
            heel_ratio = (heel / total_pressure) * 100
            forefoot_ratio = (forefoot_total / total_pressure) * 100
            midfoot_ratio = (midfoot_total / total_pressure) * 100

            balance_gap = abs(left_ratio - right_ratio)

            if balance_gap >= 20:
                issues.append("좌우 압력 불균형")

            if left_ratio >= 60:
                issues.append("왼쪽 압력 편중")

            elif right_ratio >= 60:
                issues.append("오른쪽 압력 편중")

            if heel_ratio >= 50:
                issues.append("뒤꿈치 중심 착지")

            if forefoot_ratio >= 60:
                issues.append("앞발 중심 착지")

            if midfoot_ratio >= 40:
                issues.append("중족부 사용 양호")

        forefoot_gap = abs(forefoot_left - forefoot_right)
        midfoot_gap = abs(midfoot_left - midfoot_right)

        if forefoot_gap >= 25:
            issues.append("앞발 좌우 압력 차이 큼")

        if midfoot_gap >= 25:
            issues.append("중족부 좌우 압력 차이 큼")

    if "심박수 높음" in issues and "케이던스 낮음" in issues:
        issues.append("피로 누적 가능성")

    if "뒤꿈치 압력 집중" in issues and "뒤꿈치 착지 비율 높음" in issues:
        issues.append("뒤꿈치 착지 습관 강함")

    if "좌우 압력 불균형" in issues and (
        "과회내 경향" in issues or "회외 경향" in issues
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

    elif "좌우 압력 불균형" in issues:
        focus_point = "좌우 균형 개선"
        rec_exercise = "한 발 균형 잡기와 좌우 밸런스 러닝"

    elif "과회내 경향" in issues:
        focus_point = "발목 안정성"
        rec_exercise = "발목 안정화 운동과 밸런스 훈련"

    elif "회외 경향" in issues:
        focus_point = "착지 균형 개선"
        rec_exercise = "발바닥 전체 착지 연습"

    elif "뒤꿈치 착지 습관 강함" in issues:
        focus_point = "뒤꿈치 착지 개선"
        rec_exercise = "미드풋 착지 연습과 보폭 조절 훈련"

    elif "뒤꿈치 압력 집중" in issues or "뒤꿈치 중심 착지" in issues:
        focus_point = "뒤꿈치 착지 개선"
        rec_exercise = "미드풋 착지 연습"

    elif "앞발 압력 집중" in issues or "앞발 중심 착지" in issues:
        focus_point = "앞발 부담 완화"
        rec_exercise = "종아리 스트레칭과 보폭 조절 훈련"

    elif "중족부 압력 낮음" in issues:
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