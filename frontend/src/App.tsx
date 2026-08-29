import { useEffect, useState } from "react";

import { getDocuments, queryRag } from "./api/client";
import { AnswerPanel } from "./components/AnswerPanel";
import { DocumentList } from "./components/DocumentList";
import { QueryForm } from "./components/QueryForm";
import { RetrievedDocuments } from "./components/RetrievedDocuments";
import type {
  Document,
  RetrievedDocument,
} from "./types/api";

function App() {
  const [documents, setDocuments] =
    useState<Document[]>([]);

  const [answer, setAnswer] =
    useState<string | null>(null);

  const [retrievedDocuments, setRetrievedDocuments] =
    useState<RetrievedDocument[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    async function loadDocuments() {
      try {
        const data = await getDocuments();
        setDocuments(data);
      } catch {
        setError(
          "Failed to load documents.",
        );
      }
    }

    loadDocuments();
  }, []);

  async function handleQuery(query: string) {
    setLoading(true);
    setError(null);
    setAnswer(null);
    setRetrievedDocuments([]);

    try {
      const result = await queryRag(query);

      setAnswer(result.answer);

      setRetrievedDocuments(
        result.retrieved_docs,
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Optibus RAG Dashboard</h1>

          <p>
            Semantic search and grounded
            answers over transit documents.
          </p>
        </div>
      </header>

      <main className="dashboard">
        <aside>
          <DocumentList
            documents={documents}
          />
        </aside>

        <div className="content">
          <section className="panel">
            <QueryForm
              onSubmit={handleQuery}
              loading={loading}
            />
          </section>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          <AnswerPanel answer={answer} />

          <RetrievedDocuments
            documents={retrievedDocuments}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
