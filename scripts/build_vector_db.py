from scripts.chunk_details import chunk_details
from scripts.chunk_faq import chunk_faq

from embedding_service.embeddings import (
    SentenceTransformerEmbeddings
)

from vector_store.chroma_store import (
    ChromaVectorStore
)


SCHEMES = [
    "pm_usp_csss",
    "nmmss",
    "pragati",
    "pgs_sc_st",
    "sports_free_education",
    "niti_internship"
]


def build_documents():

    all_documents = []

    for scheme_id in SCHEMES:

        print("=" * 70)
        print(f"Processing: {scheme_id}")
        print("=" * 70)

        details = chunk_details(
            scheme_id
        )

        faq = chunk_faq(
            scheme_id
        )

        print(
            f"Details chunks: "
            f"{len(details)}"
        )

        print(
            f"FAQ chunks: "
            f"{len(faq)}"
        )

        all_documents.extend(details)
        all_documents.extend(faq)

    print(
        f"\nTotal chunks: "
        f"{len(all_documents)}"
    )

    return all_documents


def create_embedding_text(document):

    scheme_id = document.metadata.get(
        "scheme_id",
        ""
    )

    section = document.metadata.get(
        "section",
        ""
    )

    scheme_name = (
        scheme_id
        .replace("_", " ")
        .upper()
    )

    return (
        f"Scheme: {scheme_name}\n"
        f"Section: {section}\n\n"
        f"{document.page_content}"
    )


def build_embeddings(documents):

    embedder = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    embedding_texts = [
        create_embedding_text(document)
        for document in documents
    ]

    print(
        "\nGenerating embeddings..."
    )

    embeddings = embedder.embed_documents(
        embedding_texts
    )

    print(
        f"Generated embeddings: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    return embeddings


def build_vector_database(
    documents,
    embeddings
):

    vector_store = ChromaVectorStore(
        persist_directory="data/chroma_db",
        collection_name="government_schemes"
    )

    vector_store.add_documents(
        documents,
        embeddings
    )

    return vector_store


def main():

    print("=" * 70)
    print("Government Scheme Vector Database Pipeline")
    print("=" * 70)

    documents = build_documents()

    embeddings = build_embeddings(
        documents
    )

    build_vector_database(
        documents,
        embeddings
    )

    print("\n" + "=" * 70)
    print("Vector database build completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
