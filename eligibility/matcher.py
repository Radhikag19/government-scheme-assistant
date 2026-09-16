import json
import re
from pathlib import Path

from eligibility.profile import UserProfile
from eligibility.scorer import (
    calculate_match_score,
    determine_status
)


METADATA_PATH = Path("data/scheme_metadata.json")


class EligibilityMatcher:

    def __init__(self):

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.schemes = data["schemes"]

    # ==================================================
    # GENERAL HELPERS
    # ==================================================

    def _as_list(self, value):

        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]

    def _normalise(self, value):

        return str(
            value
        ).lower().strip()

    # ==================================================
    # TEXT MATCHING
    # ==================================================

    def _text_matches(
        self,
        user_value,
        required_value
    ):

        if user_value is None:
            return False

        user_text = self._normalise(
            user_value
        )

        for value in self._as_list(
            required_value
        ):

            required_text = self._normalise(
                value
            )

            if user_text == required_text:
                return True

            if user_text in required_text:
                return True

            if required_text in user_text:
                return True

        return False

    # ==================================================
    # STUDY YEAR MATCHING
    # ==================================================

    def _study_year_matches(
        self,
        user_year,
        requirement
    ):

        if user_year is None:
            return None

        requirement_text = self._normalise(
            requirement
        )

        # ----------------------------------------------
        # Explicit ranges
        # ----------------------------------------------

        ranges = re.findall(
            r"(\d+)\s*(?:st|nd|rd|th)?\s*(?:-|to|and)\s*(\d+)",
            requirement_text
        )

        for start, end in ranges:

            if int(start) <= user_year <= int(end):
                return True

        # ----------------------------------------------
        # Individual years
        # ----------------------------------------------

        numbers = re.findall(
            r"\b([1-5])(?:st|nd|rd|th)\b",
            requirement_text
        )

        if numbers:

            allowed_years = [
                int(number)
                for number in numbers
            ]

            if user_year in allowed_years:
                return True

        # ----------------------------------------------
        # First year / fresh
        # ----------------------------------------------

        if (
            user_year == 1
            and
            (
                "first year" in requirement_text
                or
                "1st year" in requirement_text
                or
                "fresh" in requirement_text
            )
        ):

            return True

        # ----------------------------------------------
        # Second year
        # ----------------------------------------------

        if (
            user_year == 2
            and
            (
                "second year" in requirement_text
                or
                "2nd year" in requirement_text
            )
        ):

            return True

        return False

    # ==================================================
    # CATEGORY MATCHING
    # ==================================================

    def _category_requirement_is_specific(
        self,
        requirement
    ):

        requirement_text = self._normalise(
            requirement
        )

        specific_categories = [
            "sc",
            "st",
            "obc",
            "general",
            "ews"
        ]

        for category in specific_categories:

            if re.search(
                rf"\b{re.escape(category)}\b",
                requirement_text
            ):

                return True

        return False

    # ==================================================
    # MATCH SCHEME
    # ==================================================

    def match_scheme(
        self,
        profile: UserProfile,
        scheme: dict
    ):

        matched_conditions = []
        failed_conditions = []
        unverified_conditions = []

        eligibility = scheme.get(
            "eligibility",
            {}
        )

        # ==================================================
        # GENDER
        # ==================================================

        required_gender = eligibility.get(
            "gender"
        )

        if required_gender:

            allowed_genders = [
                self._normalise(value)
                for value in self._as_list(
                    required_gender
                )
            ]

            # If both male and female are listed,
            # the scheme is not gender restricted.

            if (
                "male" in allowed_genders
                and
                "female" in allowed_genders
            ):

                pass

            elif profile.gender is None:

                unverified_conditions.append(
                    f"Gender requirement: "
                    f"{required_gender}"
                )

            elif self._text_matches(
                profile.gender,
                required_gender
            ):

                matched_conditions.append(
                    "Gender requirement satisfied"
                )

            else:

                failed_conditions.append(
                    f"Gender does not match "
                    f"required value: {required_gender}"
                )

        # ==================================================
        # EDUCATION LEVEL
        # ==================================================

        required_education = eligibility.get(
            "education_level"
        )

        if required_education:

            if profile.education_level is None:

                unverified_conditions.append(
                    f"Education requirement: "
                    f"{required_education}"
                )

            elif self._text_matches(
                profile.education_level,
                required_education
            ):

                matched_conditions.append(
                    "Education level matches"
                )

            else:

                failed_conditions.append(
                    f"Education level does not match "
                    f"required value: {required_education}"
                )

        # ==================================================
        # COURSE TYPE
        # ==================================================

        required_course_type = eligibility.get(
            "course_type"
        )

        if required_course_type:

            if profile.course_type is None:

                unverified_conditions.append(
                    f"Course type requirement: "
                    f"{required_course_type}"
                )

            elif self._text_matches(
                profile.course_type,
                required_course_type
            ):

                matched_conditions.append(
                    "Course type matches"
                )

            else:

                failed_conditions.append(
                    f"Course type does not match "
                    f"required value: {required_course_type}"
                )

        # ==================================================
        # STUDY YEAR
        # ==================================================

        required_study_year = eligibility.get(
            "study_year"
        )

        if required_study_year:

            if profile.study_year is None:

                unverified_conditions.append(
                    f"Study year requirement: "
                    f"{required_study_year}"
                )

            else:

                study_year_matched = False

                for requirement in self._as_list(
                    required_study_year
                ):

                    if self._study_year_matches(
                        profile.study_year,
                        requirement
                    ):

                        study_year_matched = True
                        break

                if study_year_matched:

                    matched_conditions.append(
                        "Study year matches"
                    )

                else:

                    failed_conditions.append(
                        f"Study year does not match "
                        f"required value: "
                        f"{required_study_year}"
                    )

        # ==================================================
        # CATEGORY
        # ==================================================

        required_category = eligibility.get(
            "category"
        )

        if required_category:

            specific_requirement = False

            for requirement in self._as_list(
                required_category
            ):

                if self._category_requirement_is_specific(
                    requirement
                ):

                    specific_requirement = True
                    break

            # Descriptive requirements such as:
            # "Reservation as per Government of India norms"
            # are not treated as exact categories.

            if not specific_requirement:

                unverified_conditions.append(
                    f"Category requirement requires "
                    f"verification: {required_category}"
                )

            elif profile.category is None:

                unverified_conditions.append(
                    f"Category requirement: "
                    f"{required_category}"
                )

            elif self._text_matches(
                profile.category,
                required_category
            ):

                matched_conditions.append(
                    "Category matches"
                )

            else:

                failed_conditions.append(
                    f"Category does not match "
                    f"required value: {required_category}"
                )

        # ==================================================
        # DISABILITY
        # ==================================================

        disability_requirement = eligibility.get(
            "disability"
        )

        if disability_requirement:

            if profile.disability is None:

                unverified_conditions.append(
                    f"Disability requirement: "
                    f"{disability_requirement}"
                )

            elif profile.disability:

                matched_conditions.append(
                    "Disability requirement may be satisfied"
                )

            else:

                unverified_conditions.append(
                    "Disability-related provision "
                    "requires verification"
                )

        # ==================================================
        # INCOME
        # ==================================================

        income_requirement = eligibility.get(
            "income_limit"
        )

        if income_requirement:

            if profile.annual_income is None:

                unverified_conditions.append(
                    "Annual income is required"
                )

            else:

                income_limit = None

                # Existing metadata stores income as:
                #
                # {
                #     "amount": 450000,
                #     "currency": "INR",
                #     "period": "annual"
                # }

                if isinstance(
                    income_requirement,
                    dict
                ):

                    income_limit = income_requirement.get(
                        "amount"
                    )

                else:

                    try:

                        income_limit = float(
                            income_requirement
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        income_limit = None

                if income_limit is not None:

                    if (
                        profile.annual_income
                        <= income_limit
                    ):

                        matched_conditions.append(
                            "Annual income is within limit"
                        )

                    else:

                        failed_conditions.append(
                            "Annual income exceeds limit"
                        )

                else:

                    unverified_conditions.append(
                        f"Income requirement: "
                        f"{income_requirement}"
                    )

        # ==================================================
        # GEOGRAPHY
        # ==================================================

        geography_requirement = eligibility.get(
            "geography"
        )

        if geography_requirement:

            if profile.geography is None:

                unverified_conditions.append(
                    "Geographical eligibility "
                    "requires verification"
                )

            elif isinstance(
                geography_requirement,
                dict
            ):

                details = geography_requirement.get(
                    "details",
                    ""
                )

                unverified_conditions.append(
                    f"Geography requires verification: "
                    f"{details}"
                )

            elif self._text_matches(
                profile.geography,
                geography_requirement
            ):

                matched_conditions.append(
                    "Geography matches"
                )

            else:

                failed_conditions.append(
                    "Geography does not match"
                )

        # ==================================================
        # INSTITUTION TYPE
        # ==================================================

        institution_requirement = eligibility.get(
            "institution_type"
        )

        if institution_requirement:

            if profile.institution_type is None:

                unverified_conditions.append(
                    f"Institution requirement: "
                    f"{institution_requirement}"
                )

            elif self._text_matches(
                profile.institution_type,
                institution_requirement
            ):

                matched_conditions.append(
                    "Institution type matches"
                )

            else:

                # Institution requirements can be
                # descriptive, so avoid incorrectly
                # rejecting the user.

                unverified_conditions.append(
                    f"Institution requirement needs "
                    f"verification: "
                    f"{institution_requirement}"
                )

        # ==================================================
        # ACADEMIC REQUIREMENT
        # ==================================================

        academic_requirement = eligibility.get(
            "academic_requirement"
        )

        if academic_requirement:

            if (
                profile.academic_percentage is None
                and
                profile.academic_percentile is None
            ):

                unverified_conditions.append(
                    f"Academic requirement: "
                    f"{academic_requirement}"
                )

            else:

                academic_text = self._normalise(
                    academic_requirement
                )

                # ------------------------------------------
                # Percentile requirement
                # ------------------------------------------

                if (
                    profile.academic_percentile
                    is not None
                    and
                    "percentile" in academic_text
                ):

                    if (
                        profile.academic_percentile
                        > 80
                    ):

                        matched_conditions.append(
                            "Academic percentile "
                            "appears to satisfy requirement"
                        )

                    else:

                        failed_conditions.append(
                            "Academic percentile does "
                            "not satisfy requirement"
                        )

                else:

                    unverified_conditions.append(
                        f"Academic requirement: "
                        f"{academic_requirement}"
                    )

        # ==================================================
        # SPECIAL CONDITIONS
        # ==================================================

        special_conditions = eligibility.get(
            "special_conditions"
        )

        if special_conditions:

            for condition in self._as_list(
                special_conditions
            ):

                unverified_conditions.append(
                    f"Special condition: {condition}"
                )

        # ==================================================
        # SCORE
        # ==================================================

        score = calculate_match_score(
            matched_conditions,
            failed_conditions,
            unverified_conditions
        )

        # ==================================================
        # STATUS
        # ==================================================

        status = determine_status(
            matched_conditions,
            failed_conditions,
            unverified_conditions
        )

        # ==================================================
        # RESULT
        # ==================================================

        return {
            "scheme_id":
                scheme["scheme_id"],

            "scheme_name":
                scheme.get(
                    "scheme_name",
                    scheme["scheme_id"]
                ),

            "score":
                score,

            "status":
                status,

            "matched_conditions":
                matched_conditions,

            "failed_conditions":
                failed_conditions,

            "unverified_conditions":
                unverified_conditions
        }

    # ==================================================
    # MATCH ALL SCHEMES
    # ==================================================

    def match_all(
        self,
        profile: UserProfile
    ):

        results = []

        for scheme in self.schemes:

            result = self.match_scheme(
                profile,
                scheme
            )

            results.append(result)

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results
