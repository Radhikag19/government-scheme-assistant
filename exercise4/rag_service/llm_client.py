import os

import requests


LLM_SERVICE_URL = os.getenv(
    "LLM_SERVICE_URL",
    "http://127.0.0.1:9004",
)


def generate_response(prompt: str):
    response = requests.post(
        f"{LLM_SERVICE_URL}/llm/generate",
        json={
            "prompt": prompt,
        },
        timeout=180,
    )

    response.raise_for_status()

    return response.json()["response"]
