"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { HeatmapEntry, ApiResponse } from "@/lib/types";
import { MOOD_COLORS } from "@/lib/types";

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DOW_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""];

const MOOD_LABELS: Record<number, string> = {
  1: "Terrible",
  2: "Bad",
  3: "Neutral",
  4: "Good",
  5: "Excellent",
};

const SQUARE_COLOR: Record<number, string> = {
  0: "bg-white/[0.04]",
  1: "bg-red-500",
  2: "bg-orange-500",
  3: "bg-yellow-500",
  4: "bg-lime-500",
  5: "bg-green-500",
};

interface TooltipState {
  x: number;
  y: number;
  date: string;
  score: number;
  label: string;
}

function getDaysInYear(year: number): Date[] {
  const days: Date[] = [];
  const start = new Date(year, 0, 1);
  const end = new Date(year, 11, 31);
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    days.push(new Date(d));
  }
  return days;
}

function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export default function MoodCalendarHeatmap() {
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [heatmapMap, setHeatmapMap] = useState<Record<string, HeatmapEntry>>({});
  const [loading, setLoading] = useState(false);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const fetchHeatmap = useCallback(async (y: number) => {
    setLoading(true);
    try {
      const res = await api.get<ApiResponse<HeatmapEntry[]>>(`/analytics/heatmap?year=${y}`);
      const map: Record<string, HeatmapEntry> = {};
      for (const entry of res.data) {
        map[entry.date] = entry;
      }
      setHeatmapMap(map);
    } catch {
      setHeatmapMap({});
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHeatmap(year);
  }, [year, fetchHeatmap]);

  const allDays = getDaysInYear(year);
  const firstDow = (new Date(year, 0, 1).getDay() + 6) % 7;

  type Cell = Date | null;
  const cells: Cell[] = Array(firstDow).fill(null).concat(allDays);
  while (cells.length % 7 !== 0) cells.push(null);

  const numWeeks = cells.length / 7;

  const monthColStart: Record<number, number> = {};
  for (let col = 0; col < numWeeks; col++) {
    for (let row = 0; row < 7; row++) {
      const cell = cells[col * 7 + row];
      if (cell) {
        const m = cell.getMonth();
        if (!(m in monthColStart)) {
          monthColStart[m] = col;
        }
      }
    }
  }

  const handleMouseMove = (e: React.MouseEvent, day: Date) => {
    const dateStr = toISODate(day);
    const entry = heatmapMap[dateStr];
    // Keep tooltip within viewport
    const tooltipW = 140;
    const tooltipH = 70;
    let x = e.clientX + 14;
    let y = e.clientY + 14;
    if (x + tooltipW > window.innerWidth) x = e.clientX - tooltipW - 8;
    if (y + tooltipH > window.innerHeight) y = e.clientY - tooltipH - 8;
    setTooltip({
      x,
      y,
      date: dateStr,
      score: entry?.mood_score ?? 0,
      label: entry?.mood_label ?? "No entry",
    });
  };

  const handleMouseLeave = () => setTooltip(null);

  return (
    <div className="glass-card rounded-2xl p-4 sm:p-6 w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Mood History</h2>
          <p className="text-sm text-muted-foreground">Your mood over {year}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setYear((y) => y - 1)}
            className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/[0.05] transition"
            aria-label="Previous year"
          >
            &#8249;
          </button>
          <span className="text-foreground font-semibold text-sm w-12 text-center">{year}</span>
          <button
            onClick={() => setYear((y) => y + 1)}
            disabled={year >= new Date().getFullYear()}
            className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/[0.05] disabled:opacity-30 disabled:cursor-not-allowed transition"
            aria-label="Next year"
          >
            &#8250;
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
          Loading heatmap...
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div className="flex gap-1 min-w-max">
            {/* Day-of-week labels */}
            <div className="flex flex-col gap-0.5 mr-1 pt-5">
              {DOW_LABELS.map((label, i) => (
                <div key={i} className="h-3 w-7 text-right text-[10px] text-muted-foreground/60 leading-3">
                  {label}
                </div>
              ))}
            </div>

            {/* Grid columns */}
            <div className="flex flex-col">
              {/* Month labels row */}
              <div className="flex gap-0.5 mb-1">
                {Array.from({ length: numWeeks }, (_, col) => (
                  <div key={col} className="w-3 text-[10px] text-muted-foreground/60 truncate">
                    {MONTH_LABELS[
                      Object.entries(monthColStart).find(([, v]) => v === col)?.[0] as unknown as number
                    ] ?? ""}
                  </div>
                ))}
              </div>

              {/* Week columns */}
              <div className="flex gap-0.5">
                {Array.from({ length: numWeeks }, (_, col) => (
                  <div key={col} className="flex flex-col gap-0.5">
                    {Array.from({ length: 7 }, (_, row) => {
                      const cell = cells[col * 7 + row];
                      if (!cell) {
                        return <div key={row} className="w-3 h-3" />;
                      }
                      const dateStr = toISODate(cell);
                      const entry = heatmapMap[dateStr];
                      const score = entry?.mood_score ?? 0;
                      return (
                        <div
                          key={row}
                          onMouseMove={(e) => handleMouseMove(e, cell)}
                          onMouseLeave={handleMouseLeave}
                          className={`w-3 h-3 rounded-sm cursor-pointer transition-opacity hover:opacity-80 ${SQUARE_COLOR[score]}`}
                          aria-label={`${dateStr}: ${entry?.mood_label ?? "No entry"}`}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-2 mt-4">
        <span className="text-[10px] text-muted-foreground/50">Less</span>
        {([0, 1, 2, 3, 4, 5] as const).map((score) => (
          <div
            key={score}
            className={`w-3 h-3 rounded-sm ${SQUARE_COLOR[score]}`}
            title={score === 0 ? "No entry" : MOOD_LABELS[score]}
          />
        ))}
        <span className="text-[10px] text-muted-foreground/50">More</span>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 pointer-events-none glass-card rounded-lg px-3 py-2 text-xs"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <p className="text-white/70 font-medium">{tooltip.date}</p>
          {tooltip.score > 0 ? (
            <>
              <p style={{ color: MOOD_COLORS[tooltip.score] }} className="font-semibold">
                {tooltip.label}
              </p>
              <p className="text-muted-foreground">Score: {tooltip.score}/5</p>
            </>
          ) : (
            <p className="text-muted-foreground/60">No mood logged</p>
          )}
        </div>
      )}
    </div>
  );
}
