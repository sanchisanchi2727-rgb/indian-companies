

from app.retrieval.bm25_search import BM25Search


def test_bm25_search_returns_results():
    # Sample company documents
    documents = [
        "TCS provides IT consulting and technology services.",
        "Infosys provides software consulting and digital services.",
        "HDFC Bank offers banking and financial services."
    ]

    # Company metadata
    metadatas = [
        {"company": "TCS"},
        {"company": "Infosys"},
        {"company": "HDFC Bank"}
    ]

    # Initialize BM25 search
    searcher = BM25Search()

    # Build the search index
    searcher.fit(documents, metadatas)

    # Search for relevant companies
    results = searcher.search(
        "IT consulting services",
        top_k=2
    )

    # Verify search results
    assert results is not None
    assert len(results) > 0
    assert len(results) <= 2

    # Verify result structure
    for result in results:
        assert "document" in result
        assert "metadata" in result
        assert "score" in result

    # Verify returned company information
    companies = [
        result["metadata"]["company"]
        for result in results
    ]

    assert all(company in ["TCS", "Infosys", "HDFC Bank"]
               for company in companies)
