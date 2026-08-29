from app.models import Document, DocumentChunk


def chunk_document(
    document: Document,
    max_chars: int = 1000,
    overlap_chars: int = 150,
) -> list[DocumentChunk]:
    """
    Split a document into overlapping chunks.

    The provided homework dataset contains short documents, so most
    documents remain a single chunk. The overlap makes the implementation
    safer as the dataset grows and documents become longer.
    """

    text = document.text.strip()

    if not text:
        return []

    if len(text) <= max_chars:
        return [
            DocumentChunk(
                chunk_id=f"{document.id}_0",
                document_id=document.id,
                module=document.module,
                text=text,
            )
        ]

    chunks: list[DocumentChunk] = []

    start = 0
    index = 0

    while start < len(text):
        end = min(
            start + max_chars,
            len(text),
        )

        # Avoid splitting a word when possible.
        if end < len(text):
            search_start = (
                start + int(max_chars * 0.6)
            )

            word_boundary = text.rfind(
                " ",
                search_start,
                end,
            )

            if word_boundary > start:
                end = word_boundary

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                DocumentChunk(
                    chunk_id=(
                        f"{document.id}_{index}"
                    ),
                    document_id=document.id,
                    module=document.module,
                    text=chunk_text,
                )
            )

            index += 1

        if end >= len(text):
            break

        next_start = max(
            end - overlap_chars,
            start + 1,
        )

        start = next_start

    return chunks