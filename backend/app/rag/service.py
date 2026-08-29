from app.models import QueryResponse
from app.rag.llm import LLMService
from app.rag.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from app.rag.retriever import Retriever


class RAGService:
    def __init__(
        self,
        retriever: Retriever,
        llm_service: LLMService,
        max_context_chars: int,
    ):
        self.retriever = retriever
        self.llm_service = llm_service
        self.max_context_chars = max_context_chars

    def query(
        self,
        question: str,
    ) -> QueryResponse:
        retrieved_docs = self.retriever.retrieve(
            question
        )

        if not retrieved_docs:
            return QueryResponse(
                answer=(
                    "I don't have enough information "
                    "in the provided documents to answer "
                    "this question."
                ),
                retrieved_docs=[],
            )

        context_parts = []
        current_length = 0

        for document in retrieved_docs:
            part = (
                f"[Document ID: {document.document_id}]\n"
                f"[Module: {document.module}]\n"
                f"{document.text}\n"
            )

            if (
                current_length + len(part)
                > self.max_context_chars
            ):
                break

            context_parts.append(part)
            current_length += len(part)

        context = "\n".join(context_parts)

        user_prompt = build_user_prompt(
            question=question,
            context=context,
        )

        answer = self.llm_service.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return QueryResponse(
            answer=answer,
            retrieved_docs=retrieved_docs,
        )
