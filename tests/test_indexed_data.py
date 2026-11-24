
from app.vectorstore.chroma_store import ChromaStore


def test_company_data_is_indexed(tmp_path):

    # Create a separate temporary ChromaDB for testing
    store = ChromaStore(
        persist_directory=str(tmp_path / "chroma_test"),
        collection_name="test_companies"
    )

    # Add sample company data
    chunks = [
        "Infosys provides IT consulting and digital services.",
        "TCS provides technology and business consulting services."
    ]

    metadatas = [
        {"company": "Infosys", "source": "test"},
        {"company": "TCS", "source": "test"}
    ]

    ids = ["test_infosys", "test_tcs"]

    # Use simple test embeddings
    import numpy as np

    embeddings = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ])

    store.add_documents(
        chunks=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    # Verify indexed documents
    count = store.count_documents()

    assert count == 2
    assert isinstance(count, int)

