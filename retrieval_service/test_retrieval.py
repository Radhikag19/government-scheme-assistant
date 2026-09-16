from retrieval_service.retriever import SchemeRetriever


def print_results(title, results):

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for index, document in enumerate(documents):

        metadata = metadatas[index]
        distance = distances[index]

        print(f"\nResult {index + 1}")
        print("-" * 80)

        print(
            f"Scheme   : "
            f"{metadata.get('scheme_id')}"
        )

        print(
            f"Source   : "
            f"{metadata.get('source')}"
        )

        print(
            f"Section  : "
            f"{metadata.get('section')}"
        )

        print(
            f"Distance : "
            f"{distance}"
        )

        print("\nText:")
        print(document[:1000])


retriever = SchemeRetriever()


# --------------------------------------------------
# TEST 1
# Search across ALL schemes
# --------------------------------------------------

query = (
    "What benefits are available to students "
    "who have won medals in national sporting events?"
)

results = retriever.retrieve(
    query=query,
    top_k=5
)

print_results(
    "ALL-SCHEME RETRIEVAL",
    results
)


# --------------------------------------------------
# TEST 2
# Search only PRAGATI
# --------------------------------------------------

query = (
    "What are the eligibility requirements?"
)

results = retriever.retrieve(
    query=query,
    top_k=5,
    scheme_id="pragati"
)

print_results(
    "PRAGATI-ONLY RETRIEVAL",
    results
)
