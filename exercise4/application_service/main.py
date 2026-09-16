import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from eligibility.profile import UserProfile


ELIGIBILITY_SERVICE_URL = os.getenv(
    "ELIGIBILITY_SERVICE_URL",
    "http://127.0.0.1:9001",
)

RAG_SERVICE_URL = os.getenv(
    "RAG_SERVICE_URL",
    "http://127.0.0.1:9002",
)

DATA_SERVICE_URL = os.getenv(
    "DATA_SERVICE_URL",
    "http://127.0.0.1:9003",
)

LLM_SERVICE_URL = os.getenv(
    "LLM_SERVICE_URL",
    "http://127.0.0.1:9004",
)


app = FastAPI(
    title="Government Scheme Application Service",
    description="Main orchestration service for the Government Scheme Assistant.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    prompt: str


class QueryRequest(BaseModel):
    scheme_id: str
    question: str
    top_k: int = 5


def handle_service_error(
    exc: requests.RequestException,
    service_name: str,
):
    raise HTTPException(
        status_code=503,
        detail=f"{service_name} is unavailable: {str(exc)}",
    )


@app.get("/")
def root():
    return {
        "service": "application-service",
        "status": "running",
    }


@app.get("/api/schemes")
def get_schemes():
    try:
        response = requests.get(
            f"{DATA_SERVICE_URL}/data/schemes",
            timeout=30,
        )
        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        handle_service_error(exc, "Data Service")


@app.post("/api/eligibility/check")
def check_eligibility(profile: UserProfile):
    try:
        response = requests.post(
            f"{ELIGIBILITY_SERVICE_URL}/eligibility/match",
            json=profile.model_dump(),
            timeout=60,
        )
        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        handle_service_error(exc, "Eligibility Service")


@app.post("/api/ask")
def ask_llm(request: AskRequest):
    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    try:
        response = requests.post(
            f"{LLM_SERVICE_URL}/llm/generate",
            json={
                "prompt": request.prompt,
            },
            timeout=180,
        )
        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        handle_service_error(exc, "LLM Service")


@app.post("/api/query")
def query_rag(request: QueryRequest):
    if not request.scheme_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Scheme ID cannot be empty.",
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        response = requests.post(
            f"{RAG_SERVICE_URL}/rag/query",
            json={
                "scheme_id": request.scheme_id,
                "question": request.question,
                "top_k": request.top_k,
            },
            timeout=240,
        )
        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        handle_service_error(exc, "RAG Service")

