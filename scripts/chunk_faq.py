from pathlib import Path
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# Load PDF
# ============================================================

def load_pdf(scheme_id):

    pdf_path = (
        PROJECT_ROOT
        / "knowledge_base"
        / scheme_id
        / "faq.pdf"
    )

    loader = PyPDFLoader(
        str(pdf_path),
        extraction_mode="layout"
    )

    documents = loader.load()

    print(
        f"Loaded {len(documents)} pages "
        f"for {scheme_id}."
    )

    return documents


# ============================================================
# Combine pages
# ============================================================

def combine_pages(documents):

    return "\n".join(
        document.page_content
        for document in documents
    )


# ============================================================
# Detect FAQ question number
# ============================================================

def detect_question_number(line):

    question_pattern = re.compile(
        r"^\s*(?:Q\s*)?(\d+)\s*[\.\):\-]\s+",
        flags=re.IGNORECASE
    )

    match = question_pattern.match(
        line
    )

    if match:

        return int(
            match.group(1)
        )

    return None


# ============================================================
# Split FAQ
# ============================================================

def split_faq(text):

    faq_chunks = []

    current_question_number = None
    current_content = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        question_number = (
            detect_question_number(line)
        )

        # ----------------------------------------------------
        # New question
        # ----------------------------------------------------

        if question_number is not None:

            # Save previous question
            if current_question_number is not None:

                faq_chunks.append({
                    "question_number":
                        current_question_number,

                    "text":
                        "\n".join(
                            current_content
                        ).strip()
                })

            current_question_number = (
                question_number
            )

            current_content = [
                line
            ]

        # ----------------------------------------------------
        # Answer / continuation
        # ----------------------------------------------------

        else:

            if current_question_number is not None:

                current_content.append(
                    line
                )

    # --------------------------------------------------------
    # Save final question
    # --------------------------------------------------------

    if current_question_number is not None:

        faq_chunks.append({
            "question_number":
                current_question_number,

            "text":
                "\n".join(
                    current_content
                ).strip()
        })

    return faq_chunks


# ============================================================
# Convert to LangChain Documents
# ============================================================

def create_documents(
    faq_chunks,
    scheme_id
):

    documents = []

    for item in faq_chunks:

        question_number = (
            item["question_number"]
        )

        document = Document(
            page_content=item["text"],
            metadata={
                "scheme_id": scheme_id,
                "source": "faq",
                "section": "FAQ",
                "question_number":
                    question_number,
                "chunk_id": (
                    f"{scheme_id}_faq_"
                    f"q{question_number}"
                )
            }
        )

        documents.append(
            document
        )

    return documents


# ============================================================
# Main reusable function
# ============================================================

def chunk_faq(scheme_id):

    pdf_path = (
        PROJECT_ROOT
        / "knowledge_base"
        / scheme_id
        / "faq.pdf"
    )

    if not pdf_path.exists():

        print(
            f"PDF not found: {pdf_path}"
        )

        return []

    documents = load_pdf(
        scheme_id
    )

    full_text = combine_pages(
        documents
    )

    faq_chunks = split_faq(
        full_text
    )

    print(
        f"Detected {len(faq_chunks)} FAQ questions "
        f"for {scheme_id}."
    )

    faq_documents = create_documents(
        faq_chunks,
        scheme_id
    )

    return faq_documents


# ============================================================
# Optional standalone execution
# ============================================================

if __name__ == "__main__":

    scheme_id = "pragati"

    documents = chunk_faq(
        scheme_id
    )

    for document in documents:

        print("=" * 70)
        print(
            document.metadata
        )
        print(
            document.page_content
        )
        
        
        
        
        
        
        
        
        
