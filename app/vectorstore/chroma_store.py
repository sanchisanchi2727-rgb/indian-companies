
import chromadb
from pathlib import Path


class ChromaStore:
    def __init__(
        self,
        persist_directory="chroma_db",
        collection_name="indian_companies"
    ):
        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks, embeddings, metadatas, ids):
        if not (
            len(chunks) == len(embeddings)
            == len(metadatas) == len(ids)
        ):
            raise ValueError("All input lists must have equal length")

        if not chunks:
            return

        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        print(f"Stored {len(chunks)} chunks in ChromaDB")

    def search(self, query_embedding, top_k=3):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        return results

    def count_documents(self):
        return self.collection.count()
