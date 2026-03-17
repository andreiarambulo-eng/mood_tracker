"use client";

import { useState, useEffect, useCallback } from "react";
import { useMood } from "@/hooks/useMood";
import type { MoodEntry } from "@/lib/types";
import { MOOD_EMOJIS } from "@/lib/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ITEMS_PER_PAGE = 10;

function sentimentColor(label: string): "default" | "secondary" | "destructive" | "outline" {
  switch (label?.toLowerCase()) {
    case "positive":
      return "default";
    case "neutral":
      return "secondary";
    case "negative":
      return "destructive";
    default:
      return "outline";
  }
}

function sentimentBadgeClass(label: string): string {
  switch (label?.toLowerCase()) {
    case "positive":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "neutral":
      return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    case "negative":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-muted text-muted-foreground";
  }
}

function truncate(text: string | null, maxLen: number): string {
  if (!text) return "—";
  return text.length > maxLen ? text.slice(0, maxLen) + "…" : text;
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function MoodHistoryTable() {
  const { getMoods, loading } = useMood();
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [filterStart, setFilterStart] = useState("");
  const [filterEnd, setFilterEnd] = useState("");

  const fetchMoods = useCallback(
    async (p: number, start: string, end: string) => {
      try {
        const result = await getMoods(p, ITEMS_PER_PAGE, start || undefined, end || undefined);
        if (result) {
          setEntries(result.data);
          setTotalPages(result.pagination.total_pages);
          setTotalCount(result.pagination.total_count);
        }
      } catch {
        // error handled by hook
      }
    },
    [getMoods]
  );

  useEffect(() => {
    fetchMoods(page, filterStart, filterEnd);
  }, [page, filterStart, filterEnd, fetchMoods]);

  function applyFilter() {
    setPage(1);
    setFilterStart(startDate);
    setFilterEnd(endDate);
  }

  function clearFilter() {
    setStartDate("");
    setEndDate("");
    setPage(1);
    setFilterStart("");
    setFilterEnd("");
  }

  const pageNumbers: number[] = [];
  const startPage = Math.max(1, page - 2);
  const endPage = Math.min(totalPages, page + 2);
  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Mood History</CardTitle>

        {/* Date range filter */}
        <div className="flex flex-wrap items-end gap-3 pt-2">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground">From</label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-40 bg-background border-border text-foreground"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground">To</label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-40 bg-background border-border text-foreground"
            />
          </div>
          <Button onClick={applyFilter} variant="default" size="sm">
            Apply
          </Button>
          {(filterStart || filterEnd) && (
            <Button onClick={clearFilter} variant="outline" size="sm">
              Clear
            </Button>
          )}
          {totalCount > 0 && (
            <span className="text-sm text-muted-foreground ml-auto">
              {totalCount} {totalCount === 1 ? "entry" : "entries"}
            </span>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {loading && entries.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
          </div>
        ) : entries.length === 0 ? (
          <div className="py-12 text-center text-muted-foreground">
            No mood entries found.
          </div>
        ) : (
          <>
            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left">
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Date</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Mood</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Remark</th>
                    <th className="pb-3 font-medium text-muted-foreground">Sentiment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {entries.map((entry) => (
                    <tr key={entry._id} className="hover:bg-muted/30 transition-colors">
                      <td className="py-3 pr-4 text-foreground whitespace-nowrap">
                        {formatDate(entry.logged_date)}
                      </td>
                      <td className="py-3 pr-4">
                        <span className="flex items-center gap-2">
                          <span className="text-lg">
                            {MOOD_EMOJIS[entry.mood_score] ?? "❓"}
                          </span>
                          <span className="text-foreground capitalize">
                            {entry.mood_label}
                          </span>
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-muted-foreground max-w-xs">
                        {truncate(entry.remark, 60)}
                      </td>
                      <td className="py-3">
                        <span
                          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${sentimentBadgeClass(
                            entry.sentiment_label
                          )}`}
                        >
                          {entry.sentiment_label}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-1 mt-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1 || loading}
                >
                  Prev
                </Button>

                {startPage > 1 && (
                  <>
                    <Button
                      variant={page === 1 ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPage(1)}
                      disabled={loading}
                    >
                      1
                    </Button>
                    {startPage > 2 && (
                      <span className="px-2 text-muted-foreground">…</span>
                    )}
                  </>
                )}

                {pageNumbers.map((n) => (
                  <Button
                    key={n}
                    variant={n === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setPage(n)}
                    disabled={loading}
                  >
                    {n}
                  </Button>
                ))}

                {endPage < totalPages && (
                  <>
                    {endPage < totalPages - 1 && (
                      <span className="px-2 text-muted-foreground">…</span>
                    )}
                    <Button
                      variant={page === totalPages ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPage(totalPages)}
                      disabled={loading}
                    >
                      {totalPages}
                    </Button>
                  </>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages || loading}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
