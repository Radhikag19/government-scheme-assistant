import os

import requests
from fastapi import FastAPI, HTTPException

from eligibility.matcher import EligibilityMatcher
from eligibility.profile import UserProfile


DATA_SERVICE_URL = os.getenv(
    "DATA_SERVICE_URL",
    "http://127.0.0.1:9003",
)


app = FastAPI(
    title="Government Scheme Eligibility Service",
    description="Evaluates user profiles against government scheme eligibility rules.",
    version="1.0.0",
)


class EligibilityService:
    def __init__(self):
        self.matcher = EligibilityMatcher()

    def get_schemes_from_data_service(self):
        try:
            response = requests.get(
                f"{DATA_SERVICE_URL}/data/schemes",
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            return data["schemes"]

        except requests.RequestException as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Data Service is unavailable: {str(exc)}",
            )

    def match_profile(self, profile: UserProfile):
        schemes = self.get_schemes_from_data_service()

        results = []

        for scheme in schemes:
            result = self.matcher.match_scheme(
                profile,
                scheme,
            )
            results.append(result)

        results.sort(
            key=lambda result: result.get("score", 0),
            reverse=True,
        )

        return results


eligibility_service = EligibilityService()


@app.get("/")
def root():
    return {
        "service": "eligibility-service",
        "status": "running",
    }


@app.post("/eligibility/match")
def match_eligibility(profile: UserProfile):
    try:
        results = eligibility_service.match_profile(profile)

        return {
            "profile": profile.model_dump(),
            "results": results,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Eligibility matching failed: {str(exc)}",
        )
