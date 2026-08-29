from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    module: str
    text: str


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    module: str
    text: str


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class RetrievedDocument(BaseModel):
    chunk_id: str
    document_id: str
    module: str
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    retrieved_docs: list[RetrievedDocument]
