"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { WeeklySummary, ApiResponse } from "@/lib/types";
import { WeeklySummaryCard } from "@/components/WeeklySummaryCard";

function getISOWeekAndYear(date: Date): { week: number; year: number } {
  // Copy date to avoid mutation
  const d = new Date(date.getTime());
  // Set to nearest Thursday: current date + 4 - current day number (Monday=1)
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + 4 - (d.getDay() || 7));
  const yearStart = new Date(d.getFullYear(), 0, 1);
  const week = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return { week, year: d.getFullYear() };
}

function getWeeksInYear(year: number): number {
  // A year has 53 ISO weeks if Jan 1 or Dec 31 is Thursday
  const jan1 = new Date(year, 0, 1).getDay();
  const dec31 = new Date(year, 11, 31).getDay();
  return jan1 === 4 || dec31 === 4 ? 53 : 52;
}

export default function ReportsPage() {
  const now = new Date();
  const { week: currentWeek, year: currentYear } = getISOWeekAndYear(now);

  const [week, setWeek] = useState(currentWeek);
  const [year, setYear] = useState(currentYear);
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ApiResponse<WeeklySummary>>(
        `/analytics/weekly-summary/${year}/${week}`
      );
      setSummary(res.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load weekly summary");
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, [year, week]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  function goToPrevWeek() {
    if (week === 1) {
      const prevYear = year - 1;
      setYear(prevYear);
      setWeek(getWeeksInYear(prevYear));
    } else {
      setWeek((w) => w - 1);
    }
  }

  function goToNextWeek() {
    const maxWeeks = getWeeksInYear(year);
    if (week === maxWeeks) {
      setYear((y) => y + 1);
      setWeek(1);
    } else {
      setWeek((w) => w + 1);
    }
  }

  const isCurrentWeek = week === currentWeek && year === currentYear;

  return (
    <div className="w-full space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Weekly Report</h1>
        <p className="text-muted-foreground mt-1">
          Review your mood and sentiment trends week by week.
        </p>
      </div>

      {/* Week navigation */}
      <div className="flex items-center gap-4">
        <button
          onClick={goToPrevWeek}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-foreground hover:bg-muted/50 transition-colors"
          aria-label="Previous week"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-foreground min-w-[120px] text-center">
            Week {week}, {year}
          </span>
          {isCurrentWeek && (
            <span className="text-xs rounded-full bg-blue-500/20 text-blue-400 px-2 py-0.5 font-medium">
              This week
            </span>
          )}
        </div>

        <button
          onClick={goToNextWeek}
          disabled={isCurrentWeek}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-foreground hover:bg-muted/50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Next week"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
            <p className="text-sm text-muted-foreground">Loading summary…</p>
          </div>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-5 py-4 text-sm text-destructive">
          {error}
        </div>
      ) : summary ? (
        <WeeklySummaryCard summary={summary} />
      ) : null}
    </div>
  );
}
