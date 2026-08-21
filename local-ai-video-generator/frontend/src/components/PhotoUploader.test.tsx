import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PhotoUploader } from "./PhotoUploader";
import * as api from "../api/client";
import type { Photo } from "../types";

const mockPhoto: Photo = {
  id: "photo-1",
  original_filename: "cat.png",
  content_type: "image/png",
  size_bytes: 100,
  url: "/files/uploads/cat.png",
  created_at: "2026-01-01T00:00:00Z",
};

describe("PhotoUploader", () => {
  it("uploads the selected file and reports it to the parent", async () => {
    const uploadSpy = vi.spyOn(api, "uploadPhoto").mockResolvedValue(mockPhoto);
    const onUploaded = vi.fn();

    render(<PhotoUploader photo={null} onUploaded={onUploaded} />);

    const file = new File(["bytes"], "cat.png", { type: "image/png" });
    const input = screen.getByLabelText(/choose a photo/i) as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => expect(onUploaded).toHaveBeenCalledWith(mockPhoto));
    expect(uploadSpy).toHaveBeenCalledWith(file);
  });

  it("renders the current photo preview when provided", () => {
    render(<PhotoUploader photo={mockPhoto} onUploaded={vi.fn()} />);
    expect(screen.getByAltText("cat.png")).toBeInTheDocument();
  });
});
