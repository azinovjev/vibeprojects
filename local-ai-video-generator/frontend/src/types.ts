export interface Photo {
  id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  url: string;
  created_at: string;
}

export interface PromptPreset {
  id: string;
  name: string;
  prompt_text: string;
  created_at: string;
  updated_at: string;
}

export type GenerationStatus = "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED";

export interface Generation {
  id: string;
  photo_id: string;
  prompt_text: string;
  model: string;
  ratio: string;
  duration: number;
  seed: number | null;
  status: GenerationStatus;
  operation_name: string | null;
  video_url: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface GenerationRequest {
  photo_id: string;
  prompt_text: string;
  model?: string;
  ratio?: string;
  duration?: number;
  seed?: number;
}
