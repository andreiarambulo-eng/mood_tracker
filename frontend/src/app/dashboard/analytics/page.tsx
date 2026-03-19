"use client";

import { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { api } from "@/lib/api";
import type { MoodDistribution, ApiResponse } from "@/lib/types";
import { MOOD_COLORS, MOOD_EMOJIS } from "@/lib/types";
import { SentimentTrendChart } from "@/components/SentimentTrendChart";
import { WordCloud } from "@/components/WordCloud";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TooltipPayloadItem {
  name: string;
  value: number;
}

interface CustomPieTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
}

function CustomPieTooltip({ active, payload }: CustomPieTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0];
  return (
    <div className="rounded-lg border border-border bg-card p-3 shadow-lg text-sm">
      <p className="font-medium text-foreground">{item.name}</p>
      <p className="text-muted-foreground">{item.value} entries</p>
    </div>
  );
}

interface CenterLabelProps {
  viewBox?: { cx: number; cy: number };
  total: number;
}

function CenterLabel({ viewBox, total }: CenterLabelProps) {
  if (!viewBox) return null;
  const { cx, cy } = viewBox;
  return (
    <g>
      <text
        x={cx}
        y={cy - 8}
        textAnchor="middle"
        dominantBaseline="middle"
        className="fill-foreground"
        style={{ fontSize: 22, fontWeight: 700, fill: "#f9fafb" }}
      >
        {total}
      </text>
      <text
        x={cx}
        y={cy + 14}
        textAnchor="middle"
        dominantBaseline="middle"
        style={{ fontSize: 11, fill: "#9ca3af" }}
      >
        entries
      </text>
    </g>
  );
}

function MoodDistributionChart() {
  const [data, setData] = useState<MoodDistribution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get<ApiResponse<MoodDistribution[]>>(
          "/analytics/mood-distribution"
        );
        setData(res.data ?? []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load mood distribution");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const total = data.reduce((sum, d) => sum + d.count, 0);

  const chartData = data.map((d) => ({
    name: `${MOOD_EMOJIS[d.mood_score] ?? ""} ${d.mood_label}`,
    value: d.count,
    color: MOOD_COLORS[d.mood_score] ?? "#6b7280",
    mood_score: d.mood_score,
  }));

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <CardTitle className="text-foreground">Mood Distribution</CardTitle>
        <p className="text-sm text-muted-foreground">
          Breakdown of all your mood entries
        </p>
      </CardHeader>

      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64 text-destructive text-sm">
            {error}
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
            No mood data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
                <CenterLabel viewBox={{ cx: 0, cy: 0 }} total={total} />
              </Pie>
              <Tooltip content={<CustomPieTooltip />} />
              <Legend
                wrapperStyle={{ color: "#9ca3af", fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  return (
    <div className="w-full space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
        <p className="text-muted-foreground mt-1">
          Insights and trends from your mood tracking data.
        </p>
      </div>

      {/* Full-width sentiment trend chart */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        <SentimentTrendChart />
      </div>

      {/* Word cloud + Mood distribution side by side on large screens */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <WordCloud />
        <MoodDistributionChart />
      </div>
    </div>
  );
}
