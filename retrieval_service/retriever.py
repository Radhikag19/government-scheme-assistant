from embedding_service.embeddings import SentenceTransformerEmbeddings
from vector_store.chroma_store import ChromaVectorStore


class SchemeRetriever:

    def __init__(self):
        self.embedder = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        self.vector_store = ChromaVectorStore(
            persist_directory="data/chroma_db",
            collection_name="government_schemes"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        scheme_id: str = None
    ):
        query_embedding = self.embedder.embed_query(query)

        filter_condition = None

        if scheme_id:
            # Chroma was indexed with lowercase scheme IDs.
            # Normalize the incoming scheme ID before filtering.
            filter_condition = {
                "scheme_id": scheme_id.lower()
            }

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter_condition
        )

        return results
