from run_schema import RunData


# 러닝 데이터 분석
def analyze_run(data: RunData):

    issues = []

    if data.heart_rate >= 175:
        issues.append("심박수 높음")

    if data.cadence < 160:
        issues.append("케이던스 낮음")

    return {
        "status": "주의",
        "issues": issues
    }