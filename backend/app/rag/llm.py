from openai import OpenAI


class LLMService:
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


class MockLLMService:
    model = "mock-llm-v1"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        context = self._extract_context(
            user_prompt
        )

        question = self._extract_question(
            user_prompt
        )

        if not context.strip():
            return (
                "I don't have enough information "
                "in the provided documents to answer "
                "this question."
            )

        first_document = self._extract_first_document(
            context
        )

        return (
            "Mock answer generated without OpenAI.\n\n"
            f"Question: {question}\n\n"
            "Based on the retrieved context:\n"
            f"{first_document}"
        )

    @staticmethod
    def _extract_context(
        prompt: str,
    ) -> str:
        start_marker = "<context>"
        end_marker = "</context>"

        start = prompt.find(start_marker)
        end = prompt.find(end_marker)

        if start == -1 or end == -1:
            return ""

        start += len(start_marker)

        return prompt[start:end].strip()

    @staticmethod
    def _extract_question(
        prompt: str,
    ) -> str:
        start_marker = "<question>"
        end_marker = "</question>"

        start = prompt.find(start_marker)
        end = prompt.find(end_marker)

        if start == -1 or end == -1:
            return ""

        start += len(start_marker)

        return prompt[start:end].strip()

    @staticmethod
    def _extract_first_document(
        context: str,
    ) -> str:
        documents = context.split(
            "[Document ID:"
        )

        if len(documents) < 2:
            return context

        first = documents[1]

        return "[Document ID:" + first.strip()
