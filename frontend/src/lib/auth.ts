import Cookies from "js-cookie";
import { api } from "./api";
import type { ApiResponse, User } from "./types";

export async function login(
  email: string,
  password: string
): Promise<User> {
  const res = await api.post<ApiResponse<{ token: string; user: User }>>(
    "/auth/login",
    { email, password }
  );

  if (res.success && res.data.token) {
    Cookies.set("auth_token", res.data.token, {
      expires: 1,
      sameSite: "lax",
    });
    return res.data.user;
  }

  throw new Error(res.message);
}

export async function register(
  email: string,
  full_name: string,
  password: string
): Promise<void> {
  const res = await api.post<ApiResponse>("/auth/register", {
    email,
    full_name,
    password,
  });

  if (!res.success) {
    throw new Error(res.message);
  }
}

export function logout(): void {
  Cookies.remove("auth_token");
  window.location.href = "/login";
}

export function getToken(): string | undefined {
  return Cookies.get("auth_token");
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
