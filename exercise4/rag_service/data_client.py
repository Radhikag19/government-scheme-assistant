import os

import requests


DATA_SERVICE_URL = os.getenv(
    "DATA_SERVICE_URL",
    "http://127.0.0.1:9003",
)


def get_scheme(scheme_id: str):
    response = requests.get(
        f"{DATA_SERVICE_URL}/data/schemes/{scheme_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def search_knowledge(
    query: str,
    scheme_id: str,
    top_k: int = 5,
):
    response = requests.post(
        f"{DATA_SERVICE_URL}/data/search",
        json={
            "query": query,
            "scheme_id": scheme_id,
            "top_k": top_k,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
