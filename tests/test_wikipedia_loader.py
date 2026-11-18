
from app.ingestion.wikipedia_loader import WikipediaLoader


def test_wikipedia_loader_loads_company_data():

    # Initialize Wikipedia loader
    loader = WikipediaLoader()

    # Company to retrieve
    company = "Tata Consultancy Services"

    # Load company information
    content = loader.load_company(company)

    # Verify that content is returned
    assert content is not None
    assert isinstance(content, str)
    assert len(content.strip()) > 0

    # Verify that meaningful company information exists
    assert len(content) > 50
