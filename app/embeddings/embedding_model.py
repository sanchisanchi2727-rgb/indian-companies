
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5", model=None):
        self.model_name = model_name

        if model is not None:
            self.model = model
        else:
            self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts):
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return embeddings


if __name__ == "__main__":
    model = EmbeddingModel()

    texts = [
        "TCS provides IT consulting and technology services.",
        "Infosys is an Indian information technology company."
    ]

    vectors = model.generate_embeddings(texts)

    print("Number of texts:", len(texts))
    print("Embedding shape:", vectors.shape)
    print("First vector dimensions:", len(vectors[0]))
    print("Embedding test passed!")

