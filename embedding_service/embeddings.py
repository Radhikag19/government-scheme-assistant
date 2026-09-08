import torch
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings:

    def __init__(
        self,
        model_name="all-MiniLM-L6-v2"
    ):

        self.model_name = model_name

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model = SentenceTransformer(
            model_name,
            device=self.device
        )

        print(
            f"Embedding device: {self.device}"
        )

    def embed_documents(self, texts):

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    def embed_query(self, text):

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def get_embedding_dimension(self):

        return (
            self.model
            .get_embedding_dimension()
        )
