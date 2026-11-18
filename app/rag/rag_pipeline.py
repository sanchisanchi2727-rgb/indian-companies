
from app.retrieval.hybrid_search import HybridSearch
from app.llm.ollama_client import OllamaClient


class RAGPipeline:
    def __init__(self):
        self.searcher = HybridSearch()
        self.llm = OllamaClient()

    def ask(self, question):
        results = self.searcher.search(
            query=question,
            top_k=5
        )

        if not results:
            return {
                "answer": "I could not find relevant company information.",
                "sources": []
            }

        context_parts = []
        sources = []

        for result in results:
            metadata = result["metadata"]
            company = metadata.get("company", "Unknown")
            source = metadata.get("source", "Unknown")

            context_parts.append(
                f"Company: {company}\n"
                f"Source: {source}\n"
                f"Information: {result['document']}"
            )

            sources.append({
                "company": company,
                "source": source,
                "text": result["document"][:200]
            })

        context = "\n\n".join(context_parts)

        answer = self.llm.generate_answer(
            question=question,
            context=context
        )

        return {
            "answer": answer,
            "sources": sources
        }
