import type {
  RetrievedDocument,
} from "../types/api";

interface Props {
  documents: RetrievedDocument[];
}

export function RetrievedDocuments({
  documents,
}: Props) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Retrieved Documents</h2>

        <span className="count">
          {documents.length}
        </span>
      </div>

      {documents.length === 0 ? (
        <div className="empty-state">
          No documents were retrieved.
        </div>
      ) : (
        <div className="retrieved-list">
          {documents.map((document) => (
            <article
              key={document.chunk_id}
              className="retrieved-item"
            >
              <div className="retrieved-header">
                <div>
                  <strong>
                    {document.document_id}
                  </strong>

                  <span className="module-badge">
                    {document.module}
                  </span>
                </div>

                <span className="score">
                  Similarity:{" "}
                  {document.score.toFixed(3)}
                </span>
              </div>

              <p>{document.text}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
