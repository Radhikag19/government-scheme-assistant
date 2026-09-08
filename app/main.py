from fastapi import FastAPI
from pydantic import BaseModel

from app.ollama_client import generate_response


app = FastAPI(
    title="Government Scheme Eligibility Assistant",
    description="Exercise 1. Application communicating with Gemma through Ollama.",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "Government Scheme Eligibility Assistant is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    answer = generate_response(request.question)

    return {
        "question": request.question,
        "answer": answer
    }   
