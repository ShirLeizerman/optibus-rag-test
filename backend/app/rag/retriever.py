from app.models import RetrievedDocument
from app.rag.embeddings import EmbeddingService
from app.repositories.vector_store import InMemoryVectorStore


class Retriever:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: InMemoryVectorStore,
        top_k: int,
        similarity_threshold: float,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve(
        self,
        query: str,
    ) -> list[RetrievedDocument]:
        query_embedding = (
            self.embedding_service.embed(query)
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        retrieved = []

        for chunk, score in results:
            if score < self.similarity_threshold:
                continue

            retrieved.append(
                RetrievedDocument(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    module=chunk.module,
                    text=chunk.text,
                    score=round(score, 4),
                )
            )

        return retrieved
