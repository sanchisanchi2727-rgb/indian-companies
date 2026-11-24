
import numpy as np
from app.retrieval.hybrid_search import HybridSearch


class FakeEmbeddingModel:
    def encode(self, texts, **kwargs):
        return np.array([
            [0.1, 0.2, 0.3]
            for _ in texts
        ])


def test_hybrid_search_returns_results(monkeypatch):

    # Prevent downloading the real embedding model
    monkeypatch.setattr(
        "app.retrieval.hybrid_search.EmbeddingModel",
        lambda: type(
            "FakeEmbedder",
            (),
            {
                "generate_embeddings": lambda self, texts: np.array(
                    [[0.1, 0.2, 0.3] for _ in texts]
                )
            }
        )()
    )

    # Prevent loading local company JSON files into BM25
    monkeypatch.setattr(
        "app.retrieval.hybrid_search.HybridSearch._load_bm25_index",
        lambda self: None
    )

    searcher = HybridSearch()

    def mock_bm25_search(query, top_k=10):
        return [
            {
                "document": "Infosys provides IT consulting and digital services.",
                "metadata": {
                    "company": "Infosys",
                    "source": "test"
                },
                "score": 0.95
            }
        ]

    def mock_vector_search(query_embedding, top_k=10):
        return {
            "documents": [[
                "TCS provides IT consulting and technology services."
            ]],
            "metadatas": [[
                {"company": "TCS", "source": "test"}
            ]],
            "distances": [[0.1]]
        }

    monkeypatch.setattr(searcher.bm25, "search", mock_bm25_search)
    monkeypatch.setattr(searcher.store, "search", mock_vector_search)

    results = searcher.search(
        "What IT services do companies provide?",
        top_k=5
    )

    assert len(results) > 0
    assert len(results) <= 5

    for result in results:
        assert isinstance(result["document"], str)
        assert isinstance(result["metadata"], dict)
        assert "company" in result["metadata"]
        assert "source" in result["metadata"]


