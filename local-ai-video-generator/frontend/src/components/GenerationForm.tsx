import { useEffect, useState } from "react";
import { ApiError, createGeneration } from "../api/client";
import type { Generation, Photo } from "../types";

interface GenerationFormProps {
  photo: Photo | null;
  presetText: string | null;
  presetVersion: number;
  onCreated: (generation: Generation) => void;
}

const RATIO_OPTIONS = ["16:9", "9:16"];
const DURATION_OPTIONS = [4, 6, 8];

export function GenerationForm({ photo, presetText, presetVersion, onCreated }: GenerationFormProps) {
  const [promptText, setPromptText] = useState("");
  const [ratio, setRatio] = useState(RATIO_OPTIONS[0]);
  const [duration, setDuration] = useState(DURATION_OPTIONS[DURATION_OPTIONS.length - 1]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (presetText !== null) setPromptText(presetText);
    // presetVersion increments each time "Use this prompt" is clicked, even for the same
    // preset text, so this effect must depend on it rather than on presetText alone.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [presetVersion]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!photo) return;

    setError(null);
    setIsSubmitting(true);
    try {
      const generation = await createGeneration({
        photo_id: photo.id,
        prompt_text: promptText,
        ratio,
        duration,
      });
      onCreated(generation);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start generation.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="card">
      <h2>3. Generate video</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Prompt
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            placeholder="Describe how the photo should move…"
            required
          />
        </label>
        <div className="field-row">
          <label>
            Aspect ratio
            <select value={ratio} onChange={(e) => setRatio(e.target.value)}>
              {RATIO_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label>
            Duration (seconds)
            <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
              {DURATION_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>
        {error && <p className="error-text">{error}</p>}
        <button type="submit" disabled={!photo || isSubmitting}>
          {isSubmitting ? "Starting…" : "Generate video"}
        </button>
        {!photo && <p className="hint">Upload a photo first.</p>}
      </form>
    </section>
  );
}
