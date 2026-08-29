interface Props {
  answer: string | null;
}

export function AnswerPanel({
  answer,
}: Props) {
  return (
    <section className="panel">
      <h2>Answer</h2>

      {!answer ? (
        <div className="empty-state">
          Ask a question to see the
          generated answer.
        </div>
      ) : (
        <div className="answer">
          {answer}
        </div>
      )}
    </section>
  );
}
