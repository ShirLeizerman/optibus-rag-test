from app.models import Document, DocumentChunk


def chunk_document(
    document: Document,
    max_chars: int = 1000,
) -> list[DocumentChunk]:
    text = document.text.strip()

    if len(text) <= max_chars:
        return [
            DocumentChunk(
                chunk_id=f"{document.id}_0",
                document_id=document.id,
                module=document.module,
                text=text,
            )
        ]

    chunks = []

    for index, start in enumerate(range(0, len(text), max_chars)):
        chunk_text = text[start : start + max_chars]

        chunks.append(
            DocumentChunk(
                chunk_id=f"{document.id}_{index}",
                document_id=document.id,
                module=document.module,
                text=chunk_text,
            )
        )

    return chunks
