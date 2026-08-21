import type { Generation, GenerationRequest, Photo, PromptPreset } from "../types";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // response had no JSON body; fall back to statusText
    }
    throw new ApiError(message, response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function uploadPhoto(file: File): Promise<Photo> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/photos", { method: "POST", body: formData });
  return handleResponse<Photo>(response);
}

export async function listPhotos(): Promise<Photo[]> {
  const response = await fetch("/api/photos");
  return handleResponse<Photo[]>(response);
}

export async function listPrompts(): Promise<PromptPreset[]> {
  const response = await fetch("/api/prompts");
  return handleResponse<PromptPreset[]>(response);
}

export async function createPrompt(name: string, promptText: string): Promise<PromptPreset> {
  const response = await fetch("/api/prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, prompt_text: promptText }),
  });
  return handleResponse<PromptPreset>(response);
}

export async function updatePrompt(id: string, name: string, promptText: string): Promise<PromptPreset> {
  const response = await fetch(`/api/prompts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, prompt_text: promptText }),
  });
  return handleResponse<PromptPreset>(response);
}

export async function deletePrompt(id: string): Promise<void> {
  const response = await fetch(`/api/prompts/${id}`, { method: "DELETE" });
  await handleResponse<void>(response);
}

export async function createGeneration(request: GenerationRequest): Promise<Generation> {
  const response = await fetch("/api/generations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return handleResponse<Generation>(response);
}

export async function getGeneration(id: string): Promise<Generation> {
  const response = await fetch(`/api/generations/${id}`);
  return handleResponse<Generation>(response);
}

export async function listGenerations(): Promise<Generation[]> {
  const response = await fetch("/api/generations");
  return handleResponse<Generation[]>(response);
}
