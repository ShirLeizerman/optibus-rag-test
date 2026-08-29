import type {
  Document,
  QueryResponse,
} from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(
    `${API_BASE_URL}/documents`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load documents",
    );
  }

  return response.json();
}

export async function queryRag(
  query: string,
): Promise<QueryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    },
  );

  if (!response.ok) {
    const body = await response.json().catch(
      () => null,
    );

    throw new Error(
      body?.detail ??
        "Failed to process query",
    );
  }

  return response.json();
}
