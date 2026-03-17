import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = Cookies.get("auth_token");

  // Only send auth header for non-public endpoints
  const isPublicEndpoint = path === "/auth/login" || path === "/auth/register";

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (!isPublicEndpoint && token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers as Record<string, string>),
    },
  });

  const data = await res.json();

  if (!res.ok) {
    // Handle FastAPI validation errors (array format) and standard errors
    let errorMessage = "Request failed";
    if (data.message) {
      errorMessage = data.message;
    } else if (typeof data.detail === "string") {
      errorMessage = data.detail;
    } else if (data.detail?.message) {
      errorMessage = data.detail.message;
    } else if (Array.isArray(data.detail)) {
      errorMessage = data.detail.map((e: { msg?: string }) => e.msg).join(", ");
    }
    throw new Error(errorMessage);
  }

  return data;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
