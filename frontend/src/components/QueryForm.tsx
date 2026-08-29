import { useState } from "react";

interface Props {
  onSubmit: (query: string) => void;
  loading: boolean;
}

export function QueryForm({
  onSubmit,
  loading,
}: Props) {
  const [query, setQuery] = useState("");

  function handleSubmit(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    const trimmed = query.trim();

    if (!trimmed || loading) {
      return;
    }

    onSubmit(trimmed);
  }

  return (
    <form
      className="query-form"
      onSubmit={handleSubmit}
    >
      <label htmlFor="query">
        Ask a question
      </label>

      <textarea
        id="query"
        value={query}
        onChange={(event) =>
          setQuery(event.target.value)
        }
        placeholder="e.g. Which bus requires a brake inspection?"
        rows={4}
        maxLength={2000}
      />

      <div className="query-footer">
        <span>
          {query.length}/2000
        </span>

        <button
          type="submit"
          disabled={
            loading ||
            query.trim().length === 0
          }
        >
          {loading
            ? "Searching..."
            : "Ask"}
        </button>
      </div>
    </form>
  );
}
