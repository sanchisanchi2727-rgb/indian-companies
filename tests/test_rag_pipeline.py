
from app.rag.rag_pipeline import RAGPipeline


def test_rag_pipeline_generates_answer(monkeypatch):

    # Create a RAG pipeline
    rag = RAGPipeline()

    # Mock hybrid search with sample company information
    def mock_search(query, top_k=5):
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

    # Mock Ollama so no real LLM is required
    def mock_generate_answer(question, context):
        return "Infosys provides IT consulting and digital services."

    monkeypatch.setattr(rag.searcher, "search", mock_search)
    monkeypatch.setattr(rag.llm, "generate_answer", mock_generate_answer)

    # Ask a question
    result = rag.ask("What services does Infosys provide?")

    # Verify the answer
    assert result is not None
    assert isinstance(result, dict)
    assert "answer" in result
    assert result["answer"].strip() != ""

    # Verify sources
    assert "sources" in result
    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0

    assert result["sources"][0]["company"] == "Infosys"
