import hashlib
import json
from pathlib import Path

from app.models import DocumentChunk


class EmbeddingCache:
    def __init__(self, path: str):
        self.path = Path(path)

    @staticmethod
    def calculate_documents_hash(
        chunks: list[DocumentChunk],
    ) -> str:
        content = json.dumps(
            [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "module": chunk.module,
                    "text": chunk.text,
                }
                for chunk in chunks
            ],
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def exists(self) -> bool:
        return self.path.exists()

    def save(
        self,
        embedding_model: str,
        documents_hash: str,
        embeddings: dict[str, list[float]],
    ) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "embedding_model": embedding_model,
            "documents_hash": documents_hash,
            "embeddings": embeddings,
        }

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(payload, file)

    def load(self) -> dict | None:
        if not self.exists():
            return None

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)
