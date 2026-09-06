from math import floor

from lthr_schema import (
    HeartRateSample,
    LTHRZoneResult,
)


# =========================================================
# 테스트 기준
# =========================================================

TEST_DURATION_SECONDS = 30 * 60
# 1800초 = 30분

LTHR_WINDOW_SECONDS = 20 * 60
# 1200초 = 20분

LTHR_WINDOW_START_SECONDS = (
    TEST_DURATION_SECONDS
    - LTHR_WINDOW_SECONDS
)
# 600초 = 10분

# 즉:
#
# 0 ~ 600초
# 테스트 전반부 10분
#
# 600 ~ 1800초
# LTHR 계산에 사용하는 후반 20분


# =========================================================
# 데이터 검증 기준
# =========================================================

START_TOLERANCE_SECONDS = 5

END_TOLERANCE_SECONDS = 5

MIN_SAMPLE_COUNT = 10


# 심박수 데이터가 중간에 너무 오래 끊긴 경우
# 직전 심박을 계속 유지했다고 판단하면
# 계산이 왜곡될 수 있으므로 오류 처리
MAX_ALLOWED_GAP_SECONDS = 120


# =========================================================
# Zone 이름
# =========================================================

ZONE_NAMES = {
    "Z1": "회복",
    "Z2": "유산소",
    "Z3": "템포",
    "Z4": "역치",
    "Z5": "무산소",
}


# =========================================================
# 심박수 데이터 정리
# =========================================================

def _normalize_samples(
    samples: list[HeartRateSample],
) -> list[HeartRateSample]:

    # 0 ~ 1800초 사이 데이터만 사용
    valid_samples = [
        sample
        for sample in samples
        if (
            0
            <= sample.elapsed_seconds
            <= TEST_DURATION_SECONDS
        )
    ]

    # 시간순 정렬
    valid_samples.sort(
        key=lambda sample:
            sample.elapsed_seconds
    )

    # 동일 elapsed_seconds 데이터가
    # 여러 번 들어온 경우 마지막 값 사용
    deduplicated: dict[
        float,
        HeartRateSample
    ] = {}

    for sample in valid_samples:

        deduplicated[
            sample.elapsed_seconds
        ] = sample

    return sorted(
        deduplicated.values(),

        key=lambda sample:
            sample.elapsed_seconds,
    )


# =========================================================
# 데이터 유효성 검사
# =========================================================

def _validate_samples(
    samples: list[HeartRateSample],
) -> None:

    if len(samples) < MIN_SAMPLE_COUNT:

        raise ValueError(
            "심박수 데이터가 너무 적습니다. "
            f"최소 {MIN_SAMPLE_COUNT}개 이상의 "
            "측정값이 필요합니다."
        )

    first_time = (
        samples[0]
        .elapsed_seconds
    )

    last_time = (
        samples[-1]
        .elapsed_seconds
    )

    # 시작 데이터 확인
    if (
        first_time
        > START_TOLERANCE_SECONDS
    ):

        raise ValueError(
            "테스트 시작 구간의 "
            "심박수 데이터가 부족합니다."
        )

    # 종료 데이터 확인
    if (
        last_time
        <
        TEST_DURATION_SECONDS
        - END_TOLERANCE_SECONDS
    ):

        raise ValueError(
            "30분 테스트 완료 시점까지의 "
            "심박수 데이터가 부족합니다."
        )

    # 너무 긴 데이터 누락 검사
    for current, next_sample in zip(
        samples,
        samples[1:],
    ):

        gap = (
            next_sample.elapsed_seconds
            - current.elapsed_seconds
        )

        if gap > MAX_ALLOWED_GAP_SECONDS:

            raise ValueError(
                "심박수 데이터 사이에 "
                f"{gap:.1f}초의 공백이 있습니다. "
                f"{MAX_ALLOWED_GAP_SECONDS}초를 "
                "초과하는 누락 구간은 "
                "계산하지 않습니다."
            )



def _iter_intervals(
    samples: list[HeartRateSample],
    range_start: float,
    range_end: float,
):

    if (
        not samples
        or range_end <= range_start
    ):
        return

    first = samples[0]

    # 첫 샘플이 1~5초 정도 늦게 들어온 경우
    # 첫 HR 값을 테스트 시작까지 확장
    if first.elapsed_seconds > range_start:

        start = range_start

        end = min(
            first.elapsed_seconds,
            range_end,
        )

        if end > start:

            yield (
                first.heart_rate,
                end - start,
            )

    # 샘플과 다음 샘플 사이의 시간 계산
    for index, current in enumerate(
        samples
    ):

        current_start = (
            current.elapsed_seconds
        )

        if (
            index + 1
            < len(samples)
        ):

            next_time = (
                samples[
                    index + 1
                ].elapsed_seconds
            )

        else:

            next_time = (
                range_end
            )

        start = max(
            current_start,
            range_start,
        )

        end = min(
            next_time,
            range_end,
        )

        if end > start:

            yield (
                current.heart_rate,
                end - start,
            )

        if current_start >= range_end:
            break


# =========================================================
# 시간 가중 평균
# =========================================================

def _time_weighted_average(
    samples: list[HeartRateSample],
    range_start: float,
    range_end: float,
) -> int:

    weighted_sum = 0.0

    total_duration = 0.0

    for (
        heart_rate,
        duration,
    ) in _iter_intervals(
        samples,
        range_start,
        range_end,
    ):

        weighted_sum += (
            heart_rate
            * duration
        )

        total_duration += duration

    if total_duration <= 0:

        raise ValueError(
            "평균 심박수를 계산할 수 있는 "
            "유효한 데이터가 없습니다."
        )

    return round(
        weighted_sum
        / total_duration
    )



