"use client";

import { useState } from "react";
import { useMood } from "@/hooks/useMood";
import type { MoodEntry } from "@/lib/types";
import { MOOD_EMOJIS, MOOD_COLORS } from "@/lib/types";

interface MoodEntryFormProps {
  onSubmit: (mood: MoodEntry) => void;
  existingMood?: MoodEntry | null;
}

export default function MoodEntryForm({ onSubmit, existingMood }: MoodEntryFormProps) {
  const { createMood, updateMood, loading, error } = useMood();
  const [selectedScore, setSelectedScore] = useState<number>(
    existingMood?.mood_score ?? 0
  );
  const [remark, setRemark] = useState<string>(existingMood?.remark ?? "");

  const MOOD_LABELS: Record<number, string> = {
    1: "Terrible",
    2: "Bad",
    3: "Neutral",
    4: "Good",
    5: "Excellent",
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedScore === 0) return;

    try {
      let result: MoodEntry;
      if (existingMood) {
        const res = await updateMood(existingMood._id, selectedScore, remark || undefined);
        result = res!;
      } else {
        const res = await createMood(selectedScore, remark || undefined);
        result = res!;
      }
      onSubmit(result);
    } catch {
      // error handled by hook
    }
  };

  return (
    <div className="glass-card rounded-2xl p-4 sm:p-6 w-full">
      <h2 className="text-lg font-semibold text-foreground mb-1">
        {existingMood ? "Update Today's Mood" : "How are you feeling today?"}
      </h2>
      <p className="text-sm text-muted-foreground mb-6">
        Select the emoji that best represents your current mood.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Emoji Picker */}
        <div className="flex justify-between gap-2 sm:gap-3">
          {([1, 2, 3, 4, 5] as const).map((score) => (
            <button
              key={score}
              type="button"
              onClick={() => setSelectedScore(score)}
              className={`
                flex flex-col items-center gap-1.5 sm:gap-2 flex-1 py-3 sm:py-4 rounded-xl sm:rounded-2xl transition-all duration-200
                ${selectedScore === score
                  ? "scale-105"
                  : "opacity-60 hover:opacity-90"}
              `}
              style={{
                background: selectedScore === score
                  ? `linear-gradient(135deg, ${MOOD_COLORS[score]}25, ${MOOD_COLORS[score]}08)`
                  : "rgba(255,255,255,0.03)",
                border: selectedScore === score
                  ? `2px solid ${MOOD_COLORS[score]}40`
                  : "2px solid transparent",
                boxShadow: selectedScore === score
                  ? `0 0 24px ${MOOD_COLORS[score]}15, 0 4px 12px rgba(0,0,0,0.2)`
                  : "none",
              }}
            >
              <span className="text-2xl sm:text-4xl drop-shadow-lg">{MOOD_EMOJIS[score]}</span>
              <span className="text-[10px] sm:text-[11px] text-white/60 font-medium">{MOOD_LABELS[score]}</span>
            </button>
          ))}
        </div>

        {/* Selected mood label */}
        {selectedScore > 0 && (
          <p className="text-center text-sm font-semibold" style={{ color: MOOD_COLORS[selectedScore] }}>
            {MOOD_EMOJIS[selectedScore]} {MOOD_LABELS[selectedScore]}
          </p>
        )}

        {/* Remark Textarea */}
        <div className="space-y-2">
          <label className="text-sm text-muted-foreground font-medium" htmlFor="remark">
            Add a note <span className="text-muted-foreground/50">(optional)</span>
          </label>
          <textarea
            id="remark"
            value={remark}
            onChange={(e) => {
              if (e.target.value.length <= 500) setRemark(e.target.value);
            }}
            placeholder="What's on your mind? Any context for your mood today..."
            rows={3}
            className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-foreground placeholder-white/20 resize-none focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/30 transition"
          />
          <div className="flex justify-end">
            <span className={`text-xs ${remark.length >= 480 ? "text-red-400" : "text-muted-foreground/50"}`}>
              {remark.length}/500
            </span>
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
            {error}
          </p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={selectedScore === 0 || loading}
          className="w-full py-3 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-lg shadow-violet-500/15"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Saving...
            </span>
          ) : existingMood ? "Update Mood" : "Log Mood"}
        </button>
      </form>
    </div>
  );
}
