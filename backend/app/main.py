import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router, set_rag_service
from app.config import settings
from app.rag.cache import EmbeddingCache
from app.rag.embeddings import (
    EmbeddingService,
    LocalHashEmbeddingService,
)
from app.rag.indexer import Indexer
from app.rag.llm import (
    LLMService,
    LocalExtractiveLLMService,
)
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.repositories.documents import DocumentRepository
from app.repositories.vector_store import InMemoryVectorStore


def create_embedding_service(ai_mode: str):
    if ai_mode == "openai":
        return EmbeddingService(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )

    return LocalHashEmbeddingService()


def create_llm_service(ai_mode: str):
    if ai_mode == "openai":
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required "
                "for OpenAI mode."
            )

        return LLMService(
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
        )

    return LocalExtractiveLLMService()


def create_cache_path(
    embedding_service,
) -> Path:
    provider = getattr(
        embedding_service,
        "provider",
        "unknown",
    )

    model = getattr(
        embedding_service,
        "model",
        "unknown",
    )

    safe_model = re.sub(
        r"[^a-zA-Z0-9_.-]+",
        "-",
        model,
    )

    filename = (
        f"{provider}-{safe_model}.json"
    )

    return (
        Path(settings.embedding_cache_dir)
        / filename
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    ai_mode = settings.resolve_ai_mode()

    app.state.ai_mode = ai_mode

    document_repository = DocumentRepository(
        "data/documents.json"
    )

    embedding_service = (
        create_embedding_service(ai_mode)
    )

    vector_store = InMemoryVectorStore()

    cache_path = create_cache_path(
        embedding_service
    )

    cache = EmbeddingCache(
        str(cache_path)
    )

    indexer = Indexer(
        document_repository=document_repository,
        embedding_service=embedding_service,
        cache=cache,
        vector_store=vector_store,
    )

    indexer.build_index()

    if ai_mode == "openai":
        similarity_threshold = (
            settings.openai_similarity_threshold
        )
    else:
        similarity_threshold = (
            settings.local_similarity_threshold
        )

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        top_k=settings.top_k,
        similarity_threshold=similarity_threshold,
    )

    llm_service = create_llm_service(
        ai_mode
    )

    rag_service = RAGService(
        retriever=retriever,
        llm_service=llm_service,
        max_context_chars=settings.max_context_chars,
    )

    set_rag_service(rag_service)

    yield


app = FastAPI(
    title="Optibus RAG API",
    description=(
        "A small Retrieval-Augmented Generation service "
        "for Optibus-style transit documents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_mode": settings.resolve_ai_mode(),
    }


app.include_router(router)