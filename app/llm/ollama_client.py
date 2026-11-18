
import ollama


class OllamaClient:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name

    def generate_answer(self, question, context):
        prompt = f"""
You are an assistant that answers questions about Indian companies.

Rules:
1. Answer using only the supplied context.
2. Do not invent facts or financial figures.
3. If the context does not contain the answer, say so.
4. Give a clear, concise answer.

Context:
{context}

Question:
{question}

Answer:
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]
