from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.ollama_client import generate_response
from app.rag_service import RAGService
from app.session_manager import SessionManager

from eligibility.profile import UserProfile
from eligibility.matcher import EligibilityMatcher


app = FastAPI(
    title="Government Scheme Eligibility Assistant",
    description=(
        "Government scheme discovery, eligibility matching "
        "and RAG-based question answering."
    ),
    version="2.1.0"
)


# =========================================================
# Request models
# =========================================================

class QuestionRequest(BaseModel):
    question: str


class SchemeMatchRequest(BaseModel):
    profile: UserProfile


class ChatRequest(BaseModel):
    scheme_id: str
    question: str
    top_k: int = 5


class SessionRequest(BaseModel):
    scheme_id: str | None = None


# =========================================================
# Application services
# =========================================================

session_manager = SessionManager()


# =========================================================
# Root
# =========================================================

@app.get("/")
def root():

    return {
        "message":
            "Government Scheme Eligibility Assistant is running"
    }


# =========================================================
# Existing /ask endpoint
# =========================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    answer = generate_response(
        request.question
    )

    return {
        "question": request.question,
        "answer": answer
    }


# =========================================================
# Scheme listing
# =========================================================

@app.get("/schemes")
def get_schemes():

    matcher = EligibilityMatcher()

    schemes = []

    for scheme in matcher.schemes:

        schemes.append({
            "scheme_id": scheme.get(
                "scheme_id"
            ),
            "scheme_name": scheme.get(
                "scheme_name"
            ),
            "authority": scheme.get(
                "authority"
            ),
            "scheme_type": scheme.get(
                "scheme_type"
            ),
            "benefit": scheme.get(
                "benefit"
            )
        })

    return {
        "count": len(schemes),
        "schemes": schemes
    }


# =========================================================
# Profile options
# =========================================================

@app.get("/profile/options")
def get_profile_options():

    matcher = EligibilityMatcher()

    education_levels = set()
    course_types = set()
    genders = set()
    categories = set()
    institution_types = set()

    for scheme in matcher.schemes:

        eligibility = scheme.get(
            "eligibility",
            {}
        )

        def add_values(
            target,
            value
        ):

            if value is None:
                return

            if isinstance(
                value,
                list
            ):

                for item in value:

                    if item:
                        target.add(
                            str(item)
                        )

            else:

                if value:
                    target.add(
                        str(value)
                    )

        add_values(
            education_levels,
            eligibility.get(
                "education_level"
            )
        )

        add_values(
            course_types,
            eligibility.get(
                "course_type"
            )
        )

        add_values(
            genders,
            eligibility.get(
                "gender"
            )
        )

        add_values(
            categories,
            eligibility.get(
                "category"
            )
        )

        add_values(
            institution_types,
            eligibility.get(
                "institution_type"
            )
        )

    return {
        "education_level": sorted(
            education_levels
        ),
        "course_type": sorted(
            course_types
        ),
        "gender": sorted(
            genders
        ),
        "category": sorted(
            categories
        ),
        "institution_type": sorted(
            institution_types
        )
    }


# =========================================================
# Eligibility matching
# =========================================================

@app.post("/schemes/match")
def match_schemes(
    request: SchemeMatchRequest
):

    matcher = EligibilityMatcher()

    results = matcher.match_all(
        request.profile
    )

    return {
        "profile": request.profile.model_dump(),
        "results": results
    }


# =========================================================
# Create chat session
# =========================================================

@app.post("/sessions")
def create_session(
    request: SessionRequest
):

    session_id = session_manager.create_session(
        scheme_id=request.scheme_id
    )

    return {
        "session_id": session_id,
        "scheme_id": request.scheme_id,
        "history": []
    }


# =========================================================
# Get session
# =========================================================

@app.get("/sessions/{session_id}")
def get_session(
    session_id: str
):

    session = session_manager.get_session(
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "session_id": session_id,
        "scheme_id": session["scheme_id"],
        "history": session["history"]
    }


# =========================================================
# Clear session
# =========================================================

@app.delete("/sessions/{session_id}")
def clear_session(
    session_id: str
):

    success = session_manager.clear_session(
        session_id
    )

    if not success:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "session_id": session_id,
        "message": "Conversation cleared."
    }


# =========================================================
# RAG Chat
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    matcher = EligibilityMatcher()

    matching_scheme = None

    # Find the requested scheme
    for scheme in matcher.schemes:

        stored_id = scheme.get(
            "scheme_id",
            ""
        )

        if stored_id.lower() == request.scheme_id.lower():
            matching_scheme = scheme
            break

    if matching_scheme is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Scheme '{request.scheme_id}' "
                "was not found."
            )
        )

    canonical_scheme_id = matching_scheme[
        "scheme_id"
    ]

    # ---------------------------------------------
    # Stateless RAG
    # ---------------------------------------------

    rag_service = RAGService()

    result = rag_service.answer_question(
        question=request.question,
        scheme_id=canonical_scheme_id,
        top_k=request.top_k
    )

    return {
        "scheme_id": canonical_scheme_id,
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }
