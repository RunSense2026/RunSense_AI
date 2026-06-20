def build_coaching_prompt(data, analysis: dict) -> str:
    hitmap = data.hitmap_json or {}

    forefoot_left = hitmap.get("forefoot_left", 0)
    forefoot_right = hitmap.get("forefoot_right", 0)
    midfoot_left = hitmap.get("midfoot_left", 0)
    midfoot_right = hitmap.get("midfoot_right", 0)
    heel = hitmap.get("heel", 0)

    return f"""
너는 러닝 중인 사용자에게 짧게 말해주는 AI 러닝 코치다.

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
- 문제점과 개선 포인트를 기반으로 코칭 문장을 만들어야 함
- 사용자의 입장에서 거부감이 들지 않도록 존댓말로 출력

러닝 데이터:
- 페이스: {data.pace}
- 심박수: {data.heart_rate}
- 케이던스: {data.cadence}
- 발 방향: {data.foot_side}
- 회내 유형: {data.pronation_type}
- 뒤꿈치 착지 비율: {data.heel_strike_rate}

족압 히트맵 데이터:
- 앞발 왼쪽 압력: {forefoot_left}
- 앞발 오른쪽 압력: {forefoot_right}
- 중족부 왼쪽 압력: {midfoot_left}
- 중족부 오른쪽 압력: {midfoot_right}
- 뒤꿈치 압력: {heel}

서버 분석:
- 문제점: {", ".join(analysis["issues"])}
- 핵심 개선 포인트: {analysis["focus_point"]}
- 추천 운동: {analysis["rec_exercise"]}

위 내용을 바탕으로 러닝 중 바로 들을 수 있는 짧은 코칭 문장만 출력해라.
""".strip()


def fallback_message(analysis: dict) -> str:
    issues = analysis.get("issues", [])

    if "피로 누적 가능성" in issues:
        return "페이스를 낮추고 호흡을 안정시켜보세요."

    if "심박수 높음" in issues:
        return "심박이 높습니다. 호흡을 안정시켜보세요."

    if "케이던스 낮음" in issues:
        return "보폭을 줄이고 발걸음을 가볍게 해보세요."

    if "발목 안정성 저하 가능성" in issues:
        return "착지 균형을 유지하며 달려보세요."

    if "좌우 압력 불균형" in issues:
        return "좌우 균형을 맞추며 달려보세요."

    if "왼쪽 압력 편중" in issues:
        return "왼발에 힘이 치우치지 않게 해보세요."

    if "오른쪽 압력 편중" in issues:
        return "오른발에 힘이 치우치지 않게 해보세요."

    if "과회내 경향" in issues:
        return "발목이 안쪽으로 무너지지 않게 해보세요."

    if "회외 경향" in issues:
        return "발바닥 전체로 균형 있게 착지해보세요."

    if "뒤꿈치 착지 습관 강함" in issues:
        return "뒤꿈치 충격을 줄이고 부드럽게 착지해보세요."

    if "뒤꿈치 압력 집중" in issues:
        return "뒤꿈치 충격을 줄여보세요."

    if "뒤꿈치 중심 착지" in issues:
        return "발 전체로 부드럽게 착지해보세요."

    if "앞발 압력 집중" in issues:
        return "앞발 부담을 줄이고 보폭을 안정시켜보세요."

    if "앞발 중심 착지" in issues:
        return "보폭을 조금 줄이고 리듬을 유지해보세요."

    if "중족부 압력 낮음" in issues:
        return "발 전체를 활용해 부드럽게 착지해보세요."

    if "앞발 좌우 압력 차이 큼" in issues:
        return "앞발 좌우 균형을 맞춰보세요."

    if "중족부 좌우 압력 차이 큼" in issues:
        return "발 중앙 균형을 안정적으로 유지해보세요."

    return "현재 리듬을 안정적으로 유지해보세요."