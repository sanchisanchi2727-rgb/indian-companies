

from app.ingestion.wikipedia_loader import WikipediaLoader


def test_wikipedia_loader_loads_company_data(monkeypatch):

    loader = WikipediaLoader()

    # Sample company information
    sample_content = (
        "Tata Consultancy Services is an Indian multinational "
        "IT services and consulting company. It provides "
        "technology services, consulting and business solutions."
    )

    # Mock the Wikipedia request
    monkeypatch.setattr(
        loader,
        "load_company",
        lambda company: sample_content
    )

    content = loader.load_company("Tata Consultancy Services")

    assert content is not None
    assert isinstance(content, str)
    assert len(content.strip()) > 0
    assert len(content) > 50
