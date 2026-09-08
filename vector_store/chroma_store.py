from pathlib import Path

import chromadb


class ChromaVectorStore:

    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        collection_name: str = "government_schemes"
    ):

        self.persist_directory = Path(
            persist_directory
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description":
                        "Government scheme knowledge base",

                    # Use cosine distance for semantic retrieval.
                    "hnsw:space": "cosine"
                }
            )
        )

        print(
            f"Chroma collection: "
            f"{collection_name}"
        )

        print(
            f"Existing documents: "
            f"{self.collection.count()}"
        )

    def add_documents(
        self,
        documents,
        embeddings
    ):

        ids = []
        texts = []
        metadatas = []

        for index, document in enumerate(documents):

            metadata = dict(
                document.metadata
            )

            # Chroma metadata values must be simple types.
            metadata = {
                key: value
                for key, value in metadata.items()
                if isinstance(
                    value,
                    (str, int, float, bool)
                )
            }

            chunk_id = metadata.get(
                "chunk_id",
                f"chunk_{index}"
            )

            ids.append(chunk_id)

            # Store the ORIGINAL chunk text.
            # This is intentionally different from
            # the enriched text used to create embeddings.
            texts.append(
                document.page_content
            )

            metadatas.append(metadata)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(
            f"Upserted {len(documents)} documents "
            f"to Chroma."
        )

    def similarity_search(
        self,
        query_embedding,
        top_k=5
    ):

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        return results
