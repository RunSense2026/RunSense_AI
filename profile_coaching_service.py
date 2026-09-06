from math import floor

from run_schema import CoachingRequest



ZONE_NAMES = {
    "Z1": "회복",
    "Z2": "유산소",
    "Z3": "템포",
    "Z4": "역치",
    "Z5": "고강도",
}



def _classify_lthr_zone(
    heart_rate: int,
    lthr: int,
) -> str:

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

    if heart_rate < z2_min:
        return "Z1"

    if heart_rate < z3_min:
        return "Z2"

    if heart_rate < z4_min:
        return "Z3"

    if heart_rate < z5_min:
        return "Z4"

    return "Z5"



def analyze_profile_context(
    data: CoachingRequest,
) -> dict:
    

    profile = data.profile

    result = {
        "profile_available": False,
        "lthr_available": False,
        "lthr_ratio": None,
        "training_zone": None,
        "training_zone_name": None,
        "heart_rate_context": None,
    }



    if profile is None:
        return result

    result[
        "profile_available"
    ] = True


    if profile.lthr is None:
        result[
            "heart_rate_context"
        ] = (
            "LTHR 정보가 없어 "
            "개인 심박 구간을 계산할 수 없음"
        )

        return result

    result[
        "lthr_available"
    ] = True


    lthr_ratio = (
        data.heart_rate
        / profile.lthr
        * 100
    )

    lthr_ratio = round(
        lthr_ratio,
        1,
    )


    zone = _classify_lthr_zone(
        data.heart_rate,
        profile.lthr,
    )

    zone_name = (
        ZONE_NAMES[zone]
    )


    if zone == "Z1":
        context = (
            "개인 LTHR 기준 회복 강도"
        )

    elif zone == "Z2":
        context = (
            "개인 LTHR 기준 유산소 강도"
        )

    elif zone == "Z3":
        context = (
            "개인 LTHR 기준 템포 강도"
        )

    elif zone == "Z4":
        context = (
            "개인 LTHR에 근접한 역치 강도"
        )

    else:
        context = (
            "개인 LTHR 이상 고강도"
        )

    result.update(
        {
            "lthr_ratio":
                lthr_ratio,

            "training_zone":
                zone,

            "training_zone_name":
                zone_name,

            "heart_rate_context":
                context,
        }
    )

    return result