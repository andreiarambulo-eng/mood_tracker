"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated, logout } from "@/lib/auth";
import type { User, ApiResponse } from "@/lib/types";

export function useAuth(requireAuth = true) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function check() {
      if (!isAuthenticated()) {
        if (requireAuth) router.replace("/login");
        setLoading(false);
        return;
      }

      try {
        const res = await api.get<ApiResponse<User>>("/auth/me");
        setUser(res.data);
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    }
    check();
  }, [requireAuth, router]);

  return { user, loading, logout };
}
