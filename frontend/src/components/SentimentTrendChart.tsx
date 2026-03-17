"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import { api } from "@/lib/api";
import type { SentimentTrendEntry, ApiResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DAY_OPTIONS = [7, 14, 30, 60, 90];

interface TooltipPayloadItem {
  color: string;
  name: string;
  value: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-lg border border-border bg-card p-3 shadow-lg text-sm">
      <p className="font-medium text-foreground mb-1">{label}</p>
      {payload.map((item) => (
        <p key={item.name} style={{ color: item.color }}>
          {item.name}: {typeof item.value === "number" ? item.value.toFixed(3) : item.value}
        </p>
      ))}
    </div>
  );
}

export function SentimentTrendChart() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<SentimentTrendEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get<ApiResponse<SentimentTrendEntry[]>>(
          `/analytics/sentiment-trend?days=${days}`
        );
        setData(res.data ?? []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load trend data");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [days]);

  const chartData = data.map((entry) => ({
    date: new Date(entry.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    sentiment_score: entry.sentiment_score,
    mood_score: entry.mood_score,
  }));

  return (
    <Card className="bg-card border-border col-span-2">
      <CardHeader>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <CardTitle className="text-foreground">Sentiment Trend</CardTitle>
            <p className="text-sm text-muted-foreground mt-0.5">
              Sentiment score vs mood score over time
            </p>
          </div>
          <div className="flex gap-1">
            {DAY_OPTIONS.map((d) => (
              <Button
                key={d}
                size="sm"
                variant={days === d ? "default" : "outline"}
                onClick={() => setDays(d)}
              >
                {d}d
              </Button>
            ))}
          </div>
        </div>
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
            No data available for the selected period.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 40, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                tickLine={false}
                axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              />
              {/* Left axis: sentiment -1 to 1 */}
              <YAxis
                yAxisId="sentiment"
                domain={[-1, 1]}
                tickCount={5}
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                tickLine={false}
                axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                tickFormatter={(v: number) => v.toFixed(1)}
                label={{
                  value: "Sentiment",
                  angle: -90,
                  position: "insideLeft",
                  fill: "#9ca3af",
                  fontSize: 11,
                  dx: 10,
                }}
              />
              {/* Right axis: mood 1 to 5 */}
              <YAxis
                yAxisId="mood"
                orientation="right"
                domain={[1, 5]}
                tickCount={5}
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                tickLine={false}
                axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                tickFormatter={(v: number) => v.toFixed(0)}
                label={{
                  value: "Mood",
                  angle: 90,
                  position: "insideRight",
                  fill: "#9ca3af",
                  fontSize: 11,
                  dx: -5,
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ color: "#9ca3af", fontSize: 12 }}
              />
              <Line
                yAxisId="sentiment"
                type="monotone"
                dataKey="sentiment_score"
                name="Sentiment Score"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Line
                yAxisId="mood"
                type="monotone"
                dataKey="mood_score"
                name="Mood Score"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
