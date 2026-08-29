from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router, set_rag_service
from app.config import settings
from app.rag.cache import EmbeddingCache
from app.rag.embeddings import (
    EmbeddingService,
    MockEmbeddingService,
)
from app.rag.indexer import Indexer
from app.rag.llm import (
    LLMService,
    MockLLMService,
)
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.repositories.documents import DocumentRepository
from app.repositories.vector_store import InMemoryVectorStore


def create_embedding_service():
    if settings.use_mock_ai:
        return MockEmbeddingService()

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required "
            "when USE_MOCK_AI=false."
        )

    return EmbeddingService(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )


def create_llm_service():
    if settings.use_mock_ai:
        return MockLLMService()

    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required "
            "when USE_MOCK_AI=false."
        )

    return LLMService(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    document_repository = DocumentRepository(
        "data/documents.json"
    )

    embedding_service = create_embedding_service()

    vector_store = InMemoryVectorStore()

    cache = EmbeddingCache(
        "data/embeddings.json"
    )

    indexer = Indexer(
        document_repository=document_repository,
        embedding_service=embedding_service,
        cache=cache,
        vector_store=vector_store,
    )

    indexer.build_index()

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        top_k=settings.top_k,
        similarity_threshold=settings.similarity_threshold,
    )

    llm_service = create_llm_service()

    rag_service = RAGService(
        retriever=retriever,
        llm_service=llm_service,
        max_context_chars=settings.max_context_chars,
    )

    set_rag_service(rag_service)

    yield


app = FastAPI(
    title="Optibus RAG API",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_mode": (
            "mock"
            if settings.use_mock_ai
            else "openai"
        ),
    }


app.include_router(router)
