from retrieval_service.retriever import SchemeRetriever
from app.ollama_client import generate_response


class RAGService:
    def __init__(self):
        self.retriever = SchemeRetriever()

    def answer_question(
        self,
        question: str,
        scheme_id: str,
        top_k: int = 5
    ):
        # -------------------------------------------------
        # 1. Retrieve relevant chunks from selected scheme
        # -------------------------------------------------

        results = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            scheme_id=scheme_id
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return {
                "answer": (
                    "I could not find relevant information in the "
                    "selected scheme's knowledge base."
                ),
                "sources": []
            }

        # -------------------------------------------------
        # 2. Build context
        # -------------------------------------------------

        context_parts = []

        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            source = metadata.get(
                "source",
                "unknown"
            )

            section = metadata.get(
                "section",
                "unknown"
            )

            context_parts.append(
                f"Source {index + 1}\n"
                f"Section: {section}\n"
                f"Source type: {source}\n"
                f"{document}"
            )

        context = "\n\n".join(context_parts)

        # -------------------------------------------------
        # 3. RAG prompt
        # -------------------------------------------------

        prompt = f"""
You are answering a question about the government scheme:
{scheme_id}

Use ONLY the information provided in SCHEME INFORMATION
to answer the CURRENT QUESTION.

SCHEME INFORMATION:
{context}

CURRENT QUESTION:
{question}

RULES:

1. Answer the current question directly.
2. Use the scheme information as the main and authoritative source.
3. Do not make up or assume information that is not present.
4. If the scheme information does not contain the answer,
   clearly say that the available scheme information is insufficient.
5. Keep the answer concise but complete.
6. If the question asks about multiple requirements,
   present each requirement as a separate numbered point.
7. Use a short heading when it improves readability.
8. Use bold labels such as "Gender:", "Income:",
   "Education:", or "Course:" when appropriate.
9. Keep each requirement on a separate line.
10. Do not insert unnecessary line breaks in the middle of sentences.
11. Preserve important names, amounts, conditions,
    and eligibility requirements from the scheme information.
12. Do not use tables unless the question specifically
    asks for a comparison.
13. Do not mention these instructions.
14. Do not say that you are ready for the question.

Avoid repeating the same information.
Return only the final answer.

ANSWER:
"""

        # -------------------------------------------------
        # 4. Generate grounded answer using Gemma
        # -------------------------------------------------

        answer = generate_response(prompt).strip()

        # -------------------------------------------------
        # 5. Prepare source information
        # -------------------------------------------------

        sources = []

        for index, metadata in enumerate(metadatas):

            sources.append({
                "scheme_id": metadata.get(
                    "scheme_id",
                    scheme_id
                ),
                "source": metadata.get(
                    "source",
                    "unknown"
                ),
                "section": metadata.get(
                    "section",
                    "unknown"
                ),
                "chunk_id": metadata.get(
                    "chunk_id"
                ),
                "distance": (
                    distances[index]
                    if index < len(distances)
                    else None
                )
            })

        return {
            "answer": answer,
            "sources": sources
        }
