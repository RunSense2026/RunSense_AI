def build_coaching_prompt(data, analysis: dict) -> str:
    return f'''
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

러닝 데이터:
- activity_id: {data.activity_id}
- user_id: {data.user_id}
- 페이스: {data.pace}
- 심박수: {data.heart_rate}
- 케이던스: {data.cadence}
- 회내 유형: {data.pronation_type}
- 뒤꿈치 착지 비율: {data.heel_strike_rate}

서버 분석:
- 문제점: {", ".join(analysis["issues"])}
- 핵심 개선 포인트: {analysis["focus_point"]}
- 추천 운동: {analysis["rec_exercise"]}

짧은 코칭 문장만 출력해라.
'''.strip()

def fallback_message(analysis: dict) -> str:
    issues = analysis.get("issues", [])

    if "심박수 높음" in issues:
        return "심박이 높습니다. 호흡을 안정시켜보세요."
    if "케이던스 낮음" in issues:
        return "보폭을 줄이고 발걸음을 가볍게 해보세요."
    if "과회내 경향" in issues:
        return "발목이 안쪽으로 무너지지 않게 신경 써보세요."
    if "뒤꿈치 착지 비율 높음" in issues:
        return "발을 조금 더 부드럽게 내려놓아보세요."

    return "현재 리듬을 안정적으로 유지해보세요."
