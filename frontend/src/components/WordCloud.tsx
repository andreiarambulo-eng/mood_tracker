"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { WordCloudEntry, ApiResponse } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PALETTE = [
  "#3b82f6", // blue
  "#a855f7", // purple
  "#ec4899", // pink
  "#6366f1", // indigo
  "#06b6d4", // cyan
  "#14b8a6", // teal
];

function pickColor(index: number): string {
  return PALETTE[index % PALETTE.length];
}

function scaleFontSize(count: number, maxCount: number): number {
  if (maxCount === 0) return 14;
  const min = 14;
  const max = 48;
  return Math.round(min + ((count / maxCount) * (max - min)));
}

function deterministicRotation(word: string): number {
  // Produce a stable -5..5 degree rotation based on word characters
  let hash = 0;
  for (let i = 0; i < word.length; i++) {
    hash = (hash * 31 + word.charCodeAt(i)) % 1000;
  }
  return ((hash % 100) / 100) * 10 - 5;
}

export function WordCloud() {
  const [words, setWords] = useState<WordCloudEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchWords() {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get<ApiResponse<WordCloudEntry[]>>(
          "/analytics/word-cloud?days=90"
        );
        setWords(res.data ?? []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load word cloud");
      } finally {
        setLoading(false);
      }
    }
    fetchWords();
  }, []);

  const maxCount = words.reduce((m, w) => Math.max(m, w.count), 0);

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <CardTitle className="text-foreground">Word Cloud</CardTitle>
        <p className="text-sm text-muted-foreground">
          Most frequent words from your remarks (last 90 days)
        </p>
      </CardHeader>

      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-48 text-destructive text-sm">
            {error}
          </div>
        ) : words.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-muted-foreground text-sm">
            No words to display. Add some remarks to your mood entries!
          </div>
        ) : (
          <div className="flex flex-wrap justify-center gap-3 p-4 min-h-48">
            {words.map((entry, index) => {
              const fontSize = scaleFontSize(entry.count, maxCount);
              const color = pickColor(index);
              const rotation = deterministicRotation(entry.word);
              return (
                <span
                  key={entry.word}
                  title={`${entry.word}: ${entry.count} occurrence${entry.count !== 1 ? "s" : ""}`}
                  style={{
                    fontSize: `${fontSize}px`,
                    color,
                    transform: `rotate(${rotation}deg)`,
                    display: "inline-block",
                    lineHeight: 1.2,
                    cursor: "default",
                    transition: "opacity 0.15s",
                    userSelect: "none",
                  }}
                  className="hover:opacity-70 font-semibold"
                >
                  {entry.word}
                </span>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
