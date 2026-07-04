def build_coaching_prompt(data, analysis: dict) -> str:
    issues = ", ".join(analysis.get("issues", []))
    focus_point = analysis.get("focus_point", "현재 리듬 유지")
    rec_exercise = analysis.get("rec_exercise", "가벼운 지속주")

    left = data.left_foot
    right = data.right_foot

    left_hitmap = left.hitmap
    right_hitmap = right.hitmap

    prompt = f"""
너는 러닝 중인 사용자에게 실시간으로 짧게 코칭해주는 AI 러닝 코치다.

현재 러닝 데이터:
- 페이스: {data.pace}
- 심박수: {data.heart_rate}
- 케이던스: {data.cadence}

왼발 데이터:
- 회내/회외 상태: {left.pronation_type}
- 뒤꿈치 착지 비율: {left.heel_strike_rate}
- 앞쪽 왼쪽 압력: {left_hitmap.forefoot_left}
- 앞쪽 오른쪽 압력: {left_hitmap.forefoot_right}
- 중간 왼쪽 압력: {left_hitmap.midfoot_left}
- 중간 오른쪽 압력: {left_hitmap.midfoot_right}
- 뒤꿈치 압력: {left_hitmap.heel}

오른발 데이터:
- 회내/회외 상태: {right.pronation_type}
- 뒤꿈치 착지 비율: {right.heel_strike_rate}
- 앞쪽 왼쪽 압력: {right_hitmap.forefoot_left}
- 앞쪽 오른쪽 압력: {right_hitmap.forefoot_right}
- 중간 왼쪽 압력: {right_hitmap.midfoot_left}
- 중간 오른쪽 압력: {right_hitmap.midfoot_right}
- 뒤꿈치 압력: {right_hitmap.heel}

분석 결과:
- 문제점: {issues}
- 집중 코칭 포인트: {focus_point}
- 추천 운동: {rec_exercise}

조건:
- 반드시 한국어만 사용
- 반드시 한 문장만 출력
- 설명 금지
- 해설 금지
- 마크다운 금지
- 제목 금지
- 따옴표 금지
- 40자 이내
- 러닝 중 바로 들을 수 있는 코칭만 출력
- 사용자가 바로 행동할 수 있는 말로 출력 
- 분석 결과 중 현재 러닝에 가장 직접적인 문제만 선택해 코칭한다.
- 선택한 문제를 문장에 구체적으로 포함한다.
- 문제점과 개선 포인트를 기반으로 코칭 문장을 만들어야 함
- 사용자의 입장에서 거부감이 들지 않도록 존댓말로 출력
""".strip()

    return prompt


def fallback_message(analysis: dict) -> str:
    issues = analysis.get("issues", [])

    if "피로 누적 가능성" in issues:
        return "무리하지 말고 페이스를 낮춰보세요."

    if "심박수 높음" in issues:
        return "호흡을 안정시키고 페이스를 낮춰보세요."

    if "케이던스 낮음" in issues:
        return "보폭을 줄이고 발걸음을 가볍게 해보세요."

    if "발목 안정성 저하 가능성" in issues:
        return "발목이 흔들리지 않게 착지해보세요."

    if "양발 하중 불균형" in issues:
        return "양발에 고르게 힘을 싣고 달려보세요."

    if "왼발 하중 편중" in issues:
        return "왼발 힘을 줄이고 균형을 맞춰보세요."

    if "오른발 하중 편중" in issues:
        return "오른발 힘을 줄이고 균형을 맞춰보세요."

    if "왼발 과회내 경향" in issues or "오른발 과회내 경향" in issues:
        return "발목이 안쪽으로 무너지지 않게 해보세요."

    if "왼발 회외 경향" in issues or "오른발 회외 경향" in issues:
        return "발바닥 전체로 부드럽게 착지해보세요."

    if "뒤꿈치 착지 습관 강함" in issues:
        return "뒤꿈치 충격을 줄이고 보폭을 줄여보세요."

    if "왼발 뒤꿈치 중심 착지" in issues or "오른발 뒤꿈치 중심 착지" in issues:
        return "뒤꿈치 충격을 줄이고 부드럽게 착지하세요."

    if "왼발 앞발 중심 착지" in issues or "오른발 앞발 중심 착지" in issues:
        return "앞발 부담을 줄이고 보폭을 안정시켜보세요."

    if "왼발 중족부 압력 낮음" in issues or "오른발 중족부 압력 낮음" in issues:
        return "발 전체를 활용해 부드럽게 착지해보세요."

    return "현재 리듬을 안정적으로 유지해보세요."