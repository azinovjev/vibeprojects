import { useRef, useState } from "react";
import { ApiError, uploadPhoto } from "../api/client";
import type { Photo } from "../types";

interface PhotoUploaderProps {
  photo: Photo | null;
  onUploaded: (photo: Photo) => void;
}

export function PhotoUploader({ photo, onUploaded }: PhotoUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsUploading(true);
    try {
      const uploaded = await uploadPhoto(file);
      onUploaded(uploaded);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <section className="card">
      <h2>1. Upload a photo</h2>
      <label className="file-drop">
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        {isUploading ? "Uploading…" : "Choose a photo (JPEG, PNG or WebP)"}
      </label>
      {error && <p className="error-text">{error}</p>}
      {photo && (
        <div className="photo-preview">
          <img src={photo.url} alt={photo.original_filename} />
          <span>{photo.original_filename}</span>
        </div>
      )}
    </section>
  );
}
