import hashlib
import math

from openai import OpenAI


class EmbeddingService:
    def __init__(
        self,
        api_key: str | None,
        model: str,
    ):
        self.model = model

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "for real embeddings."
            )

        self.client = OpenAI(
            api_key=api_key,
            timeout=30.0,
        )

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding


class MockEmbeddingService:
    model = "mock-embedding-v1"

    DIMENSIONS = 128

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.DIMENSIONS

        words = text.lower().split()

        for word in words:
            digest = hashlib.sha256(
                word.encode("utf-8")
            ).digest()

            index = int.from_bytes(
                digest[:4],
                byteorder="big",
            ) % self.DIMENSIONS

            vector[index] += 1.0

        return self._normalize(vector)

    @staticmethod
    def _normalize(
        vector: list[float],
    ) -> list[float]:
        magnitude = math.sqrt(
            sum(value * value for value in vector)
        )

        if magnitude == 0:
            return vector

        return [
            value / magnitude
            for value in vector
        ]
