"use client";

import { MoodHistoryTable } from "@/components/MoodHistoryTable";

export default function HistoryPage() {
  return (
    <div className="w-full space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Mood History</h1>
        <p className="text-muted-foreground mt-1">
          Browse and filter all your past mood entries.
        </p>
      </div>

      <MoodHistoryTable />
    </div>
  );
}
