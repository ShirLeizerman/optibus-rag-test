import math

from app.models import DocumentChunk


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have the same dimension")

    dot_product = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class InMemoryVectorStore:
    def __init__(self):
        self.items: list[tuple[DocumentChunk, list[float]]] = []

    def add(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
    ) -> None:
        self.items.append((chunk, embedding))

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[DocumentChunk, float]]:
        scored = []

        for chunk, embedding in self.items:
            score = cosine_similarity(
                query_embedding,
                embedding,
            )

            scored.append((chunk, score))

        scored.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scored[:top_k]