def _build_zone_ranges(
    lthr: int,
) -> dict[
    str,
    tuple[
        int | None,
        int | None,
    ],
]:

    z2_min = floor(
        lthr * 0.81
    )

    z3_min = floor(
        lthr * 0.89
    )

    z4_min = floor(
        lthr * 0.94
    )

    z5_min = lthr

    return {

        "Z1": (
            None,
            z2_min - 1,
        ),

        "Z2": (
            z2_min,
            z3_min - 1,
        ),

        "Z3": (
            z3_min,
            z4_min - 1,
        ),

        "Z4": (
            z4_min,
            z5_min - 1,
        ),

        "Z5": (
            z5_min,
            None,
        ),
    }


# =========================================================
# 해당 심박수 Zone 판별
# =========================================================

def _classify_zone(
    heart_rate: int,
    lthr: int,
) -> str:

    ranges = (
        _build_zone_ranges(
            lthr
        )
    )

    if (
        heart_rate
        <= ranges["Z1"][1]
    ):
        return "Z1"

    if (
        heart_rate
        <= ranges["Z2"][1]
    ):
        return "Z2"

    if (
        heart_rate
        <= ranges["Z3"][1]
    ):
        return "Z3"

    if (
        heart_rate
        <= ranges["Z4"][1]
    ):
        return "Z4"

    return "Z5"


# =========================================================
# Zone별 체류시간 / 비율 계산
# =========================================================

def _calculate_zones(
    samples: list[HeartRateSample],
    lthr: int,
) -> list[LTHRZoneResult]:

    durations = {
        zone: 0.0
        for zone
        in ZONE_NAMES
    }

    # 전체 30분 기준
    for (
        heart_rate,
        duration,
    ) in _iter_intervals(
        samples,
        0,
        TEST_DURATION_SECONDS,
    ):

        zone = (
            _classify_zone(
                heart_rate,
                lthr,
            )
        )

        durations[zone] += (
            duration
        )

    total_duration = sum(
        durations.values()
    )

    if total_duration <= 0:

        raise ValueError(
            "Training Zone을 계산할 수 있는 "
            "심박수 데이터가 없습니다."
        )

    ranges = (
        _build_zone_ranges(
            lthr
        )
    )

    results: list[
        LTHRZoneResult
    ] = []

    for zone in (
        "Z1",
        "Z2",
        "Z3",
        "Z4",
        "Z5",
    ):

        min_bpm, max_bpm = (
            ranges[zone]
        )

        duration = (
            durations[zone]
        )

        percentage = (
            duration
            / total_duration
            * 100
        )

        results.append(
            LTHRZoneResult(

                zone=zone,

                name=(
                    ZONE_NAMES[
                        zone
                    ]
                ),

                min_bpm=min_bpm,

                max_bpm=max_bpm,

                duration_seconds=round(
                    duration,
                    1,
                ),

                percentage=round(
                    percentage,
                    1,
                ),
            )
        )

    # ---------------------------------------------
    # 8.3 + 21.7 + ... 등의 반올림 때문에
    # 전체 합계가 99.9 또는 100.1이 될 수 있음
    #
    # 가장 오래 머문 Zone에 오차를 더해
    # 정확히 100.0%가 되도록 처리
    # ---------------------------------------------

    percentage_sum = round(
        sum(
            zone.percentage
            for zone
            in results
        ),
        1,
    )

    correction = round(
        100.0
        - percentage_sum,
        1,
    )

    if correction != 0:

        largest_zone = max(
            results,

            key=lambda zone:
                zone.duration_seconds,
        )

        largest_zone.percentage = round(
            largest_zone.percentage
            + correction,
            1,
        )

    return results


# =========================================================
# 최종 LTHR 분석
# =========================================================

def analyze_lthr(
    samples: list[HeartRateSample],
    previous_lthr: int | None = None,
) -> dict:

    # ---------------------------------------------
    # 데이터 정리
    # ---------------------------------------------

    normalized_samples = (
        _normalize_samples(
            samples
        )
    )

    # ---------------------------------------------
    # 데이터 검증
    # ---------------------------------------------

    _validate_samples(
        normalized_samples
    )

    # ---------------------------------------------
    # LTHR
    #
    # 600초 ~ 1800초
    # 즉 후반 20분 평균
    # ---------------------------------------------

    lthr = (
        _time_weighted_average(
            normalized_samples,

            LTHR_WINDOW_START_SECONDS,

            TEST_DURATION_SECONDS,
        )
    )

    # ---------------------------------------------
    # 전체 30분 평균 심박
    # ---------------------------------------------

    average_heart_rate = (
        _time_weighted_average(
            normalized_samples,

            0,

            TEST_DURATION_SECONDS,
        )
    )

    # ---------------------------------------------
    # 전체 30분 최고 심박
    # ---------------------------------------------

    max_heart_rate = max(
        sample.heart_rate

        for sample
        in normalized_samples
    )

    # ---------------------------------------------
    # 이전 LTHR와 차이
    # ---------------------------------------------

    if previous_lthr is not None:

        lthr_difference = (
            lthr
            - previous_lthr
        )

    else:

        lthr_difference = None

    # ---------------------------------------------
    # Training Zone 계산
    # ---------------------------------------------

    zones = (
        _calculate_zones(
            normalized_samples,
            lthr,
        )
    )

    return {

        "lthr":
            lthr,

        "previous_lthr":
            previous_lthr,

        "lthr_difference":
            lthr_difference,

        "max_heart_rate":
            max_heart_rate,

        "average_heart_rate":
            average_heart_rate,

        "zones":
            zones,
    }