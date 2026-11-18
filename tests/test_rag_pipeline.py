
from app.rag.rag_pipeline import RAGPipeline


def test_rag_pipeline_generates_answer():

    # Initialize RAG pipeline
    rag = RAGPipeline()

    # Ask a question about a company
    question = "What services does Infosys provide?"

    # Generate an answer using RAG
    result = rag.ask(question)

    # Verify the result structure
    assert result is not None
    assert isinstance(result, dict)

    # Verify that an answer is generated
    assert "answer" in result
    assert isinstance(result["answer"], str)
    assert result["answer"].strip() != ""

    # Verify that sources are returned
    assert "sources" in result
    assert isinstance(result["sources"], list)

    # Verify source information if available
    for source in result["sources"]:
        assert "company" in source
        assert "source" in source
        assert "text" in source
