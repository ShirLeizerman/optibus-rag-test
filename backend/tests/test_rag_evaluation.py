import json
from pathlib import Path

from app.rag.chunker import chunk_document
from app.rag.embeddings import (
    LocalHashEmbeddingService,
)
from app.rag.retriever import Retriever
from app.repositories.documents import (
    DocumentRepository,
)
from app.repositories.vector_store import (
    InMemoryVectorStore,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]

EVALUATION_FILE = (
    Path(__file__).resolve().parent
    / "evaluation_cases.json"
)

DOCUMENTS_FILE = (
    BACKEND_DIR
    / "data"
    / "documents.json"
)


def load_evaluation_cases() -> list[dict]:
    return json.loads(
        EVALUATION_FILE.read_text(
            encoding="utf-8"
        )
    )


def create_offline_retriever() -> Retriever:
    embedding_service = (
        LocalHashEmbeddingService()
    )

    vector_store = InMemoryVectorStore()

    repository = DocumentRepository(
        str(DOCUMENTS_FILE)
    )

    for document in repository.get_all():
        for chunk in chunk_document(document):
            vector_store.add(
                chunk,
                embedding_service.embed(
                    chunk.text
                ),
            )

    return Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        top_k=3,

        # Evaluation focuses on ranking/recall@3.
        # Threshold filtering is evaluated by the application layer.
        similarity_threshold=-1.0,
    )


def test_evaluation_file_has_five_cases():
    cases = load_evaluation_cases()

    assert len(cases) == 5


def test_offline_embedding_is_deterministic():
    service = LocalHashEmbeddingService()

    first = service.embed(
        "Bus 215 requires brake inspection"
    )

    second = service.embed(
        "Bus 215 requires brake inspection"
    )

    assert first == second


def test_retrieval_recall_at_3():
    cases = load_evaluation_cases()

    retriever = create_offline_retriever()

    hits = 0

    for case in cases:
        results = retriever.retrieve(
            case["query"]
        )

        retrieved_ids = {
            item.document_id
            for item in results
        }

        if (
            case["expected_document_id"]
            in retrieved_ids
        ):
            hits += 1

    recall_at_3 = hits / len(cases)

    assert recall_at_3 >= 0.8