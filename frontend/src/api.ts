export const API_URL = (import.meta as ImportMeta & { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ?? "http://127.0.0.1:8001";

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}
