type ApiOptions = RequestInit & {
  authToken?: string;
  idempotencyKey?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const CLIENT_VERSION = process.env.NEXT_PUBLIC_CLIENT_VERSION ?? "0.1.0";

export function createRequestId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  return `req_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status: number,
    public traceId?: string,
  ) {
    super(message);
  }
}

export async function apiClient<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("X-Client-Version", CLIENT_VERSION);
  headers.set("X-Timezone", Intl.DateTimeFormat().resolvedOptions().timeZone);
  headers.set("X-Request-ID", createRequestId());
  if (options.authToken) headers.set("Authorization", `Bearer ${options.authToken}`);
  if (options.idempotencyKey) headers.set("Idempotency-Key", options.idempotencyKey);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload?.error?.message ?? "No pudimos completar la accion.";
    throw new ApiClientError(message, response.status, payload?.meta?.request_id);
  }
  return payload.data as T;
}
