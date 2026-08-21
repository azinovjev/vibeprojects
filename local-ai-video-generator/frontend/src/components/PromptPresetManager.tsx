import { useState } from "react";
import { ApiError, createPrompt, deletePrompt, updatePrompt } from "../api/client";
import type { PromptPreset } from "../types";

interface PromptPresetManagerProps {
  presets: PromptPreset[];
  onPresetsChanged: () => void;
  onUsePreset: (promptText: string) => void;
}

const EMPTY_FORM = { name: "", promptText: "" };

export function PromptPresetManager({ presets, onPresetsChanged, onUsePreset }: PromptPresetManagerProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function startEdit(preset: PromptPreset) {
    setEditingId(preset.id);
    setForm({ name: preset.name, promptText: preset.prompt_text });
    setError(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await createPrompt(form.name, form.promptText);
      setForm(EMPTY_FORM);
      setIsCreating(false);
      onPresetsChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save preset.");
    }
  }

  async function handleUpdate(event: React.FormEvent, id: string) {
    event.preventDefault();
    setError(null);
    try {
      await updatePrompt(id, form.name, form.promptText);
      cancelEdit();
      onPresetsChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not update preset.");
    }
  }

  async function handleDelete(id: string) {
    setError(null);
    try {
      await deletePrompt(id);
      onPresetsChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete preset.");
    }
  }

  return (
    <section className="card">
      <h2>2. Configure your prompt</h2>
      <p className="hint">Save reusable prompt presets, or pick one to use as a starting point below.</p>
      {error && <p className="error-text">{error}</p>}

      <ul className="preset-list">
        {presets.map((preset) => (
          <li key={preset.id} className="preset-item">
            {editingId === preset.id ? (
              <form onSubmit={(e) => handleUpdate(e, preset.id)} className="preset-form">
                <input
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  placeholder="Preset name"
                  required
                />
                <textarea
                  value={form.promptText}
                  onChange={(e) => setForm((f) => ({ ...f, promptText: e.target.value }))}
                  placeholder="Prompt text"
                  required
                />
                <div className="button-row">
                  <button type="submit">Save</button>
                  <button type="button" onClick={cancelEdit}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <>
                <div className="preset-summary">
                  <strong>{preset.name}</strong>
                  <p>{preset.prompt_text}</p>
                </div>
                <div className="button-row">
                  <button type="button" onClick={() => onUsePreset(preset.prompt_text)}>
                    Use this prompt
                  </button>
                  <button type="button" onClick={() => startEdit(preset)}>
                    Edit
                  </button>
                  <button type="button" onClick={() => handleDelete(preset.id)}>
                    Delete
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>

      {isCreating ? (
        <form onSubmit={handleCreate} className="preset-form">
          <input
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="Preset name"
            required
          />
          <textarea
            value={form.promptText}
            onChange={(e) => setForm((f) => ({ ...f, promptText: e.target.value }))}
            placeholder="Prompt text"
            required
          />
          <div className="button-row">
            <button type="submit">Save preset</button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false);
                setForm(EMPTY_FORM);
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <button type="button" onClick={() => setIsCreating(true)}>
          + New preset
        </button>
      )}
    </section>
  );
}
