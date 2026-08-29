import json
from pathlib import Path

from app.models import DocumentChunk
from app.rag.retriever import Retriever
from app.repositories.vector_store import (
    InMemoryVectorStore,
)


class FakeEmbeddingService:
    model = "fake"

    def embed(self, text: str) -> list[float]:
        text = text.lower()

        if "ridership" in text or "route 1" in text:
            return [1.0, 0.0, 0.0]

        if "brake" in text or "bus 215" in text:
            return [0.0, 1.0, 0.0]

        if "night" in text or "six hours" in text:
            return [0.0, 0.0, 1.0]

        return [0.5, 0.5, 0.5]


def test_evaluation_file_exists():
    path = Path("tests/evaluation_cases.json")

    assert path.exists()

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert len(data) == 5
