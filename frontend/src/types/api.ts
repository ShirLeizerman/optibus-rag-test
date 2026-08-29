export interface Document {
  id: string;
  module: string;
  text: string;
}

export interface RetrievedDocument {
  chunk_id: string;
  document_id: string;
  module: string;
  text: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  retrieved_docs: RetrievedDocument[];
}

export interface QueryRequest {
  query: string;
}
