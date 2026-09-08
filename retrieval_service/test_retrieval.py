from retrieval_service.retriever import SchemeRetriever


def main():

    retriever = SchemeRetriever()

    query = "What benefits are available to students who have won medals in national sporting events?"

    results = retriever.retrieve(query, top_k=5)

    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)
    print(query)

    print("\n" + "=" * 70)
    print("RETRIEVED CHUNKS")
    print("=" * 70)

    for i, result in enumerate(results["documents"][0], start=1):

        metadata = results["metadatas"][0][i - 1]
        distance = results["distances"][0][i - 1]

        print(f"\n--- Result {i} ---")
        print(f"Scheme: {metadata.get('scheme_id')}")
        print(f"Source: {metadata.get('source')}")
        print(f"Section: {metadata.get('section')}")
        print(f"Distance: {distance:.4f}")
        print(f"Text:\n{result}")


if __name__ == "__main__":
    main()
