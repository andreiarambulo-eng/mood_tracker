"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { MoodEntry, ApiResponse, PaginatedResponse } from "@/lib/types";

export function useMood() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMood = useCallback(
    async (mood_score: number, remark?: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.post<ApiResponse<MoodEntry>>("/moods/create", {
          mood_score,
          remark,
        });
        return res.data;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to create mood";
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getToday = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ApiResponse<MoodEntry>>("/moods/today");
      return res.data;
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateMood = useCallback(
    async (moodId: string, mood_score?: number, remark?: string) => {
      setLoading(true);
      setError(null);
      try {
        const body: Record<string, unknown> = {};
        if (mood_score !== undefined) body.mood_score = mood_score;
        if (remark !== undefined) body.remark = remark;

        const res = await api.patch<ApiResponse<MoodEntry>>(
          `/moods/edit/${moodId}`,
          body
        );
        return res.data;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to update mood";
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getMoods = useCallback(
    async (
      page = 1,
      limit = 10,
      startDate?: string,
      endDate?: string
    ) => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams({
          page: String(page),
          limit: String(limit),
        });
        if (startDate) params.set("start_date", startDate);
        if (endDate) params.set("end_date", endDate);

        const res = await api.get<PaginatedResponse<MoodEntry>>(
          `/moods/get?${params}`
        );
        return res.data;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to fetch moods";
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteMood = useCallback(async (moodId: string) => {
    setLoading(true);
    setError(null);
    try {
      await api.delete<ApiResponse>(`/moods/${moodId}`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to delete mood";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { createMood, getToday, updateMood, getMoods, deleteMood, loading, error };
}
