
from app.retrieval.hybrid_search import HybridSearch


def test_hybrid_search_returns_results():
    # Initialize Hybrid Search
    searcher = HybridSearch()

    # Search query
    query = "What IT services does Infosys provide?"

    # Perform hybrid search
    results = searcher.search(query, top_k=5)

    # Verify that results are returned
    assert results is not None
    assert len(results) > 0
    assert len(results) <= 5

    # Verify the structure of each result
    for result in results:
        assert "document" in result
        assert "metadata" in result
        assert "score" in result

        assert isinstance(result["document"], str)
        assert isinstance(result["metadata"], dict)

        assert "company" in result["metadata"]
        assert "source" in result["metadata"]
