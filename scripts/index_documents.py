
import json
from pathlib import Path

from app.preprocessing.text_processor import TextProcessor
from app.embeddings.embedding_model import EmbeddingModel
from app.vectorstore.chroma_store import ChromaStore


class CompanyIndexer:
    def __init__(self):
        self.data_dir = Path("data/raw")
        self.processor = TextProcessor(
            chunk_size=500,
            overlap=75
        )
        self.embedder = EmbeddingModel()
        self.store = ChromaStore(
            persist_directory="chroma_db",
            collection_name="indian_companies"
        )

    def index_all(self):
        files = list(self.data_dir.glob("*.json"))

        if not files:
            print("No JSON files found in data/raw.")
            return

        total_chunks = 0

        for file_path in files:
            print(f"\nProcessing: {file_path.name}")

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    record = json.load(file)

                company = record["company"]
                content = record["content"]
                source = record.get("source", "Wikipedia")

                chunks = self.processor.split_into_chunks(content)

                if not chunks:
                    print(f"No text chunks found for {company}")
                    continue

                embeddings = self.embedder.generate_embeddings(chunks)

                ids = [
                    f"{file_path.stem}_{i}"
                    for i in range(len(chunks))
                ]

                metadatas = [
                    {
                        "company": company,
                        "source": source,
                        "chunk_index": i,
                        "source_file": file_path.name
                    }
                    for i in range(len(chunks))
                ]

                self.store.add_documents(
                    chunks=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )

                total_chunks += len(chunks)
                print(f"Indexed {len(chunks)} chunks for {company}")

            except Exception as error:
                print(f"Failed to index {file_path.name}: {error}")

        print(f"\nTotal chunks processed: {total_chunks}")
        print("Indexing complete!")


if __name__ == "__main__":
    indexer = CompanyIndexer()
    indexer.index_all()
