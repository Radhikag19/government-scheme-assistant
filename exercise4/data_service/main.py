from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from exercise4.data_service.scheme_repository import (
    SchemeRepository
)

from exercise4.data_service.vector_repository import (
    VectorRepository
)


app = FastAPI(
    title="Government Scheme Data Service",
    description=(
        "Provides government scheme metadata "
        "and vector knowledge retrieval."
    ),
    version="1.0.0"
)


# =========================================================
# Request models
# =========================================================

class SearchRequest(BaseModel):

    query: str

    scheme_id: str | None = None

    top_k: int = 5


# =========================================================
# Repositories
# =========================================================

scheme_repository = SchemeRepository()

vector_repository = VectorRepository()


# =========================================================
# Root
# =========================================================

@app.get("/")
def root():

    return {
        "service": "data-service",
        "status": "running"
    }


# =========================================================
# Get all schemes
# =========================================================

@app.get("/data/schemes")
def get_schemes():

    schemes = scheme_repository.get_all_schemes()

    return {
        "count": len(schemes),
        "schemes": schemes
    }


# =========================================================
# Get one scheme
# =========================================================

@app.get("/data/schemes/{scheme_id}")
def get_scheme(
    scheme_id: str
):

    scheme = scheme_repository.get_scheme(
        scheme_id
    )

    if scheme is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Scheme '{scheme_id}' "
                "was not found."
            )
        )

    return scheme


# =========================================================
# Vector search
# =========================================================

@app.post("/data/search")
def search_knowledge(
    request: SearchRequest
):

    results = vector_repository.search(
        query=request.query,
        top_k=request.top_k,
        scheme_id=request.scheme_id
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    return {
        "query": request.query,
        "scheme_id": request.scheme_id,
        "count": len(documents),
        "documents": documents,
        "metadatas": metadatas,
        "distances": distances
    }

