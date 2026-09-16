def calculate_match_score(
    matched_conditions: list,
    failed_conditions: list,
    unverified_conditions: list
) -> float:
    """
    Calculate a simple candidate-match score.

    Important:
    This is NOT an eligibility probability.
    It only represents how much of the known
    profile matches the known scheme requirements.
    """

    known_conditions = (
        len(matched_conditions)
        + len(failed_conditions)
    )

    if known_conditions == 0:
        return 0.0

    score = (
        len(matched_conditions)
        / known_conditions
    )

    return round(score, 2)


def determine_status(
    matched_conditions: list,
    failed_conditions: list,
    unverified_conditions: list
) -> str:
    """
    Determine candidate status.

    not_match:
        At least one known eligibility condition fails.

    strong_candidate:
        No known condition fails and most known
        conditions are satisfied.

    possible_candidate:
        No known condition fails but some
        important information is still unverified.

    needs_verification:
        There is insufficient information to
        make a meaningful assessment.
    """

    if failed_conditions:
        return "not_match"

    if not matched_conditions:
        return "needs_verification"

    if len(unverified_conditions) == 0:
        return "strong_candidate"

    if len(matched_conditions) >= 4:
        return "strong_candidate"

    return "possible_candidate"
