
import json
from pathlib import Path

from app.preprocessing.text_processor import TextProcessor
from app.embeddings.embedding_model import EmbeddingModel
from app.vectorstore.chroma_store import ChromaStore
from app.retrieval.bm25_search import BM25Search


class HybridSearch:
    def __init__(self):
        self.processor = TextProcessor()
        self.embedder = EmbeddingModel()

        self.store = ChromaStore(
            persist_directory="chroma_db",
            collection_name="indian_companies"
        )

        self.bm25 = BM25Search()
        self._load_bm25_index()

    def _load_bm25_index(self):
        documents = []
        metadatas = []

        for file_path in Path("data/raw").glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as file:
                record = json.load(file)

            chunks = self.processor.split_into_chunks(
                record.get("content") or record.get("description", "")
            )

            for index, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "company": record.get("company") or record.get("company_name", "Unknown Company"),
                    "source": record.get("source", "Wikipedia"),
                    "chunk_index": index,
                    "source_file": file_path.name
                })

        self.bm25.fit(documents, metadatas)
        print(f"BM25 indexed {len(documents)} chunks")

    def search(self, query, top_k=5, candidate_k=10):
        # 1. Keyword retrieval
        keyword_results = self.bm25.search(
            query, top_k=candidate_k
        )

        # 2. Semantic retrieval
        query_embedding = self.embedder.generate_embeddings(
            [query]
        )[0]

        vector_results = self.store.search(
            query_embedding, top_k=candidate_k
        )

        # 3. Reciprocal Rank Fusion
        fused = {}

        def add_result(document, metadata, rank):
            key = document

            if key not in fused:
                fused[key] = {
                    "document": document,
                    "metadata": metadata,
                    "score": 0.0
                }

            fused[key]["score"] += 1.0 / (60 + rank)

        for rank, result in enumerate(keyword_results, start=1):
            add_result(
                result["document"],
                result["metadata"],
                rank
            )

        vector_documents = vector_results.get("documents", [[]])[0]
        vector_metadatas = vector_results.get("metadatas", [[]])[0]

        for rank, (document, metadata) in enumerate(
            zip(vector_documents, vector_metadatas),
            start=1
        ):
            add_result(document, metadata, rank)

        ranked_results = sorted(
            fused.values(),
            key=lambda item: item["score"],
            reverse=True
        )

        return ranked_results[:top_k]
