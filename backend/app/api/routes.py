from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import (
    Document,
    QueryRequest,
    QueryResponse,
)
from app.rag.service import RAGService
from app.repositories.documents import DocumentRepository


router = APIRouter()

document_repository = DocumentRepository(
    "data/documents.json"
)

rag_service: RAGService | None = None


def set_rag_service(service: RAGService) -> None:
    global rag_service
    rag_service = service


@router.get(
    "/documents",
    response_model=list[Document],
)
def get_documents():
    return document_repository.get_all()


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty",
        )

    if len(request.query) > settings.max_query_length:
        raise HTTPException(
            status_code=400,
            detail="Query is too long",
        )

    if rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not ready",
        )

    try:
        return rag_service.query(
            request.query.strip()
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to process query",
        )
