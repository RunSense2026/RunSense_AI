# Gemini 프롬프트 생성

def build_prompt(data, analysis):

    return f'''
너는 AI 러닝 코치다.

조건:
- 한국어만 사용
- 한 문장만 출력
- 설명 금지
- 40자 이내

러닝 상태:
- 상태: {analysis["status"]}
- 문제점: {", ".join(analysis["issues"])}

러닝 데이터:
- 페이스: {data.pace}
- 심박수: {data.heart_rate}
- 케이던스: {data.cadence}

짧은 코칭 문장만 출력해라.
'''