
from app.preprocessing.text_processor import TextProcessor


def test_text_processor_splits_into_chunks():

    # Initialize text processor
    processor = TextProcessor(
        chunk_size=500,
        overlap=75
    )

    # Sample company text
    sample_text = (
        "Tata Consultancy Services is an Indian IT company. " * 100
    )

    # Split text into chunks
    chunks = processor.split_into_chunks(sample_text)

    # Verify chunks are generated
    assert chunks is not None
    assert len(chunks) > 1

    # Verify every chunk contains text
    assert all(
        isinstance(chunk, str) and chunk.strip()
        for chunk in chunks
    )

    # Verify chunk size
    assert all(
        len(chunk) <= 500
        for chunk in chunks
    )
