from pathlib import Path
import json
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


# ============================================================
# Section headings
# ============================================================

SECTION_HEADINGS = [
    "Details:",
    "Benefits:",
    "Eligibility:",
    "Renewal Applications:",
    "Exclusions:",
    "Application Process:",
    "Payment Status:",
    "Documents Required:",
]


# ============================================================
# Load PDF
# ============================================================

def load_pdf(scheme_id):

    pdf_path = (
        PROJECT_ROOT
        / "knowledge_base"
        / scheme_id
        / "details.pdf"
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
# Split document into sections
# ============================================================

def split_into_sections(text):

    pattern = r"(?=(" + "|".join(
        re.escape(section)
        for section in SECTION_HEADINGS
    ) + r"))"

    parts = re.split(
        pattern,
        text
    )

    sections = []

    current_section = "General"

    for part in parts:

        part = part.strip()

        if not part:
            continue

        matched_heading = None

        for heading in SECTION_HEADINGS:

            if part.startswith(heading):

                matched_heading = heading
                break

        if matched_heading:

            current_section = (
                matched_heading
                .rstrip(":")
                .strip()
            )

            content = part[
                len(matched_heading):
            ].strip()

        else:

            content = part

        if content:

            sections.append({
                "section": current_section,
                "text": content
            })

    return sections


# ============================================================
# Create chunks inside each section
# ============================================================

def create_chunks(
    sections,
    scheme_id
):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    final_documents = []

    chunk_counter = 1

    for section in sections:

        section_name = section["section"]

        chunks = splitter.split_text(
            section["text"]
        )

        for chunk in chunks:

            document = Document(
                page_content=chunk,
                metadata={
                    "scheme_id": scheme_id,
                    "source": "details",
                    "section": section_name,
                    "chunk_id": (
                        f"{scheme_id}_details_"
                        f"{chunk_counter}"
                    ),
                }
            )

            final_documents.append(
                document
            )

            chunk_counter += 1

    return final_documents


# ============================================================
# Main reusable function
# ============================================================

def chunk_details(scheme_id):

    pdf_path = (
        PROJECT_ROOT
        / "knowledge_base"
        / scheme_id
        / "details.pdf"
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

    sections = split_into_sections(
        full_text
    )

    print(
        f"Detected {len(sections)} sections "
        f"for {scheme_id}."
    )

    chunks = create_chunks(
        sections,
        scheme_id
    )

    print(
        f"Created {len(chunks)} details chunks "
        f"for {scheme_id}."
    )

    return chunks


# ============================================================
# Optional standalone execution
# ============================================================

if __name__ == "__main__":

    scheme_id = "pragati"

    chunks = chunk_details(
        scheme_id
    )

    for document in chunks:

        print("=" * 70)
        print(
            document.metadata
        )
        print(
            document.page_content
        )
