# Optibus RAG Homework

A small end-to-end Retrieval-Augmented Generation (RAG) application built for the Optibus GenAI homework assignment.

The application allows users to:

- View the available Optibus-style documents
- Ask natural-language questions
- Retrieve the most relevant document chunks
- Inspect retrieval similarity scores
- Generate a grounded answer from the retrieved context

The system supports both real OpenAI-powered RAG and a fully offline mode.

---

## Architecture

```text
React + TypeScript
       |
       | HTTP
       v
FastAPI
       |
       v
RAG Service
       |
       +--> Query Embedding
       |
       +--> In-Memory Vector Search
       |
       +--> Top-K Retrieved Chunks
       |
       +--> Context Construction
       |
       +--> Answer Generation
              |
              +--> OpenAI
              |
              +--> Offline Extractive Answer
```

### Backend components

The backend is intentionally separated into small components:

- `DocumentRepository` - loads source documents
- `chunker` - creates overlapping document chunks
- `EmbeddingService` - OpenAI embeddings
- `LocalHashEmbeddingService` - deterministic offline embeddings
- `EmbeddingCache` - persistent document embedding cache
- `InMemoryVectorStore` - cosine-similarity search
- `Retriever` - top-k retrieval
- `RAGService` - orchestration and context construction
- `LLMService` - OpenAI answer generation
- `LocalExtractiveLLMService` - offline grounded answer generation

---

## AI Modes

The application supports three modes.

### `AI_MODE=auto`

Default.

If `OPENAI_API_KEY` exists:

```text
OpenAI embeddings + OpenAI LLM
```

If no API key exists:

```text
Local deterministic embeddings + offline extractive answering
```

### `AI_MODE=local`

Forces fully offline execution.

No OpenAI API key or internet connection is required.

### `AI_MODE=openai`

Forces OpenAI execution.

An `OPENAI_API_KEY` is required.

---

## Embedding Cache

Document embeddings are generated during backend startup.

The application calculates a hash of the document chunks and checks for a matching cache before embedding them again.

Separate cache files are used for different embedding providers/models, for example:

```text
data/embeddings/
    local-local-hash-v2.json
    openai-text-embedding-3-small.json
```

This prevents vectors from different embedding spaces from being mixed.

Cache writes use atomic file replacement so application instances never read partially-written JSON files.

Each backend process loads the embeddings into its own in-memory vector store.

For a larger production deployment, the repository abstraction could be replaced with a persistent vector database such as pgvector or Qdrant.

For this small homework dataset, an in-memory vector store keeps the architecture simple and avoids unnecessary infrastructure.

---

## Offline Mode

Offline mode is intentionally implemented as a first-class feature rather than a fake API response.

The complete pipeline still runs:

```text
documents
    ↓
local embeddings
    ↓
vector search
    ↓
top-k retrieval
    ↓
context construction
    ↓
extractive grounded answer
```

The local hashed embedding implementation is deterministic and useful for development/testing without external dependencies.

It is not intended to provide the same semantic quality as the OpenAI embedding model.

---

## RAG Evaluation

The repository contains a small golden evaluation dataset:

```text
backend/tests/evaluation_cases.json
```

The evaluation checks retrieval quality using Recall@3.

This makes retrieval behavior measurable rather than relying only on manual examples.

---

# Running with Docker

## Requirements

Install:

- Docker Desktop
- Docker Compose

Clone the repository:

```bash
git clone https://github.com/ShirLeizerman/optibus-rag-test.git
cd optibus-rag-test
```

Create your environment file:

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

No OpenAI API key is required.

Start the application:

```bash
docker compose up --build
```

Open:

Frontend:

```text
http://localhost:3000
```

Backend API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

# Running with OpenAI

Edit `.env`:

```dotenv
AI_MODE=auto
OPENAI_API_KEY=your-key-here
```

Then rebuild/restart:

```bash
docker compose down
docker compose up --build
```

The health endpoint should return:

```json
{
  "status": "ok",
  "ai_mode": "openai"
}
```

---

# Running Fully Offline

Edit `.env`:

```dotenv
AI_MODE=local
OPENAI_API_KEY=
```

Then run:

```bash
docker compose up --build
```

Health response:

```json
{
  "status": "ok",
  "ai_mode": "local"
}
```

---

# Local Development Without Docker

## Backend

From the repository root:

```bash
cd backend
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

## Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# API

## GET `/documents`

Returns all available source documents.

Example:

```bash
curl http://localhost:8000/documents
```

## POST `/query`

Example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Which bus requires a brake inspection?"}'
```

Response:

```json
{
  "answer": "...",
  "retrieved_docs": [
    {
      "chunk_id": "ops_2_0",
      "document_id": "ops_2",
      "module": "OPS",
      "text": "...",
      "score": 0.8
    }
  ]
}
```

---

# Tests

From the `backend` directory:

```bash
pytest -q
```

The regular test suite does not require OpenAI or internet access.

---

# Example Questions

Try:

```text
Which bus requires a brake inspection?
```

```text
What is the continuous driving limit for night routes?
```

```text
Where will downtown routes be diverted during the marathon?
```

```text
What is expected to happen to Route 1 morning ridership?
```

```text
What does the fuel shortage alert say about Friday?
```

---

# Design Decisions

## Why an in-memory vector store?

The homework dataset is intentionally small.

Using a hosted or persistent vector database would introduce unnecessary infrastructure.

The vector store is behind a repository abstraction, so it can be replaced with a persistent implementation if the dataset grows.

## Why cache embeddings?

Document embeddings do not need to be recalculated on every application startup.

The cache is invalidated when:

- document content changes
- chunks change
- the embedding model changes

## Why support offline mode?

It makes the application:

- easy to review
- easy to test
- deterministic
- usable without sharing secrets
- usable without external network access

OpenAI mode remains the intended higher-quality semantic RAG implementation.

---

# Possible Production Improvements

Given more time and a larger dataset, the next improvements would be:

- Persistent vector database such as pgvector or Qdrant
- Batch embedding requests
- Hybrid lexical + vector search
- Reranking
- More comprehensive RAG evaluation
- Observability for retrieval latency and token usage
- Distributed locking for embedding generation across multiple application replicas
- Streaming LLM responses
- Authentication and rate limiting

These are intentionally omitted from the homework implementation to keep the solution focused and proportional to the assignment scope.