
import re


class TextProcessor:
    def __init__(self, chunk_size=500, overlap=75):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text):
        # Remove Wikipedia section headings.
        text = re.sub(r"==+.*?==+", " ", text)

        # Replace repeated whitespace with a single space.
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def split_into_chunks(self, text):
        text = self.clean_text(text)
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(text):
                break

            start = end - self.overlap

        return chunks
