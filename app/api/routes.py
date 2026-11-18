
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.rag_pipeline import RAGPipeline

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the RAG pipeline
rag_pipeline = RAGPipeline()


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000
    )


@router.get("/health")
def health():
    """Check whether the API is running."""
    return {"status": "ok"}


@router.post("/ask")
def ask_question(request: QuestionRequest):
    """Answer questions about companies using the dataset and RAG."""

    try:
        original_question = request.question.strip()
        question = original_question.lower()

        # Handle company-count questions separately
        count_keywords = [
            "how many companies",
            "how many company",
            "number of companies",
            "company count",
            "total companies",
            "count companies",
            "count the companies",
            "how many company records",
            "how many companies are listed",
            "how many companies are there"
        ]

        if any(keyword in question for keyword in count_keywords):
            data_dir = Path("data/raw")

            if not data_dir.exists():
                raise HTTPException(
                    status_code=500,
                    detail="Company dataset directory was not found."
                )

            companies = set()
            files = list(data_dir.glob("*.json"))
            failed_files = 0

            for file_path in files:
                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        record = json.load(file)

                    if not isinstance(record, dict):
                        failed_files += 1
                        continue

                    # Support both JSON formats
                    company = (
                        record.get("company")
                        or record.get("company_name")
                    )

                    if isinstance(company, str) and company.strip():
                        companies.add(company.strip())

                except (json.JSONDecodeError, OSError) as error:
                    failed_files += 1
                    logger.warning(
                        "Could not read %s: %s",
                        file_path.name,
                        error
                    )

            company_count = len(companies)

            return {
                "answer": (
                    f"There are {company_count} unique named records "
                    f"in your dataset, from {len(files)} JSON files."
                ),
                "company_count": company_count,
                "json_file_count": len(files),
                "failed_files": failed_files,
                "sources": []
            }

        # Send all other questions to the RAG pipeline
        result = rag_pipeline.ask(original_question)
        return result

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("RAG request failed")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer the question: {str(error)}"
        ) from error
