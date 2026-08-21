import { useCallback, useEffect, useState } from "react";
import { listGenerations, listPrompts } from "./api/client";
import { GenerationForm } from "./components/GenerationForm";
import { GenerationHistory } from "./components/GenerationHistory";
import { GenerationStatus } from "./components/GenerationStatus";
import { PhotoUploader } from "./components/PhotoUploader";
import { PromptPresetManager } from "./components/PromptPresetManager";
import type { Generation, Photo, PromptPreset } from "./types";

export default function App() {
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [presets, setPresets] = useState<PromptPreset[]>([]);
  const [presetText, setPresetText] = useState<string | null>(null);
  const [presetVersion, setPresetVersion] = useState(0);
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [activeGeneration, setActiveGeneration] = useState<Generation | null>(null);

  const refreshPresets = useCallback(async () => {
    setPresets(await listPrompts());
  }, []);

  useEffect(() => {
    refreshPresets();
    listGenerations().then(setGenerations).catch(() => undefined);
  }, [refreshPresets]);

  function handleUsePreset(text: string) {
    setPresetText(text);
    setPresetVersion((v) => v + 1);
  }

  function handleGenerationCreated(generation: Generation) {
    setActiveGeneration(generation);
    setGenerations((prev) => [generation, ...prev]);
  }

  function handleGenerationUpdate(updated: Generation) {
    setActiveGeneration(updated);
    setGenerations((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
  }

  return (
    <main className="app">
      <header>
        <h1>Photo → Video with Gemini</h1>
        <p className="hint">
          Upload a photo, pick or write a prompt, and generate a video with Google's Veo image-to-video model.
        </p>
      </header>

      <PhotoUploader photo={photo} onUploaded={setPhoto} />
      <PromptPresetManager presets={presets} onPresetsChanged={refreshPresets} onUsePreset={handleUsePreset} />
      <GenerationForm
        photo={photo}
        presetText={presetText}
        presetVersion={presetVersion}
        onCreated={handleGenerationCreated}
      />
      {activeGeneration && <GenerationStatus generation={activeGeneration} onUpdate={handleGenerationUpdate} />}
      <GenerationHistory generations={generations} />
    </main>
  );
}
