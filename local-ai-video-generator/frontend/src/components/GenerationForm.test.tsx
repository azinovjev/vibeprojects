import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GenerationForm } from "./GenerationForm";
import * as api from "../api/client";
import type { Generation, Photo } from "../types";

const mockPhoto: Photo = {
  id: "photo-1",
  original_filename: "cat.png",
  content_type: "image/png",
  size_bytes: 100,
  url: "/files/uploads/cat.png",
  created_at: "2026-01-01T00:00:00Z",
};

const mockGeneration: Generation = {
  id: "gen-1",
  photo_id: "photo-1",
  prompt_text: "make it move",
  model: "veo-3.1-fast-generate-preview",
  ratio: "16:9",
  duration: 8,
  seed: null,
  status: "PENDING",
  operation_name: null,
  video_url: null,
  error_message: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("GenerationForm", () => {
  it("disables submit until a photo is present", () => {
    render(<GenerationForm photo={null} presetText={null} presetVersion={0} onCreated={vi.fn()} />);
    expect(screen.getByRole("button", { name: /generate video/i })).toBeDisabled();
  });

  it("fills the prompt field when a preset is applied", () => {
    const { rerender } = render(
      <GenerationForm photo={mockPhoto} presetText={null} presetVersion={0} onCreated={vi.fn()} />,
    );
    rerender(
      <GenerationForm photo={mockPhoto} presetText="a preset prompt" presetVersion={1} onCreated={vi.fn()} />,
    );
    expect(screen.getByPlaceholderText(/describe how the photo/i)).toHaveValue("a preset prompt");
  });

  it("submits the entered prompt and reports the created generation", async () => {
    const createSpy = vi.spyOn(api, "createGeneration").mockResolvedValue(mockGeneration);
    const onCreated = vi.fn();

    render(<GenerationForm photo={mockPhoto} presetText={null} presetVersion={0} onCreated={onCreated} />);

    fireEvent.change(screen.getByPlaceholderText(/describe how the photo/i), {
      target: { value: "make it move" },
    });
    fireEvent.click(screen.getByRole("button", { name: /generate video/i }));

    await waitFor(() => expect(onCreated).toHaveBeenCalledWith(mockGeneration));
    expect(createSpy).toHaveBeenCalledWith({
      photo_id: "photo-1",
      prompt_text: "make it move",
      ratio: "16:9",
      duration: 8,
    });
  });
});
