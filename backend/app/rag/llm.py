import re

from openai import OpenAI

from app.rag.embeddings import tokenize_for_matching


class LLMService:
    """
    Real OpenAI answer generation service.
    """

    provider = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self.client = OpenAI(
            api_key=api_key,
            timeout=30.0,
        )

        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text.strip()


class LocalExtractiveLLMService:
    """
    Fully offline answer provider.

    Instead of pretending to be an LLM, this implementation performs
    grounded extractive answering from the retrieved RAG context.

    This keeps the pipeline functional without OpenAI while clearly
    distinguishing offline extractive answers from real LLM synthesis.
    """

    provider = "local"
    model = "local-extractive-v1"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        del system_prompt

        context = self._extract_block(
            user_prompt,
            "context",
        )

        question = self._extract_block(
            user_prompt,
            "question",
        )

        if not context.strip():
            return (
                "I don't have enough information "
                "in the provided documents to answer "
                "this question."
            )

        clean_context = self._remove_metadata(context)

        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                clean_context,
            )
            if sentence.strip()
        ]

        if not sentences:
            return (
                "I don't have enough information "
                "in the provided documents to answer "
                "this question."
            )

        question_tokens = set(
            tokenize_for_matching(question)
        )

        def score(sentence: str) -> tuple[int, float]:
            sentence_tokens = set(
                tokenize_for_matching(sentence)
            )

            overlap = len(
                question_tokens.intersection(
                    sentence_tokens
                )
            )

            # Prefer focused sentences when overlap is equal.
            length_penalty = len(sentence) / 1000

            return overlap, -length_penalty

        best_sentence = max(
            sentences,
            key=score,
        )

        return (
            "Offline extractive answer "
            "(OpenAI is not enabled):\n\n"
            f"{best_sentence}"
        )

    @staticmethod
    def _extract_block(
        prompt: str,
        tag: str,
    ) -> str:
        start_marker = f"<{tag}>"
        end_marker = f"</{tag}>"

        start = prompt.find(start_marker)
        end = prompt.find(end_marker)

        if start == -1 or end == -1:
            return ""

        start += len(start_marker)

        return prompt[start:end].strip()

    @staticmethod
    def _remove_metadata(context: str) -> str:
        lines = []

        for line in context.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            if (
                stripped.startswith("[Document ID:")
                or stripped.startswith("[Module:")
            ):
                continue

            lines.append(stripped)

        return " ".join(lines)