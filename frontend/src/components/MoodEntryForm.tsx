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

  const TAILWIND_BG: Record<number, string> = {
    1: "bg-red-500",
    2: "bg-orange-500",
    3: "bg-yellow-500",
    4: "bg-lime-500",
    5: "bg-green-500",
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
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full">
      <h2 className="text-lg font-semibold text-white mb-1">
        {existingMood ? "Update Today's Mood" : "How are you feeling today?"}
      </h2>
      <p className="text-sm text-gray-400 mb-5">
        Select the emoji that best represents your current mood.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Emoji Picker */}
        <div className="flex justify-between gap-2">
          {([1, 2, 3, 4, 5] as const).map((score) => (
            <button
              key={score}
              type="button"
              onClick={() => setSelectedScore(score)}
              className={`
                flex flex-col items-center gap-1 flex-1 py-3 rounded-xl transition-all duration-150
                ${TAILWIND_BG[score]} bg-opacity-20 hover:bg-opacity-30
                ${selectedScore === score
                  ? `ring-2 ring-offset-2 ring-offset-gray-900 scale-105`
                  : "opacity-70 hover:opacity-90"}
              `}
              style={
                selectedScore === score
                  ? { borderColor: MOOD_COLORS[score], boxShadow: `0 0 0 3px ${MOOD_COLORS[score]}40` }
                  : undefined
              }
            >
              <span className="text-3xl">{MOOD_EMOJIS[score]}</span>
              <span className="text-xs text-gray-300 font-medium">{MOOD_LABELS[score]}</span>
            </button>
          ))}
        </div>

        {/* Selected mood label */}
        {selectedScore > 0 && (
          <p className="text-center text-sm font-medium" style={{ color: MOOD_COLORS[selectedScore] }}>
            {MOOD_EMOJIS[selectedScore]} {MOOD_LABELS[selectedScore]}
          </p>
        )}

        {/* Remark Textarea */}
        <div className="space-y-1">
          <label className="text-sm text-gray-300 font-medium" htmlFor="remark">
            Add a note <span className="text-gray-500">(optional)</span>
          </label>
          <textarea
            id="remark"
            value={remark}
            onChange={(e) => {
              if (e.target.value.length <= 500) setRemark(e.target.value);
            }}
            placeholder="What's on your mind? Any context for your mood today..."
            rows={3}
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
          />
          <div className="flex justify-end">
            <span className={`text-xs ${remark.length >= 480 ? "text-red-400" : "text-gray-500"}`}>
              {remark.length}/500
            </span>
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="text-sm text-red-400 bg-red-900/20 border border-red-800 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={selectedScore === 0 || loading}
          className="w-full py-3 rounded-xl font-semibold text-sm text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          {loading ? "Saving..." : existingMood ? "Update Mood" : "Log Mood"}
        </button>
      </form>
    </div>
  );
}
