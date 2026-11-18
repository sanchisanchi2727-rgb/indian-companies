
from app.embeddings.embedding_model import EmbeddingModel
from app.vectorstore.chroma_store import ChromaStore


def test_chroma_store_add_and_search(tmp_path):

    # Initialize embedding model
    embedder = EmbeddingModel()

    # Use a temporary database for testing
    store = ChromaStore(
        persist_directory=str(tmp_path / "chroma_test"),
        collection_name="test_companies"
    )

    # Sample company documents
    chunks = [
        "TCS provides IT consulting and technology services.",
        "Infosys provides digital services and business consulting.",
        "HDFC Bank provides banking and financial services."
    ]

    # Company metadata
    metadatas = [
        {"company": "TCS", "source": "test"},
        {"company": "Infosys", "source": "test"},
        {"company": "HDFC Bank", "source": "test"}
    ]

    ids = ["test_tcs", "test_infosys", "test_hdfc"]

    # Generate embeddings
    embeddings = embedder.generate_embeddings(chunks)

    # Store documents in ChromaDB
    store.add_documents(
        chunks=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    # Verify document count
    assert store.count_documents() == 3

    # Generate query embedding
    query = "Which company provides IT consulting?"
    query_embedding = embedder.generate_embeddings([query])[0]

    # Perform similarity search
    results = store.search(
        query_embedding,
        top_k=2
    )

    # Verify search results
    assert results is not None
    assert len(results["documents"][0]) > 0
    assert len(results["documents"][0]) <= 2
    assert len(results["metadatas"][0]) > 0

    # Verify metadata
    companies = [
        metadata["company"]
        for metadata in results["metadatas"][0]
    ]

    assert all(
        company in ["TCS", "Infosys", "HDFC Bank"]
        for company in companies
    )

