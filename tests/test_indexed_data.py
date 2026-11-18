
from app.vectorstore.chroma_store import ChromaStore


def test_company_data_is_indexed():

    # Connect to the existing Indian Companies database
    store = ChromaStore(
        persist_directory="chroma_db",
        collection_name="indian_companies"
    )

    # Get the total number of indexed documents
    count = store.count_documents()

    # Verify that company data exists
    assert count > 0, (
        "No company data found in ChromaDB. "
        "Please run the indexing process first."
    )

    # Verify the document count
    assert isinstance(count, int)
