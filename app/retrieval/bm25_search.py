
import re
from rank_bm25 import BM25Okapi


class BM25Search:
    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.bm25 = None

    def tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def fit(self, documents, metadatas):
        if len(documents) != len(metadatas):
            raise ValueError(
                "Documents and metadata must have equal lengths"
            )

        self.documents = documents
        self.metadatas = metadatas

        tokenized_documents = [
            self.tokenize(document)
            for document in documents
        ]

        self.bm25 = (
            BM25Okapi(tokenized_documents)
            if tokenized_documents
            else None
        )

    def search(self, query, top_k=3):
        if self.bm25 is None:
            return []

        scores = self.bm25.get_scores(self.tokenize(query))

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:
            results.append({
                "document": self.documents[index],
                "metadata": self.metadatas[index],
                "score": float(scores[index])
            })

        return results
