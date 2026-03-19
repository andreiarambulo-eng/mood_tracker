"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { WeeklySummary } from "@/lib/types";
import { MOOD_EMOJIS, MOOD_COLORS } from "@/lib/types";

interface WeeklySummaryCardProps {
  summary: WeeklySummary;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDayName(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function getSentimentLabel(score: number | null): string {
  if (score === null) return "—";
  if (score >= 0.5) return "Very Positive";
  if (score >= 0.1) return "Positive";
  if (score > -0.1) return "Neutral";
  if (score > -0.5) return "Negative";
  return "Very Negative";
}

function getSentimentColor(score: number | null): string {
  if (score === null) return "bg-muted text-muted-foreground";
  if (score >= 0.5) return "bg-green-500/20 text-green-400";
  if (score >= 0.1) return "bg-lime-500/20 text-lime-400";
  if (score > -0.1) return "bg-yellow-500/20 text-yellow-400";
  if (score > -0.5) return "bg-orange-500/20 text-orange-400";
  return "bg-red-500/20 text-red-400";
}

export function WeeklySummaryCard({ summary }: WeeklySummaryCardProps) {
  const {
    week_start,
    week_end,
    total_entries,
    average_mood,
    average_sentiment,
    most_common_mood,
    days,
  } = summary;

  const avgMoodScore = average_mood !== null ? Math.round(average_mood) : null;
  const avgMoodEmoji =
    avgMoodScore !== null ? (MOOD_EMOJIS[avgMoodScore] ?? "—") : "—";

  return (
    <Card className="glass-card border-0 w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <CardTitle className="text-foreground text-lg">
            {formatDate(week_start)} — {formatDate(week_end)}
          </CardTitle>
          <Badge variant="outline" className="text-muted-foreground border-border">
            Week {summary.week}, {summary.year}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {total_entries === 0 ? (
          <div className="flex items-center justify-center py-10 text-muted-foreground text-sm">
            No entries this week.
          </div>
        ) : (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="rounded-lg bg-muted/30 px-4 py-3 flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                  Avg Mood
                </span>
                <span className="text-xl font-bold text-foreground">
                  {avgMoodEmoji}{" "}
                  {average_mood !== null ? average_mood.toFixed(1) : "—"}
                </span>
              </div>

              <div className="rounded-lg bg-muted/30 px-4 py-3 flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                  Avg Sentiment
                </span>
                <span
                  className={`text-sm font-semibold px-2 py-0.5 rounded w-fit ${getSentimentColor(
                    average_sentiment
                  )}`}
                >
                  {average_sentiment !== null
                    ? getSentimentLabel(average_sentiment)
                    : "—"}
                </span>
                {average_sentiment !== null && (
                  <span className="text-xs text-muted-foreground">
                    {average_sentiment.toFixed(2)}
                  </span>
                )}
              </div>

              <div className="rounded-lg bg-muted/30 px-4 py-3 flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                  Total Entries
                </span>
                <span className="text-xl font-bold text-foreground">
                  {total_entries}
                </span>
              </div>

              <div className="rounded-lg bg-muted/30 px-4 py-3 flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">
                  Most Common
                </span>
                <span className="text-sm font-semibold text-foreground">
                  {most_common_mood ?? "—"}
                </span>
              </div>
            </div>

            {/* Day-by-day breakdown */}
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Daily Breakdown
              </h3>

              {days.length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">
                  No daily data available.
                </p>
              ) : (
                <div className="space-y-2">
                  {days.map((day) => {
                    const barColor =
                      MOOD_COLORS[day.mood_score] ?? "#6b7280";
                    const barWidth = `${(day.mood_score / 5) * 100}%`;
                    const emoji = MOOD_EMOJIS[day.mood_score] ?? "";

                    return (
                      <div
                        key={day.date}
                        className="flex items-center gap-3 rounded-md bg-muted/20 px-3 py-2"
                      >
                        {/* Day label */}
                        <span className="w-28 shrink-0 text-sm text-muted-foreground">
                          {formatDayName(day.date)}
                        </span>

                        {/* Mood bar */}
                        <div className="flex-1 h-3 rounded-full bg-muted/40 overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300"
                            style={{
                              width: barWidth,
                              backgroundColor: barColor,
                            }}
                          />
                        </div>

                        {/* Emoji + score */}
                        <span className="w-14 shrink-0 text-center text-sm font-medium text-foreground">
                          {emoji} {day.mood_score}/5
                        </span>

                        {/* Remark preview */}
                        {day.remark_preview && (
                          <span className="hidden md:block max-w-xs text-xs text-muted-foreground truncate">
                            {day.remark_preview}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
