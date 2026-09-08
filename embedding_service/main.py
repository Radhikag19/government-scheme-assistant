from pathlib import Path
import json

from scripts.chunk_details import chunk_details
from scripts.chunk_faq import chunk_faq

from embedding_service.embedder import Embedder


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT /
    "data" /
    "embeddings"
)

SCHEMES = [
    "pm_usp_csss",
    "nmmss",
    "pragati",
    "pgs_sc_st",
    "sports_free_education",
    "niti_internship",
]


# ============================================================
# Save embeddings
# ============================================================

def save_embeddings(
    scheme_id,
    documents,
    embeddings
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR /
        f"{scheme_id}.json"
    )

    data = []

    for document, embedding in zip(
        documents,
        embeddings
    ):

        item = {
            "chunk_id":
                document.metadata.get(
                    "chunk_id"
                ),

            "scheme_id":
                document.metadata.get(
                    "scheme_id"
                ),

            "scheme_name":
                document.metadata.get(
                    "scheme_name"
                ),

            "source":
                document.metadata.get(
                    "source"
                ),

            "section":
                document.metadata.get(
                    "section"
                ),

            "question_number":
                document.metadata.get(
                    "question_number"
                ),

            "page":
                document.metadata.get(
                    "page"
                ),

            "text":
                document.page_content,

            "embedding":
                embedding.tolist()
        }

        data.append(item)

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False
        )

    print(
        f"Saved {len(data)} embeddings to:"
        f"\n{output_path}"
    )


# ============================================================
# Process one scheme
# ============================================================

def process_scheme(
    scheme_id,
    embedder
):

    print("\n")
    print("=" * 70)
    print(
        f"Processing: {scheme_id}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Details
    # --------------------------------------------------------

    print("\nChunking details PDF...")

    details_documents = chunk_details(
        scheme_id
    )

    print(
        f"Details chunks: "
        f"{len(details_documents)}"
    )

    # --------------------------------------------------------
    # FAQ
    # --------------------------------------------------------

    print("\nChunking FAQ PDF...")

    faq_documents = chunk_faq(
        scheme_id
    )

    print(
        f"FAQ chunks: "
        f"{len(faq_documents)}"
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    documents = (
        details_documents +
        faq_documents
    )

    print(
        f"\nTotal chunks: "
        f"{len(documents)}"
    )

    if not documents:

        print(
            "No chunks found. Skipping."
        )

        return

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    texts = [
        document.page_content
        for document in documents
    ]

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print(
        "\nGenerating embeddings..."
    )

    embeddings = (
        embedder.embed_documents(
            texts
        )
    )

    print(
        "Embedding matrix shape:",
        embeddings.shape
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_embeddings(
        scheme_id,
        documents,
        embeddings
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("Government Scheme Embedding Pipeline")
    print("=" * 70)

    print(
        "\nEmbedding model:"
        " all-MiniLM-L6-v2"
    )

    embedder = Embedder()

    print(
        f"Embedding dimension:"
        f" {embedder.dimension}"
    )

    for scheme_id in SCHEMES:

        process_scheme(
            scheme_id,
            embedder
        )

    print("\n")
    print("=" * 70)
    print("Embedding pipeline completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
