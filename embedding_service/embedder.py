from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:

    def __init__(self):

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Embedding model loaded successfully."
        )

    def embed_documents(self, texts):

        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )

    def embed_query(self, text):

        return self.model.encode(
            text,
            convert_to_numpy=True
        )

    @property
    def dimension(self):

        return (
            self.model
            .get_sentence_embedding_dimension()
        )
