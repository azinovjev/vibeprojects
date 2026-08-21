import { useEffect, useState } from "react";
import { getGeneration } from "../api/client";
import type { Generation } from "../types";

const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES = new Set(["SUCCEEDED", "FAILED"]);

interface GenerationStatusProps {
  generation: Generation;
  onUpdate: (generation: Generation) => void;
}

export function GenerationStatus({ generation, onUpdate }: GenerationStatusProps) {
  const [current, setCurrent] = useState(generation);

  useEffect(() => {
    setCurrent(generation);
  }, [generation]);

  useEffect(() => {
    if (TERMINAL_STATUSES.has(current.status)) return;

    const timer = setInterval(async () => {
      try {
        const updated = await getGeneration(current.id);
        setCurrent(updated);
        onUpdate(updated);
      } catch {
        // transient polling error; the next tick will retry
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current.id, current.status]);

  return (
    <section className="card">
      <h2>4. Result</h2>
      {current.status === "PENDING" && <p>Queued…</p>}
      {current.status === "RUNNING" && <p>Veo is generating your video, this can take a minute or two…</p>}
      {current.status === "FAILED" && <p className="error-text">{current.error_message}</p>}
      {current.status === "SUCCEEDED" && current.video_url && (
        <video controls src={current.video_url} className="result-video" />
      )}
    </section>
  );
}
