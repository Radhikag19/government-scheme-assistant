from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from exercise4.llm_service.ollama_client import generate_response


app = FastAPI(
    title="Government Scheme LLM Service",
    description="Provides LLM generation through Ollama and Gemma.",
    version="1.0.0",
)


class GenerateRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {
        "service": "llm-service",
        "status": "running",
    }


@app.post("/llm/generate")
def generate(request: GenerateRequest):
    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    try:
        response = generate_response(request.prompt)

        return {
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM generation failed: {str(exc)}",
        )
