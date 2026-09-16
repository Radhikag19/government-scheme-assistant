from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

from exercise4.rag_service.data_client import (
    get_scheme,
    search_knowledge,
)
from exercise4.rag_service.llm_client import generate_response


app = FastAPI(
    title="Government Scheme RAG Service",
    description="Retrieves scheme-specific knowledge and generates grounded answers.",
    version="1.0.0",
)


class RAGRequest(BaseModel):
    scheme_id: str
    question: str
    top_k: int = 5


def build_prompt(
    question: str,
    documents: list[str],
    scheme_name: str,
) -> str:
    context_parts = []

    for index, document in enumerate(documents, start=1):
        context_parts.append(
            f"--- Retrieved Source {index} ---\n{document}"
        )

    context = "\n\n".join(context_parts)

    return f"""
You are a helpful assistant answering questions about the government scheme
"{scheme_name}".

Answer the user's question using ONLY the retrieved information below.

Do not use outside knowledge.
Do not invent or assume information that is not present in the retrieved sources.

If the retrieved information does not contain enough information to answer
the question, clearly say that the available scheme information does not
provide the answer.

Keep the answer concise and easy to understand.

When there are multiple requirements or points, use a numbered list or
bullet points where appropriate.

Preserve important facts, amounts, durations, eligibility conditions,
and restrictions exactly as supported by the retrieved information.

Do not create tables unless a comparison is genuinely necessary.

Avoid repeating the same information.

Retrieved information:

{context}

User question:

{question}

Return only the final answer.
""".strip()


@app.get("/")
def root():
    return {
        "service": "rag-service",
        "status": "running",
    }


@app.post("/rag/query")
def query_rag(request: RAGRequest):
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
        # Step 1: Validate the scheme through Data Service.
        scheme = get_scheme(request.scheme_id)

        canonical_scheme_id = scheme["scheme_id"]
        scheme_name = scheme.get("scheme_name", canonical_scheme_id)

        # Step 2: Retrieve relevant knowledge through Data Service.
        retrieval = search_knowledge(
            query=request.question,
            scheme_id=canonical_scheme_id,
            top_k=request.top_k,
        )

        documents = retrieval.get("documents", [])
        metadatas = retrieval.get("metadatas", [])
        distances = retrieval.get("distances", [])

        if documents and isinstance(documents[0], list):
            documents = documents[0]

        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        if distances and isinstance(distances[0], list):
            distances = distances[0]

        if not documents:
            return {
                "scheme_id": canonical_scheme_id,
                "question": request.question,
                "answer": (
                    "I could not find relevant information in the "
                    "available knowledge base for this question."
                ),
                "sources": [],
            }

        # Step 3: Build a grounded prompt.
        prompt = build_prompt(
            question=request.question,
            documents=documents,
            scheme_name=scheme_name,
        )

        # Step 4: Send the prompt through the LLM Service.
        answer = generate_response(prompt)

        # Step 5: Return answer and source information.
        sources = []

        for index, metadata in enumerate(metadatas):
            source = dict(metadata or {})

            if index < len(distances):
                source["distance"] = distances[index]

            sources.append(source)

        return {
            "scheme_id": canonical_scheme_id,
            "question": request.question,
            "answer": answer,
            "sources": sources,
        }

    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else 502

        if status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Scheme '{request.scheme_id}' was not found.",
            )

        raise HTTPException(
            status_code=502,
            detail=f"Dependent service returned an error: {str(exc)}",
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Dependent service is unavailable: {str(exc)}",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {str(exc)}",
        )
