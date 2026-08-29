import hashlib
import json
import os
import tempfile
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

        temp_path: str | None = None

        try:
            # Create the temporary file in the SAME directory so
            # os.replace remains atomic on the same filesystem.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                delete=False,
                suffix=".tmp",
            ) as temp_file:
                temp_path = temp_file.name

                json.dump(
                    payload,
                    temp_file,
                    ensure_ascii=False,
                )

                temp_file.flush()
                os.fsync(temp_file.fileno())

            # Atomic replacement prevents readers from seeing a
            # partially-written cache file.
            os.replace(
                temp_path,
                self.path,
            )

            temp_path = None

        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def load(self) -> dict | None:
        if not self.exists():
            return None

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):
            # Invalid/stale cache should never prevent application
            # startup. The indexer will simply regenerate embeddings.
            return None