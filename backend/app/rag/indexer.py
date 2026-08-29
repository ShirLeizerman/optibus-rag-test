from app.models import DocumentChunk
from app.rag.cache import EmbeddingCache
from app.rag.chunker import chunk_document
from app.rag.embeddings import EmbeddingService
from app.repositories.documents import DocumentRepository
from app.repositories.vector_store import InMemoryVectorStore


class Indexer:
    def __init__(
        self,
        document_repository: DocumentRepository,
        embedding_service: EmbeddingService,
        cache: EmbeddingCache,
        vector_store: InMemoryVectorStore,
    ):
        self.document_repository = document_repository
        self.embedding_service = embedding_service
        self.cache = cache
        self.vector_store = vector_store

    def build_index(self) -> None:
        documents = self.document_repository.get_all()

        chunks: list[DocumentChunk] = []

        for document in documents:
            chunks.extend(
                chunk_document(document)
            )

        documents_hash = (
            self.cache.calculate_documents_hash(chunks)
        )

        cached = self.cache.load()

        if (
            cached
            and cached.get("embedding_model")
            == self.embedding_service.model
            and cached.get("documents_hash")
            == documents_hash
        ):
            self._load_cached_embeddings(
                chunks,
                cached["embeddings"],
            )
            return

        embeddings: dict[str, list[float]] = {}

        for chunk in chunks:
            embedding = self.embedding_service.embed(
                chunk.text
            )

            embeddings[chunk.chunk_id] = embedding

            self.vector_store.add(
                chunk,
                embedding,
            )

        self.cache.save(
            embedding_model=self.embedding_service.model,
            documents_hash=documents_hash,
            embeddings=embeddings,
        )

    def _load_cached_embeddings(
        self,
        chunks: list[DocumentChunk],
        embeddings: dict[str, list[float]],
    ) -> None:
        for chunk in chunks:
            embedding = embeddings.get(
                chunk.chunk_id
            )

            if embedding is None:
                raise ValueError(
                    f"Missing embedding for {chunk.chunk_id}"
                )

            self.vector_store.add(
                chunk,
                embedding,
            )
