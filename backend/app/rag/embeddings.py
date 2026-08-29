import hashlib
import math
import re

from openai import OpenAI


_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "with",
}


def _stem(token: str) -> str:
    token = token.lower()

    suffixes = (
        "ingly",
        "edly",
        "ing",
        "ers",
        "ies",
        "ly",
        "ed",
        "es",
        "er",
        "s",
    )

    for suffix in suffixes:
        if (
            token.endswith(suffix)
            and len(token) > len(suffix) + 3
        ):
            return token[: -len(suffix)]

    return token


def tokenize_for_matching(text: str) -> list[str]:
    tokens = _TOKEN_PATTERN.findall(text.lower())

    return [
        _stem(token)
        for token in tokens
        if token not in _STOP_WORDS and len(token) > 1
    ]


class EmbeddingService:
    provider = "openai"

    def __init__(
        self,
        api_key: str | None,
        model: str,
    ):
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "for real OpenAI embeddings."
            )

        self.model = model

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


class LocalHashEmbeddingService:
    provider = "local"
    model = "local-hash-v2"

    DIMENSIONS = 384

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.DIMENSIONS

        tokens = tokenize_for_matching(text)

        for token in tokens:
            self._add_feature(
                vector,
                f"word:{token}",
                weight=1.0,
            )

            if len(token) >= 4:
                for index in range(len(token) - 2):
                    trigram = token[index:index + 3]

                    self._add_feature(
                        vector,
                        f"char:{trigram}",
                        weight=0.08,
                    )

        for index in range(len(tokens) - 1):
            self._add_feature(
                vector,
                f"bigram:{tokens[index]}:{tokens[index + 1]}",
                weight=0.5,
            )

        return self._normalize(vector)

    @classmethod
    def _add_feature(
        cls,
        vector: list[float],
        feature: str,
        weight: float,
    ) -> None:
        digest = hashlib.sha256(
            feature.encode("utf-8")
        ).digest()

        index = (
            int.from_bytes(
                digest[:4],
                byteorder="big",
            )
            % cls.DIMENSIONS
        )

        sign = (
            1.0
            if digest[4] % 2 == 0
            else -1.0
        )

        vector[index] += weight * sign

    @staticmethod
    def _normalize(
        vector: list[float],
    ) -> list[float]:
        magnitude = math.sqrt(
            sum(
                value * value
                for value in vector
            )
        )

        if magnitude == 0:
            return vector

        return [
            value / magnitude
            for value in vector
        ]