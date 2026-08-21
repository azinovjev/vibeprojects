import type { Generation } from "../types";

interface GenerationHistoryProps {
  generations: Generation[];
}

const STATUS_LABEL: Record<Generation["status"], string> = {
  PENDING: "Queued",
  RUNNING: "Generating…",
  SUCCEEDED: "Done",
  FAILED: "Failed",
};

export function GenerationHistory({ generations }: GenerationHistoryProps) {
  if (generations.length === 0) return null;

  return (
    <section className="card">
      <h2>History</h2>
      <ul className="history-list">
        {generations.map((generation) => (
          <li key={generation.id} className={`history-item status-${generation.status.toLowerCase()}`}>
            <span className="history-status">{STATUS_LABEL[generation.status]}</span>
            <span className="history-prompt">{generation.prompt_text}</span>
            {generation.video_url && (
              <a href={generation.video_url} target="_blank" rel="noreferrer">
                View video
              </a>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
