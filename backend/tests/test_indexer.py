from app.models import Document
from app.rag.cache import EmbeddingCache
from app.rag.indexer import Indexer
from app.repositories.documents import DocumentRepository
from app.repositories.vector_store import InMemoryVectorStore


class FakeEmbeddingService:
    model = "fake-model"

    def embed(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def test_indexer_creates_cache(tmp_path):
    documents_file = tmp_path / "documents.json"
    cache_file = tmp_path / "embeddings.json"

    documents_file.write_text(
        """
        [
          {
            "id": "test_1",
            "module": "Test",
            "text": "hello world"
          }
        ]
        """,
        encoding="utf-8",
    )

    repository = DocumentRepository(
        str(documents_file)
    )

    vector_store = InMemoryVectorStore()

    cache = EmbeddingCache(
        str(cache_file)
    )

    embedding_service = FakeEmbeddingService()

    indexer = Indexer(
        document_repository=repository,
        embedding_service=embedding_service,
        cache=cache,
        vector_store=vector_store,
    )

    indexer.build_index()

    assert cache_file.exists()
    assert len(vector_store.items) == 1
