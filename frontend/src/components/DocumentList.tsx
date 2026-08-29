import type { Document } from "../types/api";

interface Props {
  documents: Document[];
}

export function DocumentList({
  documents,
}: Props) {
  return (
    <section className="panel document-panel">
      <div className="panel-header">
        <h2>Documents</h2>
        <span className="count">
          {documents.length}
        </span>
      </div>

      <div className="document-list">
        {documents.map((document) => (
          <div
            key={document.id}
            className="document-item"
          >
            <div className="document-title">
              {document.id}
            </div>

            <div className="document-module">
              {document.module}
            </div>

            <p>{document.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
