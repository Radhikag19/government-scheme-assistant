from pathlib import Path
import chromadb


class ChromaVectorStore:

    def __init__(
        self,
        persist_directory="data/chroma_db",
        collection_name="government_schemes"
    ):
        self.persist_directory = Path(persist_directory)

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": "Government scheme knowledge base",
                "hnsw:space": "cosine"
            }
        )

        print(
            f"Chroma collection: {collection_name}"
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
            f"Upserted {len(documents)} "
            f"documents to Chroma."
        )

    def similarity_search(
        self,
        query_embedding,
        top_k=5,
        filter=None
    ):
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": [
                "documents",
                "metadatas",
                "distances"
            ]
        }

        if filter:
            query_kwargs["where"] = filter

        results = self.collection.query(
            **query_kwargs
        )

        return results
