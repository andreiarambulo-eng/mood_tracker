"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useMood } from "@/hooks/useMood";
import { api } from "@/lib/api";
import type { MoodEntry, ApiResponse, WeeklySummary } from "@/lib/types";
import { MOOD_EMOJIS, MOOD_COLORS } from "@/lib/types";
import MoodEntryForm from "@/components/MoodEntryForm";
import MoodCalendarHeatmap from "@/components/MoodCalendarHeatmap";

interface StreakData {
  current_streak: number;
  longest_streak: number;
}

const MOOD_LABELS: Record<number, string> = {
  1: "Terrible",
  2: "Bad",
  3: "Neutral",
  4: "Good",
  5: "Excellent",
};

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const { getToday } = useMood();

  const [todayMood, setTodayMood] = useState<MoodEntry | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [streak, setStreak] = useState<StreakData | null>(null);
  const [weeklyAvg, setWeeklyAvg] = useState<number | null>(null);
  const [totalEntries, setTotalEntries] = useState<number>(0);
  const [loadingData, setLoadingData] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const [streakRes, weeklyRes, moodsRes] = await Promise.allSettled([
        api.get<ApiResponse<StreakData>>("/analytics/streak"),
        api.get<ApiResponse<WeeklySummary>>("/analytics/weekly-summary"),
        api.get<ApiResponse<{ pagination: { total_count: number } }>>("/moods/get?page=1&limit=1"),
      ]);

      if (streakRes.status === "fulfilled") {
        setStreak(streakRes.value.data);
      }
      if (weeklyRes.status === "fulfilled") {
        setWeeklyAvg(weeklyRes.value.data?.average_mood ?? null);
      }
      if (moodsRes.status === "fulfilled") {
        const moodsData = moodsRes.value as { data?: { pagination?: { total_count?: number } } };
        setTotalEntries(moodsData?.data?.pagination?.total_count ?? 0);
      }
    } catch {
      // silently fail stats
    }
  }, []);

  const fetchTodayMood = useCallback(async () => {
    const res = await getToday();
    setTodayMood(res ?? null);
  }, [getToday]);

  const fetchAll = useCallback(async () => {
    setLoadingData(true);
    await Promise.allSettled([fetchTodayMood(), fetchStats()]);
    setLoadingData(false);
  }, [fetchTodayMood, fetchStats]);

  useEffect(() => {
    if (!authLoading && user) {
      fetchAll();
    }
  }, [authLoading, user, fetchAll]);

  const handleMoodSubmit = (mood: MoodEntry) => {
    setTodayMood(mood);
    setIsEditing(false);
    fetchStats();
  };

  if (authLoading || loadingData) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Good {getGreeting()}, {user?.full_name?.split(" ")[0] ?? "there"}
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Today's Mood Card */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Today&apos;s Mood
        </h2>
        {todayMood && !isEditing ? (
          <div className="glass-card glass-card-hover rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-5">
                <div
                  className="w-20 h-20 rounded-2xl flex items-center justify-center text-5xl shadow-lg"
                  style={{
                    background: `linear-gradient(135deg, ${MOOD_COLORS[todayMood.mood_score]}20, ${MOOD_COLORS[todayMood.mood_score]}08)`,
                    boxShadow: `0 0 30px ${MOOD_COLORS[todayMood.mood_score]}15`,
                  }}
                >
                  {MOOD_EMOJIS[todayMood.mood_score]}
                </div>
                <div>
                  <p
                    className="text-xl font-bold"
                    style={{ color: MOOD_COLORS[todayMood.mood_score] }}
                  >
                    {MOOD_LABELS[todayMood.mood_score]}
                  </p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Score: {todayMood.mood_score}/5
                  </p>
                  {todayMood.sentiment_label && (
                    <p className="text-xs text-muted-foreground/70 mt-0.5">
                      Sentiment: {todayMood.sentiment_label}
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 text-sm font-medium text-violet-400 border border-violet-500/20 rounded-xl hover:bg-violet-500/10 transition-all"
              >
                Edit
              </button>
            </div>
            {todayMood.remark && (
              <div className="mt-5 pt-5 border-t border-white/[0.06]">
                <p className="text-sm text-white/70 italic leading-relaxed">&ldquo;{todayMood.remark}&rdquo;</p>
              </div>
            )}
          </div>
        ) : (
          <MoodEntryForm
            onSubmit={handleMoodSubmit}
            existingMood={isEditing ? todayMood : null}
          />
        )}
        {isEditing && (
          <button
            onClick={() => setIsEditing(false)}
            className="mt-2 text-sm text-muted-foreground hover:text-foreground transition"
          >
            Cancel
          </button>
        )}
      </section>

      {/* Quick Stats */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Quick Stats
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="glass-card glass-card-hover rounded-2xl p-5">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center text-2xl">
                🔥
              </div>
              <span className="text-sm text-muted-foreground font-medium">Current Streak</span>
            </div>
            <p className="text-3xl font-bold text-foreground">
              {streak?.current_streak ?? 0}
            </p>
            <p className="text-xs text-muted-foreground/70 mt-1">days in a row</p>
          </div>

          <div className="glass-card glass-card-hover rounded-2xl p-5">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center text-2xl">
                📊
              </div>
              <span className="text-sm text-muted-foreground font-medium">This Week Avg</span>
            </div>
            <p
              className="text-3xl font-bold"
              style={{
                color:
                  weeklyAvg != null && weeklyAvg > 0
                    ? MOOD_COLORS[Math.round(weeklyAvg) as 1 | 2 | 3 | 4 | 5]
                    : "hsl(var(--muted-foreground))",
              }}
            >
              {weeklyAvg != null ? weeklyAvg.toFixed(1) : "—"}
            </p>
            <p className="text-xs text-muted-foreground/70 mt-1">mood score / 5</p>
          </div>

          <div className="glass-card glass-card-hover rounded-2xl p-5">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-2xl">
                📝
              </div>
              <span className="text-sm text-muted-foreground font-medium">Total Entries</span>
            </div>
            <p className="text-3xl font-bold text-foreground">{totalEntries}</p>
            <p className="text-xs text-muted-foreground/70 mt-1">moods logged</p>
          </div>
        </div>
      </section>

      {/* Calendar Heatmap */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Mood Calendar
        </h2>
        <MoodCalendarHeatmap />
      </section>
    </div>
  );
}

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
